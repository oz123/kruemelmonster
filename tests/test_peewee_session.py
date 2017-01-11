import datetime as dt
import os
import sqlite3
import time

from kruemelmonster.sessions import SqliteSessionManager, PeeweeSession, db

dbname = "foobar.db"
session_manager = None

def setup_module(module):
    global session_manager
    session_manager = SqliteSessionManager("foobar.db", PeeweeSession,
                                           ttl=None, ttl_unit='seconds')

#def teardown_module(module):
#    os.unlink('sessions.db')


def test_session_db_created():
    assert os.path.exists('sessions.db')


def test_session_db_is_not_locked():
    session_manager['abc'] = "it works"
    session_manager['def'] = "it works too"
    # the above assignments should work
    assert True


def test_no_trigger():
    "session manager should not have a trigger if not specified"
    conn = sqlite3.connect('sessions.db')
    cursor = conn.cursor()
    sql = "select name from sqlite_master where type = 'trigger';"
    cursor.execute(sql)
    data = cursor.fetchone()
    assert data is None

def test_sessions_inserted():
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute("select id, data from sessions;")
    sid, data = cursor.fetchone()
    assert (sid, data) == ("abc", "it works")

def test_trigger_works():
    # add trigger
    session_manager = SqliteSessionManager(dbname, PeeweeSession,
                                           ttl=1, ttl_unit='seconds')
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    time.sleep(1)
    session_manager['this'] = "deletes other sessions"
    cursor = conn.cursor()
    cursor.execute("select id from sessions;")
    data = cursor.fetchall()[0]
    assert data not in ("abc", "def")

