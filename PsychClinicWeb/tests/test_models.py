import warnings
warnings.filterwarnings("ignore")
import os
basedir = os.path.abspath(os.path.dirname(__file__))

from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.Model.models import User, Survey, Feelingspositive, Feelingsnegative, Thoughtspositive, Thoughtsnegative, Behaviormc, SituationList, Signature
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ROOT_PATH = '..//'+basedir


class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='john', firstname='John', lastname='Yate', email='john.yates@wsu.edu')
        u.set_password('covid')
        self.assertFalse(u.get_password('flu'))
        self.assertTrue(u.get_password('covid'))

    def test_password_hashing2(self):
        u = User(username='selinanguyen', firstname= 'Selina', lastname='Nguyen', email='selina@wsu.edu')
        u.set_password('1234')
        self.assertFalse(u.get_password('123'))
        self.assertTrue(u.get_password('1234'))

    def test_password_hashing3(self):
        u= User(username='Oni', firstname= 'Suhird', lastname='Giri', email='s.giri@wsu.edu')
        u.set_password('test1234')
        self.assertFalse(u.get_password('test'))
        self.assertTrue(u.get_password('test1234'))

    def test_password_hashing4(self):
        u= User(username='aaronluck', firstname= 'Aaron', lastname='Luckhardt', email='a.luck@wsu.edu')
        u.set_password('test#001')
        self.assertFalse(u.get_password('test'))
        self.assertTrue(u.get_password('test#001'))

    def test_survey(self):
        s=Survey(  thoughts_meaning_of_event = 'test3',  behaviors_description = 'test7' )
        self.assertTrue(s.behaviors_description=='test7')
        self.assertFalse(s.thoughts_meaning_of_event=='test10')

    def test_survey_user_relationship(self):
        u= User(username='aaronluck', firstname= 'Aaron', lastname='Luckhardt', email='a.luck@wsu.edu')
        u.set_password('test#001')
        s=Survey(user_id = u.id)
        self.assertTrue(s.user_id==u.id)
    
    def test_creating_admin_user(self):
        u = User(username='walt', firstname='walt', lastname='scott', email='walt.scott@wsu.edu',admin=1)
        u.set_password('1234')
        self.assertTrue(u.username =='walt')
        self.assertTrue(u.firstname =='walt')
        self.assertTrue(u.lastname =='scott')
        self.assertTrue(u.email =='walt.scott@wsu.edu')
        self.assertFalse(u.admin==0)
        self.assertTrue(u.admin==1)
        self.assertTrue(u.get_password('1234'))
    
    def test_positiveChoices_table(self):
        u= User(username='aaronluck', firstname= 'Aaron', lastname='Luckhardt', email='a.luck@wsu.edu')
       
        s=Survey(  user_id =u.id,thoughts_meaning_of_event = 'test3',  behaviors_description = 'test7' )
        self.assertTrue(s.user_id == u.id)
        fp = Feelingspositive(name = "Interested")
        tp = Thoughtspositive(name = "A burden has been lifted from my mind. A threat or harm has been removed from this situation. Things are working out after all.")
        behmc = Behaviormc(name  = "To connect, feel closer to someone, accepted/liked")

        s.feelings_pos.append(fp)
        s.thoughts_pos.append(tp)
        s.behaviors_mc.append(behmc)

        self.assertEqual(s.get_feelingspos()[0].name, "Interested")
        self.assertEqual(s.get_thoughtspos()[0].name, "A burden has been lifted from my mind. A threat or harm has been removed from this situation. Things are working out after all.")
        self.assertEqual(s.get_behaviors()[0].name, "To connect, feel closer to someone, accepted/liked")
    
    def test_negativeChoices_table(self):
        u= User(username='aaronluck', firstname= 'Aaron', lastname='Luckhardt', email='a.luck@wsu.edu')
        s=Survey(  user_id =u.id,thoughts_meaning_of_event = 'test3',  behaviors_description = 'test7' )
        self.assertTrue(s.user_id == u.id)

        fn = Feelingsnegative(name = "Bored, indifferent, apathetic")
        tn = Thoughtsnegative(name = "I don’t know whether I can handle what is happening. I feel threatened. I’m in trouble, and I might not be able to deal with it.")
        s.feelings_neg.append(fn)
        s.thoughts_neg.append(tn)
        self.assertEqual(s.get_feelingsneg()[0].name, "Bored, indifferent, apathetic")
        self.assertEqual(s.get_thoughtsneg()[0].name, "I don’t know whether I can handle what is happening. I feel threatened. I’m in trouble, and I might not be able to deal with it.")
    

    
    def test_signatureAndSituationListTable(self):
        u= User(username='aaronluck', firstname= 'Aaron', lastname='Luckhardt', email='a.luck@wsu.edu')
        db.session.add(u)
        db.session.commit()
        s = Signature(ifThen = "test if then", user_id = u.id )
        db.session.add(s)
        db.session.commit()

        sl = SituationList(signature_id = s.id, situation = "situation test")
        db.session.add(sl)
        db.session.commit()
        self.assertTrue(sl.signature_id == s.id)

    def test_signatureUserSurveyTable(self):
        u= User(username='aaronluck', firstname= 'Aaron', lastname='Luckhardt', email='a.luck@wsu.edu')
        db.session.add(u)
        db.session.commit()
        s = Signature(ifThen = "test if then", user_id = u.id )
        db.session.add(s)
        db.session.commit()
        self.assertTrue(s.user_id == u.id)
        
    def test_signatureAndSurveyTable(self):
        u= User(username='aaronluck', firstname= 'Aaron', lastname='Luckhardt', email='a.luck@wsu.edu')
        db.session.add(u)
        db.session.commit()
        s = Signature(ifThen = "test if then", user_id = u.id )
        db.session.add(s)
        db.session.commit()
        survey=Survey(  user_id =u.id,thoughts_meaning_of_event = 'test3',  behaviors_description = 'test7', signature_id = s.id )
      
        db.session.add(survey)
        db.session.commit()
        self.assertTrue(survey.signature_id == s.id)
        
        

        


       
       

 