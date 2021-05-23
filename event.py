class Event(list):
    def __call__(self, *args, **kwargs):
        for listener in self:
            listener(*args, **kwargs)


class EventSource:

    def __getattr__(self, name):
        if not name.startswith("on_"):
            return self.__getattribute__(name)

        event = name[3:]
        if not hasattr(self, event):
            setattr(self, event, Event())
        return getattr(self, event).append
