#all the imports
import sqlite3, os
from flask import Flask, request, session, g, redirect, url_for, abort,\
	render_template, flash

#create our little application
app = Flask(__name__)
app.config.from_object(__name__)

#Load default config and override config from an environment variable
app.config.update( dict(
	DATABASE=os.path.join(app.root_path, 'flaskr.db'),
	DEBUG=True,
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
	"""Connects to the specific database."""
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def get_db():
	"""Opens a new database connection if there is none yet for the
	current application context
	"""
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
	"""Closes the database again at the end of the request"""
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()


@app.route('/')
def show_entries():
	db = get_db()
	cur = db.execute('select title, text from entries order by id desc')
	entries = cur.fetchall()
	return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	db.execute('insert into entries (title,text) values (?, ?)',
				[request.form['title'], request.form['text']])
	db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_entries'))
	return render_template('login.html', error=error)


@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))


@app.route('/teams', methods=['POST'])
def add_team():
	print request.form #for debugging purposes
	db = get_db()
	cur = db.execute('insert into teams (name) values (?)', [request.form['name']])
	db.commit()
	return redirect(url_for('show_teams'))

@app.route('/teams')
def show_teams():
	db = get_db()
	cur = db.execute('select id, name from teams')
	teams = cur.fetchall()
	return render_template('show_teams.html', teams=teams)


@app.route('/players', methods=['POST'])
def add_player():
	print request.form # for debugging
	db = get_db()
	cur = db.execute("select id, name from teams where name=?", (request.form['team'],))
	teams = cur.fetchall()
	print teams
	if len(teams) == 0:
		cur = db.execute("insert into teams (name) values (?)", [request.form['team']])
		db.commit()
		teams = cur.fetchall()
		print teams
	cur = db.execute('insert into players (firstname, lastname, playernumber, position) values (?,?,?,?)', [request.form['firstname'], request.form['lastname'], request.form['number'], request.form['position']])
	db.commit()
	return redirect(url_for('show_players'))


@app.route('/players')
def show_players():
	db = get_db()
	cur = db.execute('select firstname, lastname, playernumber, position from players')
	players = cur.fetchall()
	return render_template('show_players.html', players=players)

if __name__ == '__main__':
	app.run()