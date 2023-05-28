import datetime

import peewee

database = peewee.SqliteDatabase("db.sqlite")


def init_db():
    database.connect()
    database.create_tables([Message, Dialog, DialogMessage, Chat])


class Message(peewee.Model):
    id = peewee.AutoField(primary_key=True)
    text = peewee.TextField(null=False)
    chat_id = peewee.IntegerField(null=False)
    message_id = peewee.IntegerField(null=False)
    answer = peewee.TextField(null=True)
    answer_id = peewee.IntegerField(null=True)
    time = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = database


class Dialog(peewee.Model):
    id = peewee.AutoField(primary_key=True)

    class Meta:
        database = database


class DialogMessage(peewee.Model):
    id = peewee.AutoField(primary_key=True)
    dialog = peewee.ForeignKeyField(Dialog, backref='messages')
    role = peewee.TextField()
    text = peewee.TextField()

    class Meta:
        database = database


class Chat(peewee.Model):
    id = peewee.AutoField(primary_key=True)
    chat_id = peewee.IntegerField(null=False, index=True)
    last_message_id = peewee.IntegerField(null=False, default=-1)
    is_dialog_now = peewee.BooleanField(null=False, default=False)
    current_dialog = peewee.ForeignKeyField(Dialog, backref='chat', null=True)

    class Meta:
        database = database
