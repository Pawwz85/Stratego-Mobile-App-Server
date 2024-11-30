import time
from abc import ABC, abstractmethod
import os


class ILocalMessageBrokerBoot(ABC):

    @abstractmethod
    def boot(self):
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def shutdown(self):
        pass


def boot_local_message_broker(boot: ILocalMessageBrokerBoot, threshold=10, wait=0.1):
    is_running = boot.is_available()
    check_counter = 0

    if not is_running:
        boot.boot()
        time.sleep(wait)
        while check_counter < threshold:
            if boot.is_available():
                return
            check_counter = check_counter + 1
            time.sleep(wait)

        if check_counter >= threshold:
            raise ConnectionError()
