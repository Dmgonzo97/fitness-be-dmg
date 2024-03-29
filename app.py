from datetime import datetime
from datetime import timedelta
from datetime import timezone

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
from flask_cors import CORS 
from flask_bcrypt import Bcrypt

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies

import jwt
import os

app = Flask(__name__)

# basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bmlpkrakjcqzyk:00bcf62411fc190564457c4ce69556c85c036745d5baa758b17c213b2e707a8b@ec2-18-214-134-226.compute-1.amazonaws.com:5432/detdhf7u0j65cu'
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config['JWT_SECRET_KEY'] = 'asdkjfhasdiukfgafsubfdhjkfbajskdfhakjsdflhajklds##216459756476312'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String, unique=True, nullable=False)
  password = db.Column(db.String, nullable=False)
  blogs = db.relationship('Blog', backref='user', cascade='all, delete, delete-orphan')

  def __init__(self, username, password):
    self.username = username
    self.password = password

class Blog(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  blog_name = db.Column(db.String, nullable=False)
  blog_text = db.Column(db.String, nullable=False)
  blog_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

  def __init__(self, blog_name, blog_text, blog_user_id):
    self.blog_name = blog_name
    self.blog_text = blog_text
    self.blog_user_id = blog_user_id

class BlogSchema(ma.Schema):
  class Meta:
    fields = ('id', 'blog_name', 'blog_text', 'blog_user_id')

blog_schema = BlogSchema()
multiple_blog_schema = BlogSchema(many=True)

class UserSchema(ma.Schema):
  class Meta:
    fields = ('id', 'username', 'password', 'blogs')
  blogs = ma.Nested(multiple_blog_schema)

user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)

@app.after_request
def refresh_expiring_token(response):
  try:
    exp_timestamp = get_jwt()['exp']
    now = datetime.now(timezone.utc)
    target_timestamp = datetime.timestamp(now + timedelta(hours=1))
    if target_timestamp > exp_timestamp:
      access_token = create_access_token(identity=get_jwt_identity())
      set_access_cookies(response, access_token)
    return response
  except (RuntimeError, KeyError):
    return response

# routes

@app.route('/user/add', methods=['POST'])
def add_user():
  if request.content_type != 'application/json':
    return jsonify('Error: Data must be json')

  post_data = request.get_json()
  username = post_data.get('username')
  password = post_data.get('password')

  username_duplicate = db.session.query(User).filter(User.username == username).first()

  if username_duplicate is not None:
    return jsonify('Error: Username Already Exist')

  
  encrypted_password = bcrypt.generate_password_hash(password).decode('utf-8')
  new_user = User(username, encrypted_password)

  db.session.add(new_user)
  db.session.commit()

  return jsonify(user_schema.dump(new_user))

@app.route('/user/verify', methods=['POST'])
def verify_user():
  if request.content_type != 'application/json':
    return jsonify('Error: Data must be json')

  post_data = request.get_json()
  username = post_data.get('username')
  password = post_data.get('password')

  user = db.session.query(User).filter(User.username == username).first()

  if user is None or bcrypt.check_password_hash(user.password, password) == False:
    return jsonify('User is not verified'), 401

  response = jsonify('Verification Sucessful!')
  access_token = create_access_token(identity=username)
  set_access_cookies(response, access_token)
  return jsonify(access_token=access_token)

@app.route('/user/logOut', methods=['POST'])
def logOut():
  response = jsonify('Log Out Sucessful')
  unset_jwt_cookies(response)
  return response

@app.route('/user/update/<id>', methods=['POST'])
def update_user_by_id(id):
  if request.content_type != 'application/json':
    return jsonify('Error: Data must be json')
  
  user = User.query.get(id)

  post_data = request.get_json()
  username = post_data.get('new_username')
  password = post_data.get('new_password')

  encrypted_password = bcrypt.generate_password_hash(password).decode('utf-8')

  if user:
    user.username = username
    user.password = encrypted_password

    db.session.commit()
    response = jsonify(user_schema.dump(user))
    return response
  else:
    response = jsonify('User not found')
    return response

@app.route('/user/get', methods=['GET'])
def get_all_users():
  result = db.session.query(User).all()
  return jsonify(multiple_user_schema.dump(result))

@app.route('/user/get/<username>', methods=['GET'])
def get_user_by_username(username):
  user = db.session.query(User).filter(User.username == username).first()
  return jsonify(user_schema.dump(user))

@app.route('/user/delete/<id>', methods=['DELETE'])
def delete_user_by_id(id):
  user = db.session.query(User).filter(User.id == id).first()
  db.session.delete(user)
  db.session.commit()

  return jsonify('User Deleted!')

# Endpoints for Blogs

@app.route('/blog/add', methods=['POST'])
def add_blog():
  if request.content_type != 'application/json':
    return jsonify('Error: Data must be json')

  post_data = request.get_json()
  blog_name = post_data.get('blog_name')
  blog_text = post_data.get('blog_text')
  blog_user_id = post_data.get('blog_user_id')
  new_blog = Blog(blog_name, blog_text, blog_user_id)
  db.session.add(new_blog)
  db.session.commit()

  return jsonify(blog_schema.dump(new_blog))

@app.route('/blog/get/<user_id>', methods=['GET'])
def get_all_blogs(user_id):
  all_blogs = db.session.query(Blog).filter(Blog.blog_user_id == user_id)
  return jsonify(multiple_blog_schema.dump(all_blogs))

@app.route('/blog/get/<blog_user_id>/<id>', methods=['GET'])
def get_blog(blog_user_id, id):
  blog = db.session.query(Blog).filter(User.id == blog_user_id).filter(Blog.id == id).first()
  return jsonify(blog_schema.dump(blog))

@app.route('/blog/delete/<blog_user_id>/<id>', methods=['DELETE'])
def delete_blog(blog_user_id, id):

  blog = db.session.query(Blog).filter(blog_user_id == User.id).filter(Blog.id == id).first()
  db.session.delete(blog)
  db.session.commit()

  return jsonify('Blog Deleted!')

if __name__ == '__main__':
  app.run(debug=True)