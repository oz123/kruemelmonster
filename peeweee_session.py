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
#

db = pw.SqliteDatabase(DATABASE)


class PeeweeSession(pw.Model):

    id = pw.CharField(unique=True)
    data = pw.TextField()

    class Meta(object):
        database = db
        db_table = 'sessions'


def create_tables():
    db.connect()
    db.create_tables([PeeweeSession], safe=True)

create_tables()


class SqliteSessionManager(BaseSession):

    def __init__(self, db, model):
        self.db = db
        self.model = model

    def __setitem__(self, id, data):
        self.model.create(id=id, data=data).save()

    def __getitem__(self, id):
        return self.model.select().where(self.model.id == id).get().data

    def __contains__(self, id):
        if self.select().where(self.model.id == id).exists():
            return True
        else:
            return False
