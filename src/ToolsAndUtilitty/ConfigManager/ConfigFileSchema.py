import json
import pathlib
import random
import typing
import os


class ConfigEntrySchema:
    def __init__(self, validator: typing.Callable[[any], bool] = lambda _: True,
                 initializer: typing.Callable[[], any] = lambda _: None):
        self._validator: typing.Callable[[any], bool] = validator
        self._initializer: typing.Callable[[], any] = initializer

    def validate_value(self, value) -> bool:
        return self._validator(value)

    def generate_default(self):
        return self._initializer()


class ConfigFileSchema:

    def __init__(self):
        self._content: dict[str, ConfigEntrySchema] = {}

    def add_schema(self, key: str, entry: ConfigEntrySchema):
        self._content[key] = entry

    def get_content(self) -> dict[str, ConfigEntrySchema]:
        return self._content

    def validate_json(self, js: dict) -> tuple[bool, str | None]:
        failures = [f"Value {js.get(k)} is invalid '{k}' value" for k, schema in self._content.items()
                    if schema.validate_value(js.get(k))]

        return len(failures) == 0, "\n".join(failures)

    def generate_from_schema(self) -> dict:
        return {
            k: schema.generate_default()
            for k, schema in self._content.items()
        }


def bind_validators(validators: typing.Iterable[typing.Callable[[any], bool]]) -> typing.Callable[[any], bool]:
    def bound_validator(something):
        for v in validators:
            if not v(something):
                return False
        return True

    return bound_validator


def entry_schema(initializer: any,
                 *validators: typing.Callable[[any], bool]) -> ConfigEntrySchema:
    generator = initializer if callable(initializer) else lambda: initializer
    return ConfigEntrySchema(bind_validators(validators), generator)


class ConfigFile:
    def __init__(self, path: os.PathLike, schema: ConfigFileSchema):
        self._schema: ConfigFileSchema = schema
        self._path: os.PathLike = path
        self._parsed_json: dict = {}

    def check_if_exists(self) -> bool:
        return os.path.isfile(self._path)

    def try_delete(self) -> bool:
        if res := self.check_if_exists():
            os.remove(self._path)
        return res

    def save(self):
        with open(self._path, "w") as f:
            f.write(json.dumps(self._parsed_json))

    def load(self):
        with open(self._path, "r") as f:
            content = f.read()
        self._parsed_json = json.loads(content)

    def validate(self) -> tuple[bool, str | None]:
        return self._schema.validate_json(self._parsed_json)

    def get_content(self):
        return self._parsed_json

    def set_content(self, content: dict):
        self._parsed_json = content

    def export_content_as_string(self):
        return json.dumps(self._parsed_json)

    def generate(self):
        self.try_delete()
        self._parsed_json = self._schema.generate_from_schema()
        self.save()


if __name__ == "__main__":
    schema = ConfigFileSchema()
    schema.add_schema("test", entry_schema(lambda: "".join([random.choice("123") for _ in range(12)])))
    schema.add_schema("john", entry_schema("doe"))
    file = ConfigFile(pathlib.Path("example_config.json"), schema)
    file.generate()