# TODO: create sessions database
# TODO: test that sessions are inserted
# TODO: add trigger
# TODO: insert old sessions
# TODO: see if sessions are deleted
import datetime as dt
import sqlite3
import os
from krumelmonster.sessions import SqliteSessionManager, PeeweeSession, db


session_manager = SqliteSessionManager(db, PeeweeSession,
                                       ttl=60, ttl_unit='seconds')



def test_session_db_created():
    assert os.path.exists('sessions.db')


def test_session_db_is_not_locked():
    assert False


def test_sessions_inserted():
    assert False


def test_trigger_works():
    # add trigger
    assert False
