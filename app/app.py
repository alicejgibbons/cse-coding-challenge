import os
import json
import requests
from flask import Flask, flash, request, redirect, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from azure.storage.blob import BlockBlobService
from werkzeug.utils import secure_filename

APP = Flask(__name__)
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://%s:%s@%s/%s' % (
    # ARGS.dbuser, ARGS.dbpass, ARGS.dbhost, ARGS.dbname
    os.environ['DBUSER'], os.environ['DBPASS'], os.environ['DBHOST'], os.environ['DBNAME']
)

UPLOAD_FOLDER = './employee_photos'
APP.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])
APP.secret_key = 'super secret key'
APP.config['SESSION_TYPE'] = 'filesystem'

# initialize the database connection
DB = SQLAlchemy(APP)

# initialize database migration management
MIGRATE = Migrate(APP, DB)

from models import *

with open('settings.json') as f:
    settings = json.load(f)

params_detect = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender'
}

header_detect = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': settings['cog_face_key']
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@APP.route('/')
def view_registered_employees():
    employees = Employee.query.all()
    return render_template('employee_list.html', employees=employees)


@APP.route('/register', methods = ['GET'])
def view_registration_form():
    return render_template('employee_registration.html')


@APP.route('/register', methods = ['POST'])
def register_employee():
    first_name = request.form.get('firstname')
    last_name = request.form.get('lastname')
    dept = request.form.get('dept')

    if 'photo' not in request.files:
        print('No file uploaded.')
        flash('Please upload valid employee photo.')
        return redirect(request.url)

    file = request.files['photo']

    if file.filename == '':
        print('No file uploaded.')
        flash('Please upload valid employee photo.')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        file_name = secure_filename(file.filename)
        print("Filename is " + file_name)
        # Save file locally
        local_photo_path = os.path.join(APP.config['UPLOAD_FOLDER'], file_name)
        file.save(local_photo_path)

        # Run face detection with the Face API here
        img = open(os.path.expanduser(local_photo_path),'rb')
        response = requests.post(
            settings['face_url'] + 'detect',
            data = img,
            headers = header_detect,
            params = params_detect
        )

        # Check if no faces are found in the photo
        if response.text:
            result = response.json()
            print("Face(s) detected in photo.")
        else:
            print("Error while doing face detection, Exiting... \n " + str(response))
            flash('No faces in photo detected. Please upload valid employee photo.')
            return redirect(request.url)
        
        # If multiple faces are found in the photo, exit
        face_ids = [each['faceId'] for each in result]

        if len(face_ids) > 1:
            print("Multiple faces detected in photo.")
            flash('Multiple faces detected in photo. Please upload valid employee photo.')
            return redirect(request.url)

        # Establish blob service connection
        block_blob_service = BlockBlobService(settings['storage_name'], settings['storage_key'])

        # Upload the created file, use local_file_name for the blob name
        block_blob_service.create_blob_from_path(settings['container_name'], file_name, local_photo_path)

        # Get the blob url 
        photo_url = block_blob_service.make_blob_url(settings['container_name'], file_name)
        print("Blob photo url is: " + photo_url)

        # store the blob URL in the DB
        employee = Employee(first_name, last_name, dept, photo_url)
        DB.session.add(employee)
        DB.session.commit()

        return render_template('employee_confirmation.html',
            firstname=first_name, lastname=last_name)


# Convert width height to a point in a rectangle
def getRectangle(faceDictionary):
    rect = faceDictionary['faceRectangle']
    left = rect['left']
    top = rect['top']
    bottom = left + rect['height']
    right = top + rect['width']
    return ((left, top), (bottom, right))

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
        empid=empid, firstname=employee.firstname, lastname=employee.lastname, dept=employee.dept, photourl=employee.photourl)


if __name__ == "__main__":
    APP.debug = True
    APP.run()
