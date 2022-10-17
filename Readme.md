# Cov19beds

## Description

- **Cov19beds** is a fullstack website that connects the hospitals and patients, making bed slot booking seamless.

- **Hospitals** can add / edit / delete the data of their vacant beds which will be visible to anyone visiting the website. Hospitals can view the patient bookings done for their hospital.

- **Patients** can signup and login to the website, and can book their desired beds from available beds, view available beds and their booking details.

- **Admin** is responsible for verifying the hospitals requesting for registration to website and can register respective hospital on successful verification. Admin can also view the triggered events, these are the events recorded when there is a change in any hospital data.

- Besides this, website comes with a beautiful and user-friendly UI, home page shows the counts of registered hospitals, patients and total beds of different type and from different hospitals.

## Tools used

### Development

- **Frontend:** [HTML5](https://developer.mozilla.org/en-US/docs/Glossary/HTML5), [CSS3](https://developer.mozilla.org/en-US/docs/Web/CSS), [Boostrap](https://getbootstrap.com/docs/5.0/getting-started/introduction/) and [Javascript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

- **Backend**

  - [Python](https://www.python.org/) - A high level interpreted, object-oriented programming language, that is easy to code and provides wide range of packages for different tasks.
  - [Flask](https://flask.palletsprojects.com/en/2.2.x/) - A python module and a web application framework that lets you create web applications easily by handling low-level details like protocol and thread management by itself.
  - [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/) - Flask-SQLAlchemy is an extension for Flask that adds support for SQLAlchemy to your application. It simplifies using SQLAlchemy with Flask by setting up common objects and patterns for using those objects, such as a session tied to each web request, models, and engines.
  - [Flask-Login](https://flask-login.readthedocs.io/en/latest/) - Flask-Login provides user session management for Flask. It handles the common tasks of logging in, logging out, and remembering your users’ sessions over extended periods of time.
  - [Flask-Mail](https://flask-mail.readthedocs.io/en/latest/) - The Flask-Mail extension provides a simple interface to set up SMTP with your Flask application and to send messages from your views and scripts.

- **Database**
  - [MariaDB](https://mariadb.org/) - MariaDB Server is an open source relational database made by the original developers of MySQL. MariaDB is a fork of MySQL that provides all the features of MySQL along with some additional features.

### Deployment

- [Gunicorn](https://gunicorn.org/) - Gunicorn or 'Green Unicorn' is a Python WSGI HTTP Server for UNIX. Gunicorn is compatible with various web frameworks, flask is one of them.
- [Nginx](https://www.nginx.com/) - NGINX is open source software for web serving, reverse proxying, caching, load balancing, media streaming, and more.
- [Amazon EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html) - AWS is a cloud computing platform that provides a wide variety of services. Amazon EC2 is one of those services that allows you to create a virtual machine with your desired Operating System and hardware configuration which can be used as a server.
<!--

## Development

## Deployment -->

## How to install and run the project

**Prerequisites**

1. [Python & pip](https://www.python.org/)

**Installation**

1. Download or clone the project. Use command `git clone "https://github.com/Vedant2254/Cov-19-beds.git"` to clone.

1. `cd` into the root folder of project.

1. Installtion of MySQL database and PhpMyAdmin

   - Before we get into the installation of project, we'll first need to install mysql and phpmyadmin so that we can use and configure our database.
   - If you are on windows, installation is pretty simple, you just need to install [Apache XAMPP](https://www.apachefriends.org/)
   - If you are on linux, you can either use [Apache XAMPP](https://www.apachefriends.org/), or advanced users can install the LAMP stack (Linux, Apache, MySQL, PHP) instead, for better control over database. Here are some blogs explaining LAMP installation for [Ubuntu](https://www.tecmint.com/install-lamp-with-phpmyadmin-in-ubuntu-20-04/), [OpenSUSE](https://en.opensuse.org/SDB:LAMP_setup), [Arch Linux](https://www.tecmint.com/install-lamp-in-arch-linux/), search google for your distro... 😅

1. Setup **Local MySQL database**

   - Once you are done with the installation of MySQL on your system, follow the following steps to setup database for project and to setup user to handle the database.
   - Create database named `covid`. You can either use PhpMyAdmin web-based GUI or following query `CREATE DATABASE covid`.
   - Inside project directory you will find a file named `covid.sql`, you need to import this file to add required tables and triggers in your database. Again, you can either do it using GUI or you can use command `mysql -u <username> -p covid < covid.sql`, replace `<username>` with username of database user.
   - At this point you are done with the setup of database.
   - Now you can either use the existing user to connect to the database from flask application or you can create a new user with all privileges over `covid` database. _It's recommended to create a dedicated user with privileges only on covid database._
   - To create a new user follow the following steps -

     - Create user with username `coviduser` and `coviduser123` as password
       <br />Query: `CREATE USER 'coviduser'@localhost IDENTIFIED BY 'coviduser123';`

     - Grant all privileges to `coviduser` on database `covid`
       <br />Query: `GRANT ALL PRIVILEGES ON covid.* TO 'coviduser'@localhost;`

1. Create python virtual environment and install dependencies

   - _It is not mandatory to run project in a virtual environment but it is always recommended to have a virtual environment for each project. Virtual environment helps isolate the the python enviornment of one project from another and from operating system, this helps avoid the possible clashes between installed packages that may happen if all projects are run into same python environment._
   - Run command `pip install virtualenv` to install virtualenv package.
   - Run command `virtualenv env` to create a virtual environment, a folder named `env` is created in the project directory.
   - To activate the virtual environment run command `source env/bin/activate` on linux, if on windows run `env/Scripts/activate`.
   - Now you should see something like `(env)` at start of terminal indicating that virtual environment is active.
   - After virtual environment is setup it's time to install the required dependencies in this environment, project contains a `requirements.txt` file, just run command `pip install -r requirements.txt` to install all the requirements.

1. Setup configuration file **config.json** -

   - Rename the file `config-sample.json` found in the root folder of project to `config.json`.
   - Replace `<user>` and `<password>` in `mysql+pymysql://<user>:<password>@localhost/covid` to user and password of your database user. _If you have created a user while setting up MySQL database with same username and password as illustrated above, your config file shoud look like this.._
     ```
     {
         "database": {
             "uri": "mysql+pymysql://coviduser:coviduser123@localhost/covid"
         }
     }
     ```

1. Insert admin into the database with `insertadmin.py`

   - Inside `insertadmin.py` you'll see the following lines of code, you need to make changes as per your requirement.
     ```
     # ------------------------- Make changes below ---------------------------
     username = 'admin'
     password = 'admin'
     gmail = "your_gmail"
     gpassword = 'app_password_of_your_gmail'
     # ------------------------- Make changes above ---------------------------
     ```
   - These are login credentials for admin. Set the desired values of `username` and `password`, you can keep `gmail` and `gpassword` as it is to skip them for now.
   - Enable emailing (Optional)
     - _This is an optional step, follow it if you want application to send an email to the hospital when admin registers their hospital on website. It is important to notify hospitals about their registration and login credentials, but just for the sake of project you can skip these steps, project would still work seamlessly_.
     - To enable sending email set the value of `gmail` to your(admin) email address. This account will be used to send emails.
     - Now to authenticate the application for sending email through above provided gmail we need to provide password for gmail. _Password that you use for logging in to your account won't work, you need to use_ **App Passwords** _feature of google for authenticating our application._
     - To enable and create **App passwords** visit [My Google Account](https://myaccount.google.com/), enable **2-Step Verication** for your google account, now you should be able to see **App Passwords** below 2-Step Verification.
     - Inside **App Passwords** select the app as **Mail** and device as **Other (Custom)**, name the app whatever you want (name is just for you, so that you can recognize it later) and click on **GENERATE**. You'll see a 16-character password, copy it and save it securely because you may not be able to view it again, change value of `gpassword` in `insertadmin.py` to this 16-character password.
     - Uncomment the commented lines in `add_hospital_user()` function in `app.py` file, the corresponding code is for sending mail to the hospital user.
     - For more clarification, watch [this video](https://youtu.be/Jp9B0rY6Fxk) by Nick Janetakis on how to enable App passwords in google account.
   - Now, just run the script and admin with be inserted into the database.

1. Ready to launch the website, run command `flask run` and visit [localhost:5000](http://localhost:5000/)

## Understanding the functionalities of application

- The application have 3 types of users, **Admin**, **Hospital**, **Patient**.

- **Admin can -**

  - Register hospitals to database
  - View the triggered events

- **Hospitals can -**

  - View patient bookings for their hospital
  - Add / Edit / Delete hospital data

- **Patient can -**

  - View available beds
  - View their patient details and booking details
  - Book a bed

## Screenshots

<img src="./screenshots/home.png" width="97%"></img>

<img src="./screenshots/addhos.png" width="32%"></img>
<img src="./screenshots/patsignup.png" width="32%"></img>
<img src="./screenshots/addhosdata.png" width="32%"></img>

<img src="./screenshots/bookbed.png" width="32%"></img>
<img src="./screenshots/bookings.png" width="32%"></img>
<img src="./screenshots/trigevents.png" width="32%"></img>

## Brief of tools usage

### Flask

- Basic Flask application structure and serving using development server.
- Creating routes using `@app.route()` decorator.
- Jinja2 template engine for creating dynamic HTML pages.
- Template inheritance, great way to reduce redundancy in templates (html files).

### Flask-SQLAlchemy

- Connecting to a database using `flask_sqlalchemy`.
- Creating database models.
- Performing CRUD operations on database from flask application.

### Flask-Login and Flask-Mail

- Using `LoginManger()` class from `flask_login` to manage user login, logout and sessions.
- Using decorator `@login_manager.user_loader()` for loading user on recieving the request, `@login_required` decorator to protect the routes from anonymous users, and functions like `login_user()` and `logout_user()`.
- Setting up `flask_mail` and sending a message from application.

### Hashing and Encrypting passwords

- As application includes saving passwords to database, it's important to store the passwords securely, here hashing needs to be done.
- `generate_password_hash()` and `check_password_hash()` functions from `werkzeug.security` are used to generate password hashes and to compare the incoming string with stored hash respectively.
- Some passwords like the password of admin's gmail needs to be restored when required, such passwords can't be hashed as hashing is a one-way process, extracting original text from hash is nearly impossible.
- For such password, encryption is used, `Fernet` from `cryptography.fernet` is used for encrypting and decrypting password. A secret key is used to encrypt the password, this encrypted password is then stored into the database. Whenever required, encrypted password is queried from database, it is decrypted using the same secret key to get back the plain text password.

### MariaDB / MySQL database

- Database is at the core of this application.
- Basic CRUD operations are performed on the database for storing, and manipulating hospital and patient data.
- Triggers are setup on `hospitaldata` table to record events of change in data.

### Deployment using Gunicorn and Nginx

- Deployment is as important as development. Development server that we run using `flask run` is good for development but not appropriate for deploying the application to production.
- So, we use a [WSGI](https://wsgi.readthedocs.io/en/latest/what.html) compatible production server [Gunicorn](https://gunicorn.org/) for deploying the website, which can spawn multiple workers, is fast and secure.
- About [Nginx](https://www.nginx.com/), it's not mandatory to have Nginx, but there are some strong advantages of using Nginx which makes it a must have component. Some of the advantages of using nginx include -
  - Nginx can act as a reverse proxy.
  - It can be used for serving static files much more efficiently.
  - Using nginx you can run multiple applications on a single server.
  - It can also act as a load balancer
- In this project, Nginx is used as a reverse proxy, using reverse proxy helps in completely isolating the original application from the enduser adding an extra layer of security as the application can now be served from behind the firewall. Nginx forwards the incoming requests from browser to gunicorn and forwards response from gunicorn to the browser.

## Potential improvements

- Currently all the errors are handled using single error handler, if some error occurs in the application user is redirected to the home page. Error handling can be modified so that user can be notified about the exact error.

- Currently hospitals need to apply for their registration through some external means, this functionality can also be added to the application itself. We can have a route for hospitals to request for their registration, where they can upload the required details and documents for verification.
