"""
This file is distributed under the terms of the LGPL v3.
Copyright Oz N Tiram <oz.tiram@gmail.com> 2016
"""

import peewee as pw
from wsgisession import BaseSession

DATABASE = 'sessions.db'

#
# TODO:
#
# * Add trigger to remove old sessions
# * Add tests
# * Add support for json field
# * Make sure that sessions are unique on the database level
#

db = pw.SqliteDatabase(DATABASE)


class Session(pw.Model):

    id = pw.CharField()
    data = pw.TextField()

    class Meta(object):
        database = db


def create_tables():
    db.connect()
    db.create_tables([Session])

create_tables()


class PeeweeSession(BaseSession):

    def __init__(self, db):
        self.db = db

    def __setitem__(self, id, data):
        Session.create(id=id, data=data).save()

    def __getitem__(self, id):
        return Session.select().where(Session.id == id).get().data

    def __contains__(self, id):
        if Session.select().where(Session.id == id).exists():
            return True
        else:
            return False
