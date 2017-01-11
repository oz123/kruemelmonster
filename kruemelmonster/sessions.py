"""
This file is distributed under the terms of the LGPL v3.
Copyright Oz N Tiram <oz.tiram@gmail.com> 2016
"""
import datetime
import peewee as pw

from .base import BaseSession

DATABASE = 'sessions.db'
UNITS = ('days', 'hours', 'minutes', 'seconds')

TRIGGER_SQL = """
CREATE TRIGGER IF NOT EXISTS clean_old_sessions
AFTER INSERT ON sessions
BEGIN
DELETE FROM sessions WHERE DATETIME(timestamp) <= DATETIME('now', '-{} {}');
END;
"""

# select strftime('%s', 'now') - strftime('%s', DATETIME('NOW', '-1 days'));

# TODO:
#
# * Add tests
# * Add support for json field
#

db = pw.SqliteDatabase(DATABASE)


class PeeweeSession(pw.Model):

    id = pw.CharField(unique=True)
    timestamp = pw.DateTimeField(default=datetime.datetime.utcnow)
    # Bug in peewee ???
    # timestamp = pw.TimestampField()
    data = pw.TextField()

    class Meta(object):
        database = None
        db_table = 'sessions'


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
                TRIGGER_SQL.format(ttl, ttl_unit)
                           ).execute()

        self.db.close()

    def __setitem__(self, id, data):
        self.db.connect()
        self.model.create(id=id, data=data).save()
        self.db.close()

    def __getitem__(self, id):
        self.db.connect()
        data = self.model.select().where(self.model.id == id).get().data
        self.db.close()
        return data

    def __contains__(self, id):
        self.db.connect()
        rv = self.model.select().where(self.model.id == id).exists()
        self.db.close()
        return rv
