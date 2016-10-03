import uuid
from wsgiref.simple_server import make_server
from wsgisession import SessionMiddleware
from wsgisession import Session


sessions = {}


class ExampleFactory(object):

    def load(self, id):
        session = Session()
        if id in sessions:
            session.id = id
            session.data = sessions[id]
        else:
            pass

        return session

    def save(self, session):
        print(sessions)
        if not session.id:
            session.id = uuid.uuid4().hex

        sessions[session.id] = session.data
        return session.id


def wrapped_app(environ, start_response):
    session = environ.get('wsgisession')
    # google chrome sends 2 requests ...
    if environ['PATH_INFO'] != '/favicon.ico':
        session['counter'] = session.get('counter', 0) + 1

    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['Visited {} times\n'.format(session['counter']).encode()]


factory = ExampleFactory()
app = SessionMiddleware(wrapped_app, factory)

if __name__ == '__main__':
    httpd = make_server('localhost', 8080, app)
    print("Listening on http://localhost:8080")

    httpd.serve_forever()
