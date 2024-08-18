from src.Core.JobManager import *


class MainLoopStub:
    def __init__(self):
        self.__job_manager = JobManager()

    def run(self, time_limit):
        self.__job_manager.add_delayed_task(DelayedTask(lambda: self.kill(), time_limit))
        while len(self.__job_manager) > 0:
            self.__job_manager.iteration_of_job_execution()

    def get_resource_manager(self):
        return self.__job_manager

    def kill(self):
        print(f"Killing all {len(self.__job_manager)} proces running...")
        self.__job_manager.kill()
        print("Done")
