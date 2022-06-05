from models import User
import db
import logging

#TODO: add logging 

def on_user_subscribed(id: str, name: str) -> User:
    return db.add_user(id, name)

def on_conversation_started(id: str, name: str) -> User:
    pass

def on_user_unsubscribed(id: str) -> User:
    return db.delete_user(id)

