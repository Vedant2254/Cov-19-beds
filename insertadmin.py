import json
from werkzeug.security import generate_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet

app = Flask(__name__)
key = Fernet.generate_key()
f = Fernet(key)
encoding = 'ascii'

# ------------------------- Make changes below ---------------------------
username = 'admin'
password = 'admin'
gmail = "your_gmail"
gpassword = 'app_password_of_your_gmail'
# ------------------------- Make changes above ---------------------------

with open('config.json', 'r') as c:
    content = json.load(c)
    dburi = content['database']['uri']

with open('config.json', 'w') as c:
    content['key'] = key.decode(encoding)
    json.dump(content, c)

app.config['SQLALCHEMY_DATABASE_URI'] = dburi
db = SQLAlchemy(app)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    gmail = db.Column(db.String(254))
    gpassword = db.Column(db.String(254))

with app.app_context():
    username = generate_password_hash(username)
    password = generate_password_hash(password)
    gpassword = f.encrypt(gpassword.encode(encoding)).decode(encoding)
    admin = Admin(username=username, password=password, gmail=gmail, gpassword=gpassword)
    db.engine.execute(f'TRUNCATE TABLE admin')
    db.session.add(admin)
    db.session.commit()
