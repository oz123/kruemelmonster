import inspect
import uuid


class BaseSessionMeta(type):

    def __new__(meta, name, bases, class_dict):
        # Don’t validate the abstract BaseSession class
        if bases != (object,):
            for item in ['__setitem__', '__getitem__', '__contains__']:
                method = class_dict.get(item)
                if not method or not inspect.isfunction(method):
                    raise ValueError(
                        '{} must define a method called {}'.format(name, item))

        return type.__new__(meta, name, bases, class_dict)


class BaseSession(object, metaclass=BaseSessionMeta):
    pass


class DictBasedSessionManager(BaseSession):

    sessions = {}

    def __setitem__(self, id, data):
        self.sessions[id] = data

    def __getitem__(self, id):
        if id in self.sessions:
            return self.sessions[id]

    def __contains__(self, id):
        if id in self.sessions:
            return True
        else:
            return False


class Session:

    __slots__ = ('id', 'data')

    def __init__(self):
        self.id = None
        self.data = {}

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        if key in self.data:
            return self.data[key]
        return default


class SimpleSession:

    __slots__ = ('id', 'data', 'manager')

    def __init__(self, manager_inst):
        self.id = None
        self.data = {}
        self.manager = manager_inst

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        if key in self.data:
            return self.data[key]
        return default

    def load(self, id):
        if id in self.manager:
            self.data = self.manager[id]
            self.id = id
        else:
            self.data = {}
            self.id = uuid.uuid4().hex

    def save(self):
        self.manager[self.id] = self.data
        return self.id
