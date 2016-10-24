from .base import DictBasedSessionManager, SimpleSession
from http.cookies import SimpleCookie


class SimpleSessionMiddleware:
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
        self.manager = session_manager()

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


class SessionMiddleware:

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
