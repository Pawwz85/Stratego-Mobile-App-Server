from __future__ import annotations
import json
from abc import ABC, abstractmethod
from typing import Callable
from src.Core.ResourceManager import DelayedTask, ResourceManager
import uuid


class IEventReceiver(ABC):
    """
    Think about this class like mailbox.
    It encapsulates physical endpoints of an event, like a websocket
    """
    def __init__(self, on_disconnect: Callable):
        self._on_disconnect = on_disconnect  # Likely add logic of deleting an endpoint here

    @abstractmethod
    def receive(self, message: str):
        pass

    def declare_disconnected(self):
        self._on_disconnect()


class UniCastEvent:
    """
    Think about this class like letter.
    The letter, being physical object, can be sent only to physical mailbox
    """
    def __init__(self, message: dict):
        self.msg = message.copy()
        self.id = uuid.uuid4().hex
        self.TIL = 10  # Time to live
        self.msg["event_id"] = self.id

    def __str__(self):
        return json.dumps(self.msg)


class Eventmanager:
    """
    Think about this class like a mailing company.
    It ensures that letters are reaching their destined mailboxes
    """
    def __init__(self, resource_manager: ResourceManager):
        self.events: set[str] = set()
        self.resource_man = resource_manager

    def _attempt_delivery(self, event: UniCastEvent, endpoint: IEventReceiver):
        if event.id in self.events and event.TIL > 0:
            event.TIL -= 1
            endpoint.receive(event.__str__())
            retry = DelayedTask(lambda: self._attempt_delivery(event, endpoint), 1000)
            self.resource_man.add_delayed_task(retry)
        else:
            endpoint.declare_disconnected()

    def start_delivery(self, event: UniCastEvent, endpoint: IEventReceiver):
        self.events.add(event.id)
        self._attempt_delivery(event, endpoint)

    def confirm_delivery(self, event_id: str):
        self.events.discard(event_id)


class EventLogicalEndpoint:
    """
       Think about this class like an organization.
       Organization can receive the level in any of its departments. Though, in this case
       it will receive it in all of its mailboxes.
       """

    def __init__(self, event_man: Eventmanager):
        self.endpoints: set[IEventReceiver] = set()
        self._event_manager = event_man

    def receive(self, event: dict):
        for mailbox in self.endpoints:
            e = UniCastEvent(event)
            self._event_manager.start_delivery(e, mailbox)


class EventLogicalEndpointWithSignature(EventLogicalEndpoint):
    """
        This subclass is used by backend to cumulate events in order to provide
        bulks send to frontend
    """

    def __init__(self, event_man: Eventmanager, signature: str | list[str]):
        super().__init__(event_man)
        self.signature = signature

    def receive(self, event: dict):
        ev_copy = event.copy()
        ev_copy["signature"] = self.signature
        for mailbox in self.endpoints:
            e = UniCastEvent(ev_copy)
            self._event_manager.start_delivery(e, mailbox)

    @staticmethod
    def merge(logical_endpoints: list[EventLogicalEndpointWithSignature], event_manager: Eventmanager) -> EventLogicalEndpointWithSignature:
        result_endpoint = set()
        result_signature = []
        for endpoint in logical_endpoints:
            result_endpoint = result_endpoint.union(endpoint.endpoints)
            if type(endpoint.signature) is not list:
                result_signature += [endpoint.signature]
            else:
                result_signature += endpoint.signature

        result = EventLogicalEndpointWithSignature(event_manager, result_signature)
        result.endpoints = result_endpoint
        return result
