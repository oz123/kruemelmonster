# TODO: create sessions database
# TODO: test that sessions are inserted
# TODO: add trigger
# TODO: insert old sessions
# TODO: see if sessions are deleted
import datetime as dt
import sqlite3
import os
from krumelmonster.sessions import SqliteSessionManager, PeeweeSession, db

session_manager = None

def setup_module(module):
    global session_manager
    session_manager = SqliteSessionManager(db, PeeweeSession,
                                           ttl=60, ttl_unit='seconds')

def teardown_module(module):
    os.unlink('sessions.db')


def test_session_db_created():
    assert os.path.exists('sessions.db')


def test_session_db_is_not_locked():
    session_manager['abc'] = "it works"
    session_manager['def'] = "it works too"
    # the above assignments should work
    assert True

def test_sessions_inserted():
    conn = sqlite3.connect('sessions.db')
    cur = conn.cursor()
    cur.execute("select id, data from sessions;")
    sid, data = cur.fetchone()
    assert (sid, data) == ("abc", "it works")


def test_trigger_works():
    # add trigger
    assert False

