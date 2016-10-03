import uuid

try:
    from Cookie import SimpleCookie
except ImportError:
    from http.cookies import SimpleCookie


class BaseSessionManager(object):

    def __init__(self, *args, **kwargs):
        """
        Use this to create database connections, etc.
        """
        pass

    def __setitem__(self, id, data):
        raise RuntimeError("Session manager must override __setitem__")

    def __getitem__(self, id):
        raise RuntimeError("Session manager must override __getitem__")

    def __contains__(self, id):
        raise RuntimeError("Session manager must override __contains__")


class DictBasedSessionManager(BaseSessionManager):

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


class Session(object):

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


class SimpleSession(object):

    def __init__(self, manager):
        self.id = None
        self.data = {}
        self.manager = manager()

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


class SimpleSessionMiddleware(object):
    """
    This class uses the manager attribute instead of a wrapping
    function factory.
    The manager is an instance of a simple class with magic attribute
    which is easy to understand and extend.
    """

    def __init__(self, app, session_manager=DictBasedSessionManager,
                 env_key='wsgisession', cookie_key='session_id'):
        self.app = app
        self.env_key = env_key
        self.cookie_key = cookie_key
        self.manager = session_manager

    def __call__(self, environ, start_response):
        cookie = SimpleCookie()
        if 'HTTP_COOKIE' in environ:
            cookie.load(environ['HTTP_COOKIE'])
        id = None
        if self.cookie_key in cookie:
            id = cookie[self.cookie_key].value
        session = SimpleSession(self.manager)
        session.load(id)
        environ[self.env_key] = session

        def middleware_start_response(status, response_headers, exc_info=None):
            session = environ[self.env_key]
            session.save()
            cookie = SimpleCookie()
            cookie[self.cookie_key] = session.id
            cookie[self.cookie_key]['path'] = '/'
            cookie_string = cookie[self.cookie_key].OutputString()
            response_headers.append(('Set-Cookie', cookie_string))
            return start_response(status, response_headers, exc_info)
        return self.app(environ, middleware_start_response)


class SessionMiddleware(object):

    def __init__(self, app, factory,
                 env_key='wsgisession', cookie_key='session_id'):
        self.app = app
        self.factory = factory
        self.env_key = env_key
        self.cookie_key = cookie_key

    def __call__(self, environ, start_response):
        cookie = SimpleCookie()
        if 'HTTP_COOKIE' in environ:
            cookie.load(environ['HTTP_COOKIE'])
        id = None
        if self.cookie_key in cookie:
            id = cookie[self.cookie_key].value
        environ[self.env_key] = self.factory.load(id)

        def middleware_start_response(status, response_headers, exc_info=None):
            id = self.factory.save(environ[self.env_key])
            cookie = SimpleCookie()
            cookie[self.cookie_key] = id
            cookie[self.cookie_key]['path'] = '/'
            cookie_string = cookie[self.cookie_key].OutputString()
            response_headers.append(('Set-Cookie', cookie_string))
            return start_response(status, response_headers, exc_info)
        return self.app(environ, middleware_start_response)
