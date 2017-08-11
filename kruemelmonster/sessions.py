"""
This file is distributed under the terms of the LGPL v3.
Copyright Oz N Tiram <oz.tiram@gmail.com> 2016
"""
import base64
import datetime
import hashlib
import hmac
import inspect
import json
import time

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


def for_all_methods(decorator):

    def decorate(cls):
        methods = inspect.getmembers(cls, predicate=inspect.ismethod)
        for name, method in methods:
            if name == '__init__':
                continue
            setattr(cls, name, decorator(method))

        return cls
    return decorate


def open_close_db(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        self.db.connect()
        rv = fn(self, *args, **kwargs)
        self.db.close()
        return rv

    return wrapper


@for_all_methods(open_close_db)
class SimpleSqliteSessionManager(BaseSession):

    """
    SqliteSessionManager - a session manager that uses SQLite.

    This session manager class is dumb and saves the information
    in the database and the cookie in clear text.

    Do not use it in real production. Instead you should use
    SafeSqliteSessionManager
    """

    def __init__(self, dbname, model, ttl=None, ttl_unit='minutes'):
        """
        param str: database file path
        param model: a Model instance

        Both model and db are currently using Peewee ORM, but it's easy to
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

    def __setitem__(self, id, data):
        fields = {"id": id}
        fields.update({"data": json.dumps(data)})
        query = pw.InsertQuery(self.model, rows=[fields])
        query.upsert().execute()

    def __getitem__(self, id):
        data = self.model.select().where(self.model.id == id).get().data
        data = json.loads(data)
        return data

    def __contains__(self, id):
        rv = self.model.select().where(self.model.id == id).exists()
        return rv


class SafeSqliteSessionManager(SimpleSqliteSessionManager):

    """
    A Session manager that helps you save data in SQLite in safe manner.

    It adds `load` and `save` methods that wrap your values properly.
    """
    encoding = 'utf-8'

    def __init__(self, dbname, model, secret, hash=hashlib.sha256,
                 ttl=None, ttl_unit='minutes'):
        super().__init__(dbname, model, ttl, ttl_unit)
        self.secret = secret

    def create_signature(self, value, timestamp):
        h = hmac.new(self.secret.encode(), digestmod=hashlib.sha1)
        h.update(timestamp)
        h.update(value)
        return h.hexdigest()

    def load(self, id):
        data = super().__getitem__(id)
        data = self.decrypt(data)
        return data

    def save(self, id, data):
        data = json.dumps(data, indent=None, separators=(',', ':'))
        data = self.encrypt(data)
        super().__setitem__(id, data)
        return data

    def encrypt(self, value):
        timestamp = str(int(time.time())).encode()
        value = base64.b64encode(value.encode(self.encoding))
        signature = self.create_signature(value, timestamp)
        return "|".join([value.decode(self.encoding),
                         timestamp.decode(self.encoding), signature])

    def decrypt(self, value):
        value, timestamp, signature = value.split("|")
        check = self.create_signature(value.encode(self.encoding),
                                      timestamp.encode())
        if check != signature:
            return None

        return base64.b64decode(value).decode(self.encoding)

    def _create_signature(self, value, timestamp):
        h = hmac.new(self.secret.encode(), digestmod=self.hash)
        h.update(timestamp)
        h.update(value)
        return h.hexdigest()
