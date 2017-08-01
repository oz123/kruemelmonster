from wsgiref.simple_server import make_server
from kruemelmonster.sessions import SafeSqliteSessionManager, PeeweeSession
from kruemelmonster.middleware import SafeSessionMiddleware

sqlite_safe = SafeSqliteSessionManager("foobar.db", PeeweeSession,
                                          "very-sekret-key",
                                          ttl=None, ttl_unit='seconds')


def wrapped_app(environ, start_response):
    session = environ.get('wsgisession')
    # google chrome sends 2 requests ...
    if environ['PATH_INFO'] != '/favicon.ico':
        session["counter"] = session.get("counter", 0) + 1

    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['Visited {} times\n'.format(session['counter']).encode()]


app = SafeSessionMiddleware(wrapped_app, session_manager=sqlite_safe)


if __name__ == '__main__':
    httpd = make_server('localhost', 8080, app)
    print("Listening on http://localhost:8080")

    httpd.serve_forever()
