import mongoengine
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from app import db
from app import login
from mongoengine import Document, StringField, EmailField, IntField, ReferenceField, ListField, DateTimeField

@login.user_loader
def load_user(id):
    # searches for user with specific id, find first result in query
    return User.objects(id=id).first()

# Creates models using Flask-SQLAlchemy
# Clases inherit from db.Model which is a base class provided by SQL

## Changing to Mongo --------------------------------
class Thoughtspositive(Document):
    name = StringField(max_length=200)

    def __repr__(self):
        return f'<Name: {self.name} Thoughts Positive>'

class Thoughtsnegative(Document):
    name = StringField(max_length=200)

    def __repr__(self):
        return f'<ID: {self.id} Thoughts Negative {self.name}>'


class Feelingspositive(Document):
    name = StringField(max_length=200)

    def __repr__(self):
        return f'<ID: {self.id} Feelings Positive {self.name}>'

class Feelingsnegative(Document):
    name = StringField(max_length=200)

    def __repr__(self):
        return f'<ID: {self.id} Feelings Negative {self.name}>'

class Behaviormc(Document):
    name = StringField(max_length=200)

    def __repr__(self):
        return f'<ID: {self.id} Behavior MC {self.name}>'

# change to mongo
class User(Document, UserMixin):
    username = StringField(required=True, max_length=64, unique=True)
    firstname = StringField(max_length=64)
    lastname = StringField(max_length=64)
    email = EmailField(required=True, unique=True)
    password_hash = StringField(max_length=128)
    admin = IntField(default=0)
    survey = ReferenceField('Survey')
    signature = ReferenceField('Signature')

    def repr(self):
        return '<ID: {} Username: {}>'.format(self.id,self.username)

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def get_password(self,password):
        return check_password_hash(self.password_hash,password)


class Survey(Document):
    # reference field is referencing a differetn document in User collection
    signature = ReferenceField('Signature')
    user = ReferenceField('User')
    timestamp = DateTimeField(default=datetime.utcnow)

    thoughts_pos = ListField(StringField(max_length=50))
    thoughts_neg = ListField(StringField(max_length=50))
    feelings_pos = ListField(StringField(max_length=50))
    feelings_neg = ListField(StringField(max_length=50))
    behaviors_mc = ListField(StringField(max_length=50))

    situation = StringField(max_length=300)
    what_happened = StringField(max_length=300)
    thoughts_meaning_of_event = StringField(max_length=500)
    thoughts_summary = StringField(max_length=500)
    behaviors_description = StringField(max_length=500)
    behaviors_outcome = StringField(max_length=500)

    def save_thoughts(self, thoughts_pos, thoughts_neg, thoughts_meaning_of_event):
        self.thoughts_pos = thoughts_pos
        self.thoughts_neg = thoughts_neg
        self.thoughts_meaning_of_event = thoughts_meaning_of_event

    # Save the survey
        self.save()

    def save_feelings(self, feelings_pos, feelings_neg):
        self.feelings_neg = feelings_neg
        self.feelings_pos = feelings_pos
        self.save()

    def save_behaviors_negative(self, behaviors_mc, behaviors_description, behaviors_outcome):
        self.behaviors_mc = behaviors_mc
        self.behaviors_description = behaviors_description
        self.behaviors_outcome = behaviors_outcome
        self.save()

    def save_behaviors_positive(self, behaviors_mc, behaviors_description):
        self.behaviors_mc = behaviors_mc
        self.behaviors_description = behaviors_description
        self.save()

    def get_thoughtspos(self):
        return Thoughtspositive.objects(id__in=self.thoughts_pos)
    def get_thoughtsneg(self):
        return Thoughtsnegative.objects(id__in=self.thoughts_neg)
    def get_feelingspos(self):
        return Feelingspositive.objects(id__in=self.feelings_pos)
    def get_feelingsneg(self):
        return Feelingsnegative.objects(id__in=self.feelings_neg)
    def get_behaviors(self):
        return Behaviormc.objects(id__in=self.behaviors_mc)
    def get_situationList(self):
        return self.situationlist
    def get_thoughtspos2(self):
        test =[]
        for t in self.thoughts_pos:
            test.append(t.thoughtspositive_id)



class SituationList(Document):
    signature = ReferenceField('Signature')
    situation = StringField(max_length=300)

class Signature(Document):
    ifThen = StringField(max_length=300)
    user = ReferenceField('User')
    survey = ReferenceField('Survey', reverse_delete_rule=mongoengine.CASCADE)
    situationList = ListField(ReferenceField('SituationList', reverse_delete_rule=mongoengine.CASCADE))
