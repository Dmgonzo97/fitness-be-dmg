from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
from flask_cors import CORS 
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bpqjwuibujsjsv:ebe943c91f8fe980a0bfb7b8fe03ca0a85f38d67e9242e4719ee08a9118bbcb8@ec2-52-201-124-168.compute-1.amazonaws.com:5432/d9l4vjjahr66n'
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
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

  if user is None:
    return jsonify('User is not verified!')

  if bcrypt.check_password_hash(user.password, password) == False:
    return jsonify('User is not verified!')

  return jsonify(user_schema.dump(user))

@app.route('/user/update/<id>', methods=["PUT"])
def updateUser(id):
  if request.content_type != 'application/json':
    return jsonify('Error: Data must be json')
    
  put_data = request.get_json()
  username = put_data.get('username')

  user_to_update = db.session.query(User).filter(User.id == id).first()

  if username != None:
    user_to_update.username = username
    
  db.session.commit()

  return jsonify(user_schema.dump(user_to_update))

@app.route('/user/pwupdate/<id>', methods=["PUT"])
def updatePW(id):
  if request.content_type != 'application/json':
    return jsonify('Error: Data must be json')
    
  password = request.get_json().get('password')
  user = db.session.query(User).filter(User.id == id).first()
  encrypted_password = bcrypt.generate_password_hash(password).decode('utf-8')
  user.password = encrypted_password
  
  db.session.commit()

  return jsonify(user_schema.dump(user))

@app.route('/user/get', methods=['GET'])
def get_all_users():
  result = db.session.query(User).all()
  return jsonify(multiple_user_schema.dump(result))

@app.route('/user/get/<id>', methods=['GET'])
def get_user_by_id(id):
  user = db.session.query(User).filter(User.id == id).first()
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

@app.route('/blog/get/<blog_user_id>/<id>', methods=['GET'])
def GetBlog(blog_user_id, id):
  blog = db.session.query(Blog).filter(User.id == blog_user_id).filter(Blog.id == id).first()
  return jsonify(blog_schema.dump(blog))

@app.route('/blog/delete/<blog_user_id>/<id>', methods=['DELETE'])
def DelBlog(blog_user_id, id):

  blog = db.session.query(Blog).filter(blog_user_id == User.id).filter(Blog.id == id).first()
  db.session.delete(blog)
  db.session.commit()

  return jsonify('Blog Deleted!')

if __name__ == '__main__':
  app.run(debug=True)