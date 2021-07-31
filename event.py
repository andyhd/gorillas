class Event(list):
    def __call__(self, *args, **kwargs):
        for listener in self:
            listener(*args, **kwargs)


class EventSource:
    def __getattr__(self, name):
        if name.startswith("on_"):
            event = getattr(self, name[3:], None)

            if isinstance(event, Event):
                return event.append

        return self.__getattribute__(name)
