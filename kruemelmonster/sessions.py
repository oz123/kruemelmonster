"""
This file is distributed under the terms of the LGPL v3.
Copyright Oz N Tiram <oz.tiram@gmail.com> 2016
"""
import datetime
import json

import peewee as pw

from .base import BaseSession
UNITS = ('days', 'hours', 'minutes', 'seconds')

TRIGGER_SQL = """
CREATE TRIGGER IF NOT EXISTS clean_old_sessions
AFTER INSERT ON sessions
BEGIN
DELETE FROM sessions WHERE DATETIME(timestamp) <= DATETIME('now', '-{} {}');
END;
"""

# select strftime('%s', 'now') - strftime('%s', DATETIME('NOW', '-1 days'));


class PeeweeSession(pw.Model):

    id = pw.CharField(unique=True)
    timestamp = pw.DateTimeField(default=datetime.datetime.utcnow)
    # Bug in peewee ???
    # timestamp = pw.TimestampField()
    data = pw.TextField()

    class Meta(object):
        database = None
        db_table = 'sessions'



def open_close_db(method):

    def wrap(*args, **kwargs):
        inst = args[0]
        inst.db.connect()
        method(*args, **kwargs)
        inst.db.close()

    return wrap


class SqliteSessionManager(BaseSession):

    """
    SqliteSessionManager - a session manager that uses SQLite.
    """

    def __init__(self, dbname, model, ttl=None, ttl_unit='minutes'):
        """
        :param str: database file path
        :param model: a Model instance

        Both model and db are currently use Peewee ORM, but it's easy to
        change this to another ORM.
        """

        self.dbname = dbname
        self.model = model
        self.db = self.model._meta.database
        self.model._meta.database.init(self.dbname)
        self.db.connect()
        self.db.create_tables([model], safe=True)

        if ttl and not isinstance(ttl, int):
            raise ValueError("ttl must be an integer.")
        if ttl_unit not in UNITS:
            raise ValueError("Illegal ttl_unit.")
        if ttl:
            self.model.raw(
                TRIGGER_SQL.format(ttl, ttl_unit)).execute()

        self.db.close()

    @open_close_db
    def __setitem__(self, id, data):
        fields = {"id": id}
        fields.update({"data": json.dumps(data)})
        query = pw.InsertQuery(self.model, rows=[fields])
        query.upsert().execute()

    @open_close_db
    def __getitem__(self, id):
        data = self.model.select().where(self.model.id == id).get().data
        data = json.loads(data)
        return data

    @open_close_db
    def __contains__(self, id):
        rv = self.model.select().where(self.model.id == id).exists()
        return rv
