from app import DB

class Employee(DB.Model):
    """Simple database model to track employees."""
    
    __tablename__ = 'employees'
    id = DB.Column(DB.Integer, primary_key=True)
    firstname = DB.Column(DB.String(80))
    lastname = DB.Column(DB.String(80))
    dept = DB.Column(DB.String(120))

    def __init__(self, firstname=None, lastname=None, dept=None):
        #id here???????????
        self.firstname = firstname
        self.lastname = lastname
        self.dept = dept