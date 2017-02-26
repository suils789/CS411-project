from app import app, db, lm 
from flask import Flask, render_template, request, redirect, url_for, g, jsonify, abort, flash 
from flask.ext.login import login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update, and_, insert, create_engine, text
from .forms import LoginForm
from .models import Users, Spaces 
import googlemaps, json, requests 
gmaps = googlemaps.Client(key='AIzaSyDyIjazEKwGObz96R856yDFMuNJJXXPzyU') 

engine = create_engine('postgresql://localhost/ipark')

@lm.user_loader
def load_user(user_id):
	return Users.query.filter(Users.id == int(user_id)).first()

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET': 
		return render_template('login.html')
	if request.method == 'POST':	
		username = request.form['username']
		password = request.form['password']
		registered_user = Users.query.filter_by(username=username,password=password).first()
		if registered_user is None:
			flash('Username or Password is invalid' , 'error')
			return redirect(url_for('login'))
		login_user(registered_user)
		flash('Logged in successfully')
		return redirect(request.args.get('next') or url_for('index'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    message = "You have been logged out successfully" 
    return render_template('index.html', message=message)

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/map')
def map():
	return render_template('map.html')

@app.route('/signup')
def signup(): 
	return render_template('add_user.html')

@app.route('/post_user', methods=['POST']) 
def post_user(): 
	email = request.form['email']
	if send_simple_message(email) == True: 
		user = Users(request.form['username'],request.form['password'], email, request.form['firstName'], request.form['lastName'])
		db.session.add(user)
		db.session.commit() 
		return redirect(url_for('map')) 
	else: 
		return render_template('signuperror.html')

@app.route('/post_space', methods=['POST']) 
def post_space(): 
	address = request.form['address']
	user_id = current_user.id
	space = Spaces(user_id,request.form['address'], 'false')
	db.session.add(space)
	db.session.commit()
	return redirect(url_for('show_profile')) 

@app.route('/rent', methods = ['GET', 'POST'])
def rent():
	user_id = request.args.get('user_id')  
	user = Users.query.filter_by(id=user_id).first()
	address = request.args.get('address') 
	return render_template('rent.html', user_id=user_id, username=user.username, address=address)

@app.route('/payment', methods = ['GET', 'POST'])
def payment(): 
	address = request.args.get('address')  
	user_id = request.args.get('user_id')  
	return render_template('payment.html', user_id=user_id, address=address)

@app.route('/thankyou')
def fix(): 
	user_id = request.args.get('user_id')  
	address = request.args.get('address') 
	space = Spaces.query.filter_by(user_id=user_id, address=address).first() 
	space.is_taken = True
	db.session.commit() 
	return render_template('thankyou.html')

@app.route('/profile')
@login_required 
def show_profile(): 
	user = Users.query.filter_by(username=current_user.username).first()
	spaces = Spaces.query.filter_by(user_id=user.id).all()  
	return render_template('profile.html', user=user, spaces=spaces)

@app.route('/get_spaces', methods=['GET', 'POST'])
def get_spaces(): 
	place = request.form['address'] 
	result = Spaces.query.filter_by(is_taken='false').all() 
	spaces = []
	users = []
	for s in result: 
		spaces.append(s.address)
		users.append(s.user_id)
	(locations, add, d, u) = setLocation(place, spaces, users)
	if len(locations) == 0: 
		return render_template('locationserror.html')
	return render_template('mapMarkers.html', locations=locations, add=add, d=d, u=u)

def setLocation(loc, geo, users):
	close = 3218.69  #2 miles = 3218.69 meters which is the unit used by google maps
	geoSpaces = []
	spaces = geo   
	d = []    
	u = []         			
	for i in range(len(spaces)):
		distance = gmaps.distance_matrix(loc, spaces[i])
		m = distance['rows'][0]['elements'][0]['distance']['value']
		if m < close:
			u.append(users[i])
			geoSpaces.append(spaces[i])
			d.append(round(m * .000621371, 2)) #convert meters to miles

	closeSpaces = []
	add= [] 
	for j in range(len(geoSpaces)):
		geocode_result = gmaps.geocode(geoSpaces[j])
		lat = geocode_result[0]['geometry']['location']['lat']
		lng = geocode_result[0]['geometry']['location']['lng']
		closeSpaces.append([lat,lng])
		add.append(geoSpaces[j])
	return (closeSpaces, add, d, u) 

def send_simple_message(email):
	validationKey= "5c76f6c7426c9b01f8500e8b2b70c651"
	a = requests.post("https://apilayer.net/api/check?access_key=" + validationKey +"&email="+email+"&format=1")
	b = a.text
	c = str(b)
	d = ""
	for i in c:
		d += i
	d = d.split(",")
	smtp = d[6].split(':')
	if smtp[1] == 'true':
		return True
	else:
		return False

