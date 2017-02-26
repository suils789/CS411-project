from app import db 

class Users(db.Model): 
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(80))
	email = db.Column(db.String(120), unique=True)
	firstName = db.Column(db.String(50)) 
	lastName = db.Column(db.String(50))
	address = db.relationship('Spaces', backref='users', lazy='dynamic')

	@property
	def is_authenticated(self):
		return True

	@property
	def is_active(self):
		return True

	@property
	def is_anonymous(self):
		return False

	def get_id(self):
		try:
			return unicode(self.id) 
		except NameError:
			return str(self.id) 

	def __init__(self, username, password, email, firstName, lastName): 
		self.username = username
		self.password = password
		self.email = email 
		self.firstName = firstName
		self.lastName = lastName 

	def __repr__(self): 
		return '<User %r>' % self.username 

class Spaces(db.Model): 
	id = db.Column(db.Integer, primary_key=True) 
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	address = db.Column(db.String(200))
	is_taken = db.Column(db.Boolean) 

	def __init__(self, user_id, address, is_taken):
		self.user_id = user_id 
		self.address = address
		self.is_taken = is_taken 

	def __repr__(self): 
		return '<Spaces %r>' % self.address 