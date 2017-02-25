from kruemelmonster.sessions import SqliteSessionManager, PeeweeSession
from kruemelmonster.middleware import SimpleSessionMiddleware


def app(environ, start_response):
    session = environ.get('wsgisession')
    # google chrome sends 2 requests ...
    if environ['PATH_INFO'] != '/favicon.ico':
        session["counter"] = session.get("counter", 0) + 1

    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['Visited {} times\n'.format(session['counter']).encode()]


session_manager = SqliteSessionManager("app.db", PeeweeSession,
                                       ttl=None, ttl_unit='seconds')

app = SimpleSessionMiddleware(app, session_manager=session_manager)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8080, app)
    print("Listening on http://localhost:8080")
    httpd.serve_forever()
