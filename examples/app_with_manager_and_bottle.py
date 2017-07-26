from wsgiref.simple_server import make_server
from kruemelmonster import SimpleSessionMiddleware

from bottle import Bottle, auth_basic, request, run


app = Bottle()


@app.route('/')
def countvisits():
    session = request.environ.get('wsgisession')
    # google chrome sends 2 requests ...
    if request.environ['PATH_INFO'] != '/favicon.ico':
        session["counter"] = session.get("counter", 0) + 1
    return 'Visited {} times\n'.format(session['counter'])


app = SimpleSessionMiddleware(app)


if __name__ == '__main__':
    httpd = make_server('localhost', 8080, app)
    print("Listening on http://localhost:8080")

    httpd.serve_forever()
