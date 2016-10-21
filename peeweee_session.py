"""
This file is distributed under the terms of the LGPL v3.
Copyright Oz N Tiram <oz.tiram@gmail.com> 2016
"""
import datetime

import peewee as pw
from wsgisession import BaseSession

DATABASE = 'sessions.db'
UNITS = ['days', 'hours', 'minutes', 'seconds']

TRIGGER_SQL = """
CREATE TRIGGER IF NOT EXISTS clean_old_sessions
AFTER INSERT ON sessions
BEGIN
DELETE FROM sessions WHERE DATETIME(timestamp) <= DATETIME('now', '-{} {}');
END;
"""
# TODO:
#
# * Add trigger to remove old sessions
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
        database = db
        db_table = 'sessions'


def create_tables():
    db.connect()
    db.create_tables([PeeweeSession], safe=True)

create_tables()


class SqliteSessionManager(BaseSession):

    def __init__(self, db, model, ttl=None, ttl_unit='minutes'):
        self.db = db
        self.model = model
        if ttl and isinstance(ttl, int) and ttl_unit in UNITS:
            self.model.raw(
                TRIGGER_SQL.format(ttl, ttl_unit)
                           ).execute()

    def __setitem__(self, id, data):
        self.model.create(id=id, data=data).save()

    def __getitem__(self, id):
        return self.model.select().where(self.model.id == id).get().data

    def __contains__(self, id):
        if self.select().where(self.model.id == id).exists():
            return True
        else:
            return False
