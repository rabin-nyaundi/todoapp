import os, datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
DATABASE_URL = 'postgresql://admin:admin1@localhost/todo_app'

db = SQLAlchemy()


def get_date():
    return datetime.datetime.now()


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50),unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    task = db.relationship("Tasks", backref="user", lazy=True)



    def add_user(self,firstname,lastname,  email, password):
        user = Users(firstname=firstname, lastname=lastname, email=email, password=password)
        db.session.add(user)
        db.session.commit()


class Tasks(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(50),nullable=False)
    task_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.Date, default=get_date)
    status = db.Column(db.String(50), default = 'Not completed')

    def add_task(self, task, task_user, created_at, status):
        task = Tasks(task = task,task_user=task_user, created_at=created_at,status=status)
        db.session.add(task)
        db.session.commit()