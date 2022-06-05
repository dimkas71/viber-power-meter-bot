from models import User
import db
import logging

#TODO: add logging 

def on_user_subscribed(id: str, name: str) -> User | None:
    return db.add_user(id, name)

def on_conversation_started(id: str, name: str) -> User | None:
    pass

def on_user_unsubscribed(id: str) -> User | None:
    return db.delete_user(id)

