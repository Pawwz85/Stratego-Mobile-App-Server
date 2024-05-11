from src.Core.ResourceManager import *


class MainLoopStub:
    def __init__(self):
        self.__resource_manager = ResourceManager()

    def run(self, time_limit):
        self.__resource_manager.add_delayed_task(DelayedTask(lambda: self.kill(), time_limit))
        while len(self.__resource_manager) > 0:
            self.__resource_manager.iteration_of_job_execution()

    def get_resource_manager(self):
        return self.__resource_manager

    def kill(self):
        print(f"Killing all {len(self.__resource_manager)} proces running...")
        self.__resource_manager.kill()
        print("Done")
