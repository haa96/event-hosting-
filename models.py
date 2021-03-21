from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATION']= False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///p1.db'
db = SQLAlchemy(app)


tb_attendee = db.Table('tb_attendee',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100),nullable=False)
    password = db.Column(db.String(100),nullable=False)
    
    # 1-M relationship 
    hosting = db.relationship('Event', backref='host')
    
    #m-m attendee table:
    attendee = db.relationship('Event' , secondary=tb_attendee, backref = db.backref('attending_list', lazy='dynamic'))
    
    # init func
def __init__(self, username, password):
      self.username = username
      self.password  = password

def __repr__(self):
      return '<User {}>'.format(self.username)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_datentime = db.Column(db.String(100), nullable=False)
    end_datentime = db.Column(db.String(100), nullable=False)
    #1-M foreign key
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #event_attending = db.relationship('User' , secondary=tb_attendee, backref = db.backref('attending_list', lazy='dynamic'))


def __init__(self,title,description,start_datentime,end_datentime,host_id):
    self.title=title
    self.description=description
    self.start_datentime=start_datentime
    self.end_datentime=end_datentime
    self.host_id=host_id
def __repr__(self):
    return '<Event {}>'.format(self.title)
      


