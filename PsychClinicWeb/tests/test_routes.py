import os
import pytest
from app import create_app, db
from app.Model.models import User, Survey, Signature
from config import Config
from flask import url_for

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'bad-bad-key'
    WTF_CSRF_ENABLED = False
    DEBUG = True
    TESTING = True



@pytest.fixture(scope='module')
def test_client():
    # create the flask application ; configure the app for tests
    flask_app = create_app(config_class=TestConfig)

    db.init_app(flask_app)
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()
 
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()
 
    yield  testing_client 
    # this is where the testing happens!
 
    ctx.pop()

def new_user(uname, uemail,passwd, ufirst, ulast,uadmin):
    user = User(username=uname, email=uemail, firstname=ufirst, lastname=ulast, admin=uadmin)
    user.set_password(passwd)
    return user


@pytest.fixture
def init_database():
    # Create the database and the database table
    db.create_all()
    #add a user    
    user1 = new_user(uname='selinanguyen', uemail='selina@wsu.edu',passwd='1234', ufirst = 'selina', ulast = 'nguyen',uadmin=0)
    admin_user = new_user(uname='walt', uemail='waltwsu.edu',passwd='1234', ufirst = 'Walt', ulast = 'Scott',uadmin=1)

    # new_survey = Survey(user_id=user1.id,situation = "hellotest")
    # Insert user data
    db.session.add(user1)
    db.session.add(admin_user)
    # db.session.add(new_survey)
    # Commit the changes for the users
    db.session.commit()

    yield  # this is where the testing happens!

    db.drop_all()

def test_register_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is requested (GET)
    THEN check that the response is valid
    """
    # Create a test client using the Flask application configured for testing
    response = test_client.get('/register')
    assert response.status_code == 200
    assert b"Register" in response.data

def test_register(test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' form is submitted (POST)
    THEN check that the response is valid and the database is updated correctly
    """
    # Create a test client using the Flask application configured for testing
    response = test_client.post('/register', 
                          data=dict(username='johnh',firstname = 'John', lastname = 'Hancock' , email='john@wsu.edu',password="bad-bad-password",password2="bad-bad-password",),
                          follow_redirects = True)
    assert response.status_code == 200

    s = db.session.query(User).filter(User.username=='johnh')
    assert s.first().email == 'john@wsu.edu'
    assert s.first().admin == 0
    assert s.count() == 1
    assert b"Sign In" in response.data   
    assert b"Please log in to access this page." in response.data

def test_admin_register(test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/registerAdmin' form is submitted (POST)
    THEN check that the response is valid and the database is updated correctly
    with the corresponding admin user.
    """
    response = test_client.post('/registerAdmin', 
                          data=dict(adminCode=1234,username='aaronl',firstname = 'Aaron', lastname = 'LuckHardt' , email='aaron@wsu.edu',password="test123",password2="test123",),
                          follow_redirects = True)
    assert response.status_code == 200

    s = db.session.query(User).filter(User.username=='aaronl')
    assert s.first().email == 'aaron@wsu.edu'
    assert s.first().admin == 1
    assert s.count() == 1
    assert b"Sign In" in response.data   
    assert b"Please log in to access this page." in response.data


def test_invalidlogin(test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST) with wrong credentials
    THEN check that the response is valid and login is refused 
    """
    response = test_client.post('/login', 
                          data=dict(username='selinanguyen', password='12345',remember_me=False),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data

def test_login_logout(request,test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST) with correct user credentials
    THEN check that the response is valid and login is succesfull 
    """
    response = test_client.post('/login', 
                          data=dict(username='selinanguyen', password='1234',remember_me=False),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Welcome to the Mindful Portal!" in response.data

    response = test_client.get('/logout',
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Sign In" in response.data

def test_admin_login_logout(request,test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST) with correct admin credentials
    THEN check that the response is valid and login is succesfull 
    """
    response = test_client.post('/login', 
                          data=dict(username='walt', password='1234',remember_me=False),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Welcome to the Admin Mindful Portal!" in response.data


    response = test_client.get('/logout',
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Sign In" in response.data

def test_admin_user_query(request,test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST) with correct admin credentials
    THEN check that the response is valid and login is succesfull. Also
    check if user profiles are able for admin to view.
    """
    response = test_client.post('/login', 
                          data=dict(username='walt', password='1234',remember_me=False),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Welcome to the Admin Mindful Portal!" in response.data
   
    assert b"Look at selina's surveys" in response.data
    test_user = db.session.query(User).filter(User.username=='selinanguyen')
    response = test_client.get('/userSurveys/'+str(test_user.first().id),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Below are all the If Then Signatures for selina nguyen" in response.data

    response = test_client.get('/logout',
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Sign In" in response.data

def test_admin_qsort(request,test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' form is submitted (POST) with correct admin credentials
    THEN check that the response is valid and login is succesfull. 
    THEN check that the qsort route works
    THEN submit a qsort form
    THEN check if the form is created for a user
    """
    response = test_client.post('/login', 
                          data=dict(username='walt', password='1234',remember_me=False),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Welcome to the Admin Mindful Portal!" in response.data
    response = test_client.get('/qsort',
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"User Qsort Entry" in response.data

    response = test_client.post('/qsort',
                            data = dict(user_id = 1,choice='True', ifthenSignature = 'this is a test', prototypicalSituation = 'test2' ),
                            follow_redirects = True)
    assert response.status_code == 200
    assert b"Welcome to the Admin Mindful Portal!" in response.data
    test_survey =  db.session.query(Survey).filter(Survey.user_id==1) 
    test_sig = db.session.query(Signature).filter(Signature.id == test_survey.first().signature_id)
    assert test_survey.first().user_id==1
    assert test_sig.first().ifThen == "this is a test"
    response = test_client.get('/logout',
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Sign In" in response.data


    
    

def test_survey(request,test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/situation_cateogry' form is submitted (POST) with correct credentials
    THEN check that user is redirected to '/what_happened' with correct positive or negative inputs.
    Continue with survey routes till user is redirected to '/index' and validate is survey was saved.
    Will also check if survey shows up on Admin end.
    """
    response = test_client.post('/login', 
                          data=dict(username='selinanguyen', password='1234',remember_me=False),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Welcome to the Mindful Portal!" in response.data

    response = test_client.get('/situation_category',
                          follow_redirects = True)
    assert response.status_code == 200
    
    test_user = db.session.query(User).filter(User.username=='selinanguyen')
    response = test_client.post('/situation_category', data=dict(choice='True'),
                          follow_redirects = True)
    assert response.status_code == 200    
    
    
    assert b"What Happened?" in response.data
   
    test_survey =  db.session.query(Survey).filter(Survey.user_id==test_user.first().id) 
    assert test_user.first().id  == test_survey.first().user_id

    response = test_client.post('/what_happened/'+str(test_user.first().id)+'/True/0',data=dict(back =0, answer = 'test'),
                          follow_redirects = True)
    assert b"Thoughts" in response.data    

    response = test_client.post('/thoughts/'+str(test_user.first().id)+'/True/0',data=dict(back=0),
                          follow_redirects = True)  
    assert b"Feelings" in response.data      

    response = test_client.post('/feelings/'+str(test_user.first().id)+'/True/0',
                          follow_redirects = True)  
    assert b"Behavior" in response.data       

    response = test_client.post('/behavior/'+str(test_user.first().id)+'/True/0',data=dict(),
                          follow_redirects = True)  

    assert b"Sorting" in response.data

    response = test_client.get('/logout',
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Sign In" in response.data





def back_button_test(request, test_client, init_database):
    response = test_client.post('/login', 
                          data=dict(username='lol', password='123',remember_me=False),
                          follow_redirects = True)
    assert response.status_code == 200
    assert b"Welcome to the Mindful Portal!" in response.data

    response = test_client.get('/situation_category', follow_redirects=True)
    assert response.status_code == 200
    assert b"Situation Category" in response.data

    test_user = db.session.query(User).filter(User.username=='lol').first()
    response = test_client.post('/situation_category', data=dict(positive=True), follow_redirects=True)
    assert response.status_code == 200
    assert b"What Happened?" in response.data

    response = test_client.post('/what_happened/'+str(test_user.first().id)+'/True', data=dict(back='1'), follow_redirects=True)
    assert response.status_code == 200
    assert b"Situation Category" in response.data

    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign In" in response.data

# Test new options
    
def test_information_page(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/Information' page is requested
    THEN check that the response is valid
    """
    # Log in as a user (change the username and password accordingly)
    response = test_client.post('/login', 
                          data=dict(username='selinanguyen', password='1234',remember_me=False),
                          follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome to the Mindful Portal!" in response.data

    # Access the 'Information' page
    response = test_client.get('/Information', follow_redirects=True)
    assert response.status_code == 200
    assert b"Information Page Content" in response.data  # Update with the actual content on the Information page

    # Log out
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign In" in response.data

def test_new_situation_page(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/New Situation' page is requested
    THEN check that the response is valid
    """
    # Log in as a user (change the username and password accordingly)
    response = test_client.post('/login', 
                          data=dict(username='selinanguyen', password='1234',remember_me=False),
                          follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome to the Mindful Portal!" in response.data

    # Access the 'New Situation' page
    response = test_client.get('/New Situation', follow_redirects=True)
    assert response.status_code == 200
    assert b"New Situation Page Content" in response.data  # Update with the actual content on the Information page

    # Log out
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign In" in response.data

def test_past_situation_categories_page(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/Past Situations' page is requested
    THEN check that the response is valid
    """
    # Log in as a user (change the username and password accordingly)
    response = test_client.post('/login', 
                          data=dict(username='selinanguyen', password='1234',remember_me=False),
                          follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome to the Mindful Portal!" in response.data

    # Access the 'Past Situations Categories' page
    response = test_client.get('/Past Situations Categories', follow_redirects=True)
    assert response.status_code == 200
    assert b"Past Situations Categories Page Content" in response.data  # Update with the actual content on the Information page

    # Log out
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign In" in response.data

def test_enter_pica_results_page(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/Enter PICA Results(If completed)' page is requested
    THEN check that the response is valid
    """
    # Log in as a user (change the username and password accordingly)
    response = test_client.post('/login', 
                          data=dict(username='selinanguyen', password='1234',remember_me=False),
                          follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome to the Mindful Portal!" in response.data

    # Access the 'Enter PICA Results(If completed)' page
    response = test_client.get('/Enter PICA Results(If completed)', follow_redirects=True)
    assert response.status_code == 200
    assert b"Enter PICA Results(If completed) Page Content" in response.data  # Update with the actual content on the Information page

    # Log out
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign In" in response.data

def test_search_page(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/Search' page is requested
    THEN check that the response is valid
    """
    # Log in as a user (change the username and password accordingly)
    response = test_client.post('/login', 
                          data=dict(username='selinanguyen', password='1234',remember_me=False),
                          follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome to the Mindful Portal!" in response.data

    # Access the 'Search' page
    response = test_client.get('/Search', follow_redirects=True)
    assert response.status_code == 200
    assert b"Search Page Content" in response.data  # Update with the actual content on the Information page

    # Log out
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Sign In" in response.data
