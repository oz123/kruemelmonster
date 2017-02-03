from peewee.sessions import SqliteSessionManager, PeeweeSession


def app(environ, start_response):
    session = environ.get('wsgisession')
    session['counter'] = session.get('counter', 0) + 1
    start_response('200 OK', [('Content-Type', 'text/html')])
    return 'Visited %s times\n' % session['counter']



session_manager = SqliteSessionManager("app.db", PeeweeSession,
                                       ttl=None, ttl_unit='seconds')
