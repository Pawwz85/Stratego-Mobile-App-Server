from src.Events import Eventmanager, ResourceManager, UniCastEvent, IEventReceiver
#  TODO: Make this work


class EvenManagerWithTracking(Eventmanager):
    def __init__(self, resource_manager: ResourceManager):
        self.send_messages: dict[IEventReceiver, list[dict]] = dict()
        super().__init__(resource_manager)

    def start_delivery(self, event: UniCastEvent, endpoint: IEventReceiver):
        if self.send_messages.get(endpoint) is None:
            self.send_messages[endpoint] = []
        self.send_messages[endpoint] += [event.msg]
        return super().start_delivery(event, endpoint)

    def clear_tracking(self, endpoint: IEventReceiver):
        self.send_messages[endpoint].clear()

    def clear_tracking_all(self):
        for list_ in self.send_messages.values():
            list_.clear()
