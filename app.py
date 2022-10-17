from http.client import HTTPException
from pydoc import ispath
from flask import Flask, current_app, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, logout_user, login_user, login_manager, LoginManager, current_user
from flask_mail import Mail
from sqlalchemy import func
import werkzeug
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import json

# reading config file
encoding = 'ascii'
with open('config.json', 'r') as config:
    contents = json.load(config)
    dburi = contents["database"]["uri"]
    f = Fernet(contents['key'].encode(encoding))

# creating flask app
app = Flask(__name__)
app.secret_key = "topsecretdonotread"
app.config['SQLALCHEMY_DATABASE_URI'] = dburi
db = SQLAlchemy(app)

# setting up login manager
login_manager = LoginManager(app)
login_manager.login_view = 'user_login'
login_manager.login_message = "Please login first"
login_manager.login_message_category = "warning"


# userloader
@login_manager.user_loader
def load_user(user_id):
    return Patient.query.filter_by(srfid=user_id).first() or Hospitaluser.query.filter_by(hcode=user_id).first() or Admin.query.filter_by(username=user_id).first()


# Database models
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    gmail = db.Column(db.String(254))
    gpassword = db.Column(db.String(254))

    def get_id(self):
        return self.username


class Patient(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    srfid = db.Column(db.String(13), unique=True)
    email = db.Column(db.String(254), unique=True)
    dob = db.Column(db.String(10))
    password = db.Column(db.String(254))

    def get_id(self):
        return self.srfid


class Hospitaluser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(10), unique=True)
    email = db.Column(db.String(254), unique=True)
    password = db.Column(db.String(1000))

    def get_id(self):
        return self.hcode


class Hospitaldata(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(20), unique=True)
    hname = db.Column(db.String(200))
    normalbed = db.Column(db.Integer)
    hicubed = db.Column(db.Integer)
    icubed = db.Column(db.Integer)
    ventbed = db.Column(db.Integer)


class Bookingpatient(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    srfid = db.Column(db.String(20), unique=True)
    bedtype = db.Column(db.String(10))
    hcode = db.Column(db.String(20), unique=True)
    spo2 = db.Column(db.Integer)
    pname = db.Column(db.String(50))
    pphone = db.Column(db.String(12))
    paddress = db.Column(db.String(100))


# setting up mail
def get_admin():
    return Admin.query.filter_by().first()

def initiate_mail(admin):
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT='465',
        MAIL_USE_SSL=True,
        MAIL_USERNAME=admin.gmail,
        MAIL_PASSWORD=f.decrypt(
            admin.gpassword.encode(encoding)).decode(encoding)
    )


# required decorators
def make_sure_user(access_to):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                if access_to == 'admin':
                    current_user.username

                if access_to == 'patient':
                    current_user.srfid

                if access_to == 'hospital':
                    current_user.hcode

            except:
                flash("Method not allowed", "danger")
                return redirect('/')

            return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        return wrapper

    return decorator


# ROUTES

# routes accessible by everyone
@app.route('/')
def home():
    hoscount = Hospitaluser.query.count()
    pcount = Bookingpatient.query.count()
    normalbed = db.engine.execute(
        db.select(func.sum(Hospitaldata.normalbed))).fetchall()[0][0]
    hicubed = db.engine.execute(
        db.select(func.sum(Hospitaldata.hicubed))).fetchall()[0][0]
    icubed = db.engine.execute(
        db.select(func.sum(Hospitaldata.icubed))).fetchall()[0][0]
    ventbed = db.engine.execute(
        db.select(func.sum(Hospitaldata.ventbed))).fetchall()[0][0]

    beds = 0

    if (normalbed):
        beds = normalbed+hicubed+icubed+ventbed
    
    return render_template('index.html', hoscount=hoscount, pcount=pcount, beds=beds)


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by().first()

        if (admin and check_password_hash(admin.username, username) and check_password_hash(admin.password, password)):
            login_user(admin)
            flash("Login Success", "success")
            return redirect("/")

        flash("Invalid Credentials", "danger")

    return render_template("admin.html")


@app.route('/hospitallogin', methods=['GET', 'POST'])
def hospital_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Hospitaluser.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login Success", "success")
            return redirect('/')

        else:
            flash("Invalid Credentials", "danger")
            return render_template("hospitallogin.html")

    return render_template('hospitallogin.html')


@app.route('/usersignup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        srfid = request.form.get('srfid')
        email = request.form.get('email')
        dob = request.form.get('dob')
        encpass = generate_password_hash(request.form.get('password'))
        srfid_exists = Patient.query.filter_by(srfid=srfid).first()
        email_exists = Patient.query.filter_by(email=email).first()

        if (len(srfid) != 13):
            flash("SrfID must be strictly 13 digit number", "warning")
            return render_template("usersignup.html")

        if srfid_exists or email_exists:
            flash("User with entered email or srfid already exists", "warning")
            return render_template("usersignup.html")

        db.engine.execute(
            f"INSERT INTO patient (srfid, email, dob, password) VALUES ('{srfid}', '{email}', '{dob}', '{encpass}')")

        flash("Signup success, please login here", "success")
        return render_template('userlogin.html')

    return render_template('usersignup.html')


@app.route('/userlogin', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        logout_user()
        srfid = request.form.get('srfid')
        password = request.form.get('password')
        patient = Patient.query.filter_by(srfid=srfid).first()

        if patient and check_password_hash(patient.password, password):
            login_user(patient)
            flash("Login Success", "success")
            return redirect("/")

        else:
            flash("Invalid Credentials", "danger")
            return render_template("userlogin.html")

    return render_template('userlogin.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout Successful", "warning")
    return redirect('/')


@app.route("/availablebeds")
def available_beds():
    posts = Hospitaldata.query.all()
    return render_template("availablebeds.html", posts=posts)


# routes accessible by admin only
@app.route('/addhospitaluser', methods=['GET', 'POST'])
@login_required
@make_sure_user('admin')
def add_hospital_user():
    if request.method == 'POST':
        hcode = request.form.get('hcode').upper()
        email = request.form.get('email')
        password = request.form.get('password')
        encpass = generate_password_hash(password)
        hcode_exists = Hospitaluser.query.filter_by(hcode=hcode).first()
        email_exists = Hospitaluser.query.filter_by(email=email).first()

        if len(hcode) > 10:
            flash("HCODE must be less than 10 characters", "warning")
            return render_template("addHosUser.html")

        if hcode_exists or email_exists:
            flash("Hospital with entered hcode or email already exists", "warning")
            return render_template("addHosUser.html")

        new_hos = Hospitaluser(hcode=hcode, email=email, password=encpass)
        db.session.add(new_hos)

        try:
            ''' Sending email - uncomment this section
            message = (
                "Thankyou for choosing us!\n\n" +
                "As per your request we are registering your hospital with us. We are happy to have you " +
                "and we appreciate your support for making booking process easier for patients.\n\n" +

                "Here are your login credentials:\n" +
                f"Hospital code: {hcode}\n"
                f"Email: {email}\n"
                f"Password: {password}\n\n"

                "Now you can use above credentials to login to your hospital's account on our site " +
                "http://localhost:5000. Do add your hospital data, so that others can view and book your beds.\n" +
                "Thankyou."
            )

            admin = get_admin()
            initiate_mail(admin)
            Mail(app).send_message('COVID CARE CENTRE',
                                    sender=admin.gmail,
                                    recipients=[email],
                                    body=message
                                    )
            '''
            
            db.session.commit()
            flash("Data Sent and Inserted Successfully", "success")

        except:
            flash("Failed, Error occured while sending mail, hospital not added", "danger")

    return render_template('addHosUser.html')


@app.route("/triggeredevents")
@login_required
@make_sure_user('admin')
def triggered_events():
    trigdata = db.engine.execute(f"SELECT * FROM trigevents")
    return render_template("triggeredevents.html", trigdata=trigdata)


# routes accessible by hospitals only
@app.route("/addhospitalinfo", methods=['POST', 'GET'])
@login_required
@make_sure_user('hospital')
def add_hospital_info():
    if request.method == 'POST':
        hcode = request.form.get('hcode').upper()
        hname = request.form.get('hname')
        normalbed = request.form.get('normalbed')
        hicubed = request.form.get('hicubed')
        icubed = request.form.get('icubed')
        ventbed = request.form.get('ventbed')
        hos_exists = Hospitaluser.query.filter_by(hcode=hcode).first()
        hos_data_exists = Hospitaldata.query.filter_by(hcode=hcode).first()

        if (current_user.hcode != hcode):
            flash(
                "HCODE mismatch, please login with your hospital account to change data")

        if hos_data_exists:
            flash("Data is already present, you can update it", "warning")

        elif hos_exists:
            new_data = Hospitaldata(hcode=hcode, hname=hname, normalbed=normalbed, hicubed=hicubed, icubed=icubed, ventbed=ventbed)
            db.session.add(new_data)
            db.session.commit()
            flash("Data added", "primary")

        else:
            flash("Hospital code does not exist", "danger")

        return redirect("/addhospitalinfo")

    posts = Hospitaluser.query.filter_by(email=current_user.email).first()
    postsdata = Hospitaldata.query.filter_by(hcode=posts.hcode).first()
    return render_template("hospitaldata.html", postsdata=postsdata)


@app.route("/hedit/<string:id>", methods=['POST', 'GET'])
@login_required
@make_sure_user('hospital')
def hedit(id):
    curruser = current_user.hcode
    urluser = Hospitaldata.query.filter_by(id=id).first().hcode
    if (curruser != urluser):
        flash("ID mismatch, please login with your account to change data", "warning")
        return redirect("/addhospitalinfo")

    if request.method == "POST":
        hcode = request.form.get('hcode').upper()
        hname = request.form.get('hname')
        normalbed = request.form.get('normalbed')
        hicubed = request.form.get('hicubed')
        icubed = request.form.get('icubed')
        ventbed = request.form.get('ventbed')

        db.session.query(Hospitaldata).filter_by(id=id).update({
            'hcode': hcode,
            'hname': hname,
            'normalbed': normalbed,
            'hicubed': hicubed,
            'icubed': icubed,
            'ventbed': ventbed
        })
        db.session.commit()
        flash("Data successfully updated", "success")

        return redirect("/addhospitalinfo")

    posts = Hospitaldata.query.filter_by(id=id).first()
    return render_template("hedit.html", posts=posts)


@app.route("/hdelete/<string:id>", methods=['POST', 'GET'])
@login_required
@make_sure_user('hospital')
def hdelete(id):
    curruser = current_user.hcode
    urluser = Hospitaldata.query.filter_by(id=id).first().hcode

    if (curruser != urluser):
        flash("ID mismatch, please login with your account to delete data", "warning")
    else:
        db.session.query(Hospitaldata).filter_by(id=id).delete()
        db.session.commit()
        flash("Data successfully deleted", "danger")

    return redirect("/addhospitalinfo")


@app.route("/pbookings")
@login_required
@make_sure_user('hospital')
def pbookings():
    posts = Bookingpatient.query.filter_by(hcode=current_user.hcode)
    return render_template("pbookings.html", posts=posts)


# routes accessible by patients
@app.route("/changepass", methods=['GET', 'POST'])
@login_required
@make_sure_user('patient')
def change_pass():

    if request.method == 'POST':
        oldpass = request.form.get('old-password')
        newpass = request.form.get('new-password')

        if check_password_hash(current_user.password, oldpass):
            db.session.query(Patient).filter_by(srfid=current_user.srfid).update(
                {'password': generate_password_hash(newpass)})
            db.session.commit()
            flash("Password change successfully", "success")

        else:
            flash("Entered old password is wrong", "danger")

    return render_template('changepass.html')


@app.route("/slotbooking", methods=['GET', 'POST'])
@login_required
@make_sure_user('patient')
def slot_booking():
    posts = Hospitaldata.query.filter()

    if request.method == "POST":
        srfid = request.form.get('srfid')
        bedtype = request.form.get('bedtype')
        hcode = request.form.get('hcode').upper()
        spo2 = request.form.get('spo2')
        pname = request.form.get('pname')
        pphone = request.form.get('pphone')
        paddress = request.form.get('paddress')

        hos_data_exists = Hospitaldata.query.filter_by(hcode=hcode).first()
        patient_exists = Bookingpatient.query.filter_by(srfid=srfid).first()

        if current_user.srfid != srfid:
            flash("You cannot book slot for other account", "warning")
            return render_template("slotbooking.html", posts=posts)

        if not hos_data_exists:
            flash("Entered hospital code doesn't exist", "warning")
            return render_template("slotbooking.html", posts=posts)

        if patient_exists:
            flash(
                "You already have a bed booked, view Patient details page to view your booking", "warning")
            return render_template("slotbooking.html", posts=posts)

        beds = hos_data_exists.__dict__[bedtype]

        if beds <= 0:
            flash("No beds available", "danger")
            return render_template("slotbooking.html", posts=posts)

        db.session.query(Hospitaldata).filter_by(hcode=hcode).update({bedtype: beds - 1})
        new_book = Bookingpatient(srfid=srfid, bedtype=bedtype, hcode=hcode,
                             spo2=spo2, pname=pname, pphone=pphone, paddress=paddress)
        db.session.add(new_book)

        try:
            ''' Sending email - uncomment this section
            hos = Hospitaluser.query.filter_by(hcode=hcode).first()
            patient = Patient.query.filter_by(srfid=current_user.srfid).first()
            message = (
                "Thankyou for choosing us!\n\n" +
                "Bed booking was successful\n\n" +

                "Bed booked at:\n" +
                f"Hospital code: {hos.hcode}\n"
                f"Hospital Email: {hos.email}\n\n"

                "Bed booked by:\n" +
                f"Patient SRFID: {patient.srfid}\n"
                f"DOB: {patient.dob}\n"
                f"Email: {patient.email}\n\n"

                "Thankyou."
            )

            admin = get_admin()
            initiate_mail(admin)
            Mail(app).send_message('COVID CARE CENTRE',
                                    sender=admin.gmail,
                                    recipients=[hos.email, current_user.email],
                                    body=message
                                    )
            '''
            
            db.session.commit()
            flash("Your slot booking was successful. Kindly visit hospital for further procedure", "success")

        except:
            flash("Failed, Error occured while sending mail, hospital not added", "danger")

        return render_template("slotbooking.html", posts=posts)

    srfid = current_user.srfid
    patient_exists = Bookingpatient.query.filter_by(srfid=srfid).first()
    ispatient = not not patient_exists

    if ispatient: flash("You already have a bed booked, view Patient details page to view your booking", "warning")
    return render_template("slotbooking.html", posts=posts, ispatient=ispatient)


@app.route("/pdetails", methods=['GET', 'POST'])
@login_required
@make_sure_user('patient')
def pdetails():
    data = Bookingpatient.query.filter_by(srfid=current_user.srfid).first()
    return render_template("pdetails.html", data=data)


# Error handlers
@app.errorhandler(Exception)
def handle_generic_error(e):
    return redirect('/')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
