import os

from flask import Flask, request, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://%s:%s@%s/%s' % (
    # ARGS.dbuser, ARGS.dbpass, ARGS.dbhost, ARGS.dbname
    os.environ['DBUSER'], os.environ['DBPASS'], os.environ['DBHOST'], os.environ['DBNAME']
)

# initialize the database connection
DB = SQLAlchemy(APP)

# initialize database migration management
MIGRATE = Migrate(APP, DB)

from models import *


@APP.route('/')
def view_registered_employees():
    employees = Employee.query.all()
    return render_template('employee_list.html', employees=employees)


@APP.route('/register', methods = ['GET'])
def view_registration_form():
    return render_template('employee_registration.html')


@APP.route('/register', methods = ['POST'])
def register_employee():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    dept = request.form.get('dept')

    employee = Employee(firstname, lastname, dept)
    DB.session.add(employee)
    DB.session.commit()

    return render_template('employee_confirmation.html',
        firstname=firstname, lastname=lastname, dept=dept)
    

@APP.route('/search', methods = ['GET'])
def view_employee_search_form():
    return render_template('employee_search.html')


@APP.route('/search', methods = ['POST'])
def search_employee():
    empid = request.form.get('empid')
    print("inside search employee with empid = " + empid)

    #query db for employee with id=empid
    employee = Employee.query.filter(Employee.id == empid).one()
    print("Employee returned is named " + str(employee.firstname))

    return render_template('employee_details.html',
        empid=empid, firstname=employee.firstname, lastname=employee.lastname, dept=employee.dept)
