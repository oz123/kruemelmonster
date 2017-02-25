from kruemelmonster.sessions import SqliteSessionManager, PeeweeSession
from kruemelmonster.middleware import SimpleSessionMiddleware

def app(environ, start_response):
    session = environ.get('wsgisession')
    session['counter'] = session.get('counter', 0) + 1
    start_response('200 OK', [('Content-Type', 'text/html')])
    return 'Visited %s times\n' % session['counter']



session_manager = SqliteSessionManager("app.db", PeeweeSession,
                                       ttl=None, ttl_unit='seconds')



if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8080, app)
    print("Listening on http://localhost:8080")

    httpd.serve_forever()

