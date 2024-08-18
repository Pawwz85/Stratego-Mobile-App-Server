"""
    In order to simplify debugging, troubleshooting and testing, I have created simple
    simulation language. It has no name, and it is very simplistic, here is an example:

    #Comment
    $TableAPI #Header
    user1 take_seat > {"side":"red"} # interaction
    WAIT 20
    user2 take_seat > {"side":"blue"}
    AUTOWAIT TRUE 50
    user1 set_readiness > {"value":true}

    $TableAPI - This line is a header. It informs the interpreter which API we are testing
    user1 take_seat > {"side":"red"} - This line is an interaction. It would cause call to TableAPI.take_seat()
    WAIT 20 - wait 20 ms before executing next line
    AUTOWAIT TRUE 50 - Automatically insert WAIT 50 after each next interaction
    AUTOWAIT FALSE - turns off auto wait

    Character # indicates that all text after it is comment
    Character > is payload operator. It means that text right to it is a json data

    Given code written in this language is then interpreted into list of DelayedTasks with could be
    then executed inside of resource manager.

    Important: Interpreter will replace all whitespaces in json with space
"""
import json
from enum import Enum
from pyclbr import Class, readmodule_ex
from collections import deque
from src.Core.User import User
from src.Core.JobManager import JobManager, DelayedTask
from src.Events.Events import Eventmanager, IEventReceiver


class ConsoleEventReceiver(IEventReceiver):
    def __init__(self, username: str, event_manager: Eventmanager):
        super().__init__(lambda: None)
        self.event_manager = event_manager
        self.username = username

    def receive(self, message: str):
        print(f"{self.username} received event: {message}")
        event_body = json.loads(message)
        event_id = event_body["event_id"]
        self.event_manager.confirm_delivery(event_id)


class _UserSimulationLanguageToken(Enum):
    COMMENT = 1,
    HEADER = 2,
    WAIT = 3,
    TRUE = 4,
    FALSE = 5,
    AUTOWAIT = 6,
    INTEGER = 7,
    LABEL = 8,
    JSON = 9


class UserSimulationInterpreter:
    _keywords = {"WAIT": _UserSimulationLanguageToken.WAIT,
                 "AUTOWAIT": _UserSimulationLanguageToken.AUTOWAIT,
                 "TRUE": _UserSimulationLanguageToken.TRUE,
                 "FALSE": _UserSimulationLanguageToken.FALSE
                 }
    _headers: dict[str, Class] = dict()

    def __init__(self, instances: dict[str, any], job_manager: JobManager, event_manager):
        self._api: None | Class = None
        self._auto_wait = False
        self._auto_wait_interval = 20
        self._user_pool: dict[str, User] = dict()
        self._instances: dict[Class, any] = {UserSimulationInterpreter._headers[k]: v for k, v in instances.items()}
        self._job_manager = job_manager
        self.event_manager = event_manager
        self.now = 0
        self.lines_seen = deque()

    def _lex_word(self, word: str) -> _UserSimulationLanguageToken:
        if word in UserSimulationInterpreter._keywords.keys():
            return UserSimulationInterpreter._keywords[word]

        if word.startswith("$"):
            return _UserSimulationLanguageToken.HEADER

        if word.startswith("{") and word.endswith("}"):
            return _UserSimulationLanguageToken.JSON

        if word.isdecimal():
            return _UserSimulationLanguageToken.INTEGER

        return _UserSimulationLanguageToken.LABEL

    def _resolve_user(self, login: str) -> User:
        if login not in self._user_pool.keys():
            user = User(login, "12345", len(self._user_pool), self.event_manager)
            user.session.endpoints.add(ConsoleEventReceiver(user.username, self.event_manager))
            self._user_pool[login] = user
        return self._user_pool[login]

    def __interpret(self, line):
        self.lines_seen.append(line + "\n")
        line = line.split(">", 1)
        line, json_part = (line[0], line[1]) if len(line) == 2 else (line[0], "{}")

        line = line.split("#", 1)
        line, json_part = (line[0], "{}") if len(line) == 2 else (line[0], json_part)

        words = line.split()
        tokens = [self._lex_word(w) for w in words]

        if len(tokens) == 2 and tokens[0] is _UserSimulationLanguageToken.WAIT \
                and tokens[1] is _UserSimulationLanguageToken.INTEGER:
            self.now += int(words[1])
            return
        elif len(tokens) > 1 and tokens[0] is _UserSimulationLanguageToken.AUTOWAIT:
            if len(tokens) > 2 and tokens[1] is _UserSimulationLanguageToken.TRUE\
                    and tokens[2] is _UserSimulationLanguageToken.INTEGER:
                self._auto_wait = True
                self._auto_wait_interval = int(words[2])
            elif tokens[1] is _UserSimulationLanguageToken.FALSE:
                self._auto_wait = False
            else:
                raise Exception("Expected keyword FALSE or TRUE [INTEGER] after WAIT.")

            return
        elif len(tokens) > 0 and tokens[0] is _UserSimulationLanguageToken.HEADER:
            self._api = UserSimulationInterpreter._headers.get(words[0])
            if self._api is None:
                raise Exception(f"Unknown header {words[0]}")

        elif len(tokens) > 1 and tokens[0] is _UserSimulationLanguageToken.LABEL\
                and tokens[1] is _UserSimulationLanguageToken.LABEL:

            if self._api is None:
                raise Exception("Header is not set. Please add correct $header to the beginning of the script.")

            user = self._resolve_user(words[0])
            req = json.loads(json_part)

            api_object = self._instances[self._api]
            def_line = self._get_method_def_line(words[1])
            code = f"result = api_object.{words[1]}"

            # Todo: Consider implementing more sophisticated check
            user_as_param = "user" in def_line
            req_as_param = "request" in def_line

            if user_as_param and req_as_param:
                code += "(user=USER, request=REQ)"
            elif user_as_param:
                code += "(user=USER)"
            elif req_as_param:
                code += "(request=REQ)"
            else:
                code += "()"

            code += "\nif type(result) is tuple and not result[0]:"
            code += f"\n\tprint('{user.username}: ', result)"

            task_lambda = lambda: exec(code, None, {"api_object": api_object, "USER": user, "REQ": req})
            self._job_manager.add_delayed_task(DelayedTask(task_lambda, self.now))

            if self._auto_wait:
                self.now += self._auto_wait_interval

    def _get_method_def_line(self, method_name: str):
        module = self._api.module
        file = self._api.file
        line_nr = self._api.methods[method_name]
        result = ""
        with open(file) as fp:
            for i, line in enumerate(fp):
                if i + 1 == line_nr:
                    result = line
                    break
        return result

    def run_script(self, path, convert_to: str | None = None, method_mapping: dict[str, str] | None = None):
        with open(path) as file:
            if convert_to is None:
                for line in file:
                    self.__interpret(line)
            else:
                method_mapping = method_mapping if method_mapping is not None else dict()
                result = "".join([line + "\n" for line in file])
                self.run_command(convert_script(result, convert_to, method_mapping))

    def run_command(self, cmd: str):
        for line in cmd.split("\n"):
            self.__interpret(line)

    @staticmethod
    def add_header(header: str, module_name: str, class_name: str):
        module = readmodule_ex(module_name)
        UserSimulationInterpreter._headers[header] = module[class_name]

    def dump(self, file_name: str):
        with open(file_name, mode="w") as file:
            for line in self.lines_seen:
                file.write(line)

    def forgot_lines(self):
        self.lines_seen.clear()

    def get_user_by_name(self, name: str):
        user = self._user_pool[name]
        if user is None:
            raise Exception(f"User {name} is no defined")
        return user


def convert_script(script: str, new_header: str, methods_dict):
    lines = script.split("\n")
    result = ""
    for line in lines:
        line = line.split("#")[0]
        if line.count("$") > 0 and line.split()[0].startswith("$"):
            result += f"\n{new_header}"
            continue
        elif line.count(">") > 0:
            parts = line.split(">", 1)
            labels = parts[0].split(maxsplit=2)
            labels[1] = methods_dict[labels[1]]
            result += f"\n{labels[0]} {labels[1]} {labels[2] if len(labels) == 3 else ""} > {parts[1]}"
        else:
            result += f"\n{line}"

    return result


UserSimulationInterpreter.add_header("$TableApi", "src.Core.table", "TableApi")
UserSimulationInterpreter.add_header("$RoomApi", "src.Core.Room", "RoomApi")
UserSimulationInterpreter.add_header("$ChatApi", "src.Core.chat", "ChatApi")
