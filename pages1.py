import time
import os
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, User, Event

app = Flask(__name__)


PER_PAGE = 12
SECRET_KEY = 'secretkey'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'p1.db')

app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True 

db.init_app(app)


@app.cli.command('initdb')
def initdb_command():

	db.drop_all()
	db.create_all()
	print('Initialized the database.')


def get_user_id(username):
	temp = User.query.filter_by(username=username).first()
	return temp.id if temp else None

def get_event_id(title):
	temp = Event.query.filter_by(title=title).first()
	return temp.id if temp else None

@app.before_request
def before_request():
	g.user = None
	if 'id' in session:
		g.user = User.query.filter_by(id=session['id']).first()

@app.route('/')
def root():
	if not g.user:
		return redirect(url_for('public_timeline'))
	temp = User.query.filter_by(id=session['id']).first()
	timeline_ids = [temp.id]
	for f in temp.hosting:
		timeline_ids.append(f.id)
	events = Event.query.filter(Event.host_id.in_(timeline_ids)).order_by(Event.start_datentime.asc()).limit(PER_PAGE).all()
	return render_template('timeline.html', events=events)

@app.route('/public')
def public_timeline():
	return render_template('timeline.html', events=Event.query.order_by(Event.start_datentime.asc()).limit(PER_PAGE).all())


@app.route('/login', methods=['GET', 'POST'])
def login():

	if g.user:
		return redirect(url_for('root'))
	error = None
	if request.method == 'POST':
		user = User.query.filter_by(username=request.form['username']).first()
		if user is None:
			error = 'Invalid username'
		elif not check_password_hash(user.password,request.form['password']):
			error = 'Invalid password'
		else:
			flash('Logged in successfully!')
			session['id'] = user.id
			return redirect(url_for('root'))		
	return render_template('login.html', error=error)


@app.route('/register', methods=['GET','POST'])
def register():
	if g.user:
		return redirect(url_for('root'))
	error = None
	if request.method == 'POST':
		if not request.form['username']: 
			error = 'Username feild is empty'
		elif not request.form['password']:
			error = 'Password feild is empty'
		elif get_user_id(request.form['username']) is not None:
			error = 'This username already exists! Please choose different one'
		else:
			input_username = request.form['username']
			input_password = generate_password_hash(request.form['password'])
			new_user = User(username=input_username,password=input_password)
			db.session.add(new_user)
			db.session.commit()
			flash('Registeration is complete')
			return redirect(url_for('login'))
	return render_template('register.html', error=error)

	
@app.route('/create_event', methods=['GET' , 'POST'])
def create_event():
	error = None
	if request.method=="POST":
		if not request.form['title']:
			error = 'Title field is empty!'
		elif not request.form['start_datentime']:
			error = 'Please specify event starting date&time!'	
		elif not request.form['end_datentime']:
			error = 'Please specify event ending date&time!'
		else:	
			event = Event(title=request.form['title'],
			description=request.form['description'],
			start_datentime=request.form['start_datentime'],
			end_datentime=request.form['end_datentime'] , host_id=
			session['id'])
			db.session.add(event)
			db.session.commit()
			flash('Your event is created!')
			session['Logged_in'] = True;
			return redirect(url_for('public_timeline'))
	return render_template('create_event.html', error=error)

@app.route('/cancel_event', methods=['GET' , 'POST'])
def cancel_event():

	
	error = None
	
	if request.method=="POST":
		if not request.form['title']:
			error = 'Title field is empty!'
		elif not request.form['start_datentime']:
			error = 'Please specify event starting date&time!'
		else:
			e_title = request.form['title']
			e_start = request.form['start_datentime']
			event = Event.query.filter_by(title=e_title, start_datentime= e_start).first()
			db.session.delete(event)
			db.session.commit()
			flash('Your event is cancelled!')
			session['Logged_in'] = True;
			return redirect(url_for('public_timeline'))
	return render_template('cancel_event.html', error=error)


@app.route('/<username>/<title>')
def user_events(username,title):

	profile_user = User.query.filter_by(username=username).first()
	attending = False
	if g.user:
		attending = Event.query.filter_by(id=get_event_id(title)).first().attending_list.filter_by(id=profile_user.id).first() is not None
	e = Event.query.filter_by(host_id=profile_user.id).order_by(Event.start_datentime.asc()).limit(PER_PAGE).all()
	return render_template('timeline.html', events=e, attending=attending, profile_user=profile_user)


@app.route('/<title>/attend')
def attend_event(title):
	event_id = get_event_id(title)
	Event.query.filter_by(id=event_id).first().attending_list.append(g.user)
	db.session.commit()
	flash('Yay! You are on the attending list! "%s"' % g.user.username)
	return redirect(url_for('user_events', username=g.user.username, title=title))


@app.route('/logout')
def logout():
	flash('You were logged out')
	session.pop('id', None)
	return redirect(url_for('public_timeline'))

