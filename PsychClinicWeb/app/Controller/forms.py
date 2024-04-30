from flask_mongoengine.wtf.fields import QuerySetSelectMultipleField
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import widgets
from wtforms import StringField, SubmitField, SelectField, TextAreaField, RadioField
from wtforms.fields.core import BooleanField, SelectMultipleField
from wtforms.validators import  DataRequired, Length
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
from app.Model.models import Thoughtspositive, Thoughtsnegative, Feelingspositive, Feelingsnegative, Behaviormc
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, SelectMultipleField, widgets


def get_thoughtspos():
    return Thoughtspositive.objects.all()

def get_thoughtnamepos(theThought):
    return theThought.name

def get_thoughtsneg():
    return Thoughtsnegative.objects.all()

def get_thoughtnameneg(theThought):
    return theThought.name

def get_feelingspos():
    return Feelingspositive.objects.all()

def get_feelingnamepos(theFeeling):
    return theFeeling.name

def get_feelingsneg():
    return Feelingsnegative.objects.all()

def get_feelingnameneg(theFeeling):
    return theFeeling.name

def get_behavior():
    return Behaviormc.objects.all()

def get_behaviorname(theBehavior):
    return theBehavior.name


class SituationForm(FlaskForm):
    choice = RadioField('Think about the different situations/events/happenings you experienced today and identify a situation in which you experienced positive or negative feelings. For this situation, did you experience mostly positive or negative feelings?', choices=[('True','Mostly positive feelings'),('False','Mostly negative feelings')])
    submit = SubmitField('Submit')


class WhatHappened(FlaskForm):
    answer = TextAreaField('What happened? In one or two sentences, briefly describe the event, what happened in the situation? Don’t include your interpretations, feelings, etc. Just describe objectively what happened (e.g., Someone I\'m interested in asked if I wanted to go with them to a party).')
    submit = SubmitField('Submit')

class Thoughts(FlaskForm):
    meaning_of_event = TextAreaField('When this event happened, what thoughts and/or image went through your mind? How did you interpret the event? That is, what did the event mean to you?')
    # query document in mongo, query set specifies the set of documents to be queried
    thought_pos = SelectMultipleField(
        'Positive Thoughts',
        choices=[],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )

    thought_neg = SelectMultipleField(
        'Negative Thoughts',
        choices=[],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )

    submit = SubmitField('Submit')


class Feelings(FlaskForm):
    feelings_pos = SelectMultipleField(
        'Positive Feelings',
        choices=[],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )

    feelings_neg = SelectMultipleField(
        'Negative Feelings',
        choices=[],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )

    submit = SubmitField('Submit')

class Behavior(FlaskForm):
    description = TextAreaField('Describe what you did--what you said, or how you acted--that contributed to this situation being a mostly positive situation for you.')
    outcome = TextAreaField('Describe specifically how you would’ve wanted the situation to come out for you, your desired outcome?  In thinking about this, be sure to identify a desired outcome that is realistic, under your control, attainable:')
    behaviors_mc = SelectMultipleField(
        'Behavior MC',
        choices=[],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )
    submit = SubmitField('Submit')

class IfThenSiganture(FlaskForm):
    ifthen = TextAreaField('If then Siganture')
    submit = SubmitField('Submit')

class AdminQsortForm(FlaskForm):
    user_id=StringField("User ID",validators=[DataRequired()])
    choice = RadioField('Positive or Negative Situation', choices=[('True','Mostly positive feelings'),('False','Mostly negative feelings')])
    ifthenSignature = TextAreaField('If-then Signature Title:', validators=[DataRequired()])
    prototypicalSituation = TextAreaField('Prototypical Situation', validators=[DataRequired()])
    situationList = TextAreaField('Situation List')
    protoThought = TextAreaField('Prototypical Thought')

    thought_pos = SelectMultipleField(
        'Positive Thoughts',
        choices=[],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )

    thought_neg = SelectMultipleField(
        'Negative Thoughts',
        choices=[],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )

    feelings_pos = SelectMultipleField(
        'Positive Feelings',
        choices=[],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )

    feelings_neg = SelectMultipleField(
        'Negative Feelings',
        choices=[],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )

    protoBehavior = TextAreaField('Prototypical Behavior')
    protoGoal = TextAreaField('Prototypical Goal')

    behavior_mc = SelectMultipleField(
        'Behavior MC',
        choices=[],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput()
    )
    submit = SubmitField('Submit')

class SortingForm(FlaskForm):
    choice = RadioField('Do you agree that this situation seems to fit best in this situation category', choices=[('True','True'),('False','False')])
    newCategory = TextAreaField('New Situation Category (use a short phrase to label the new situation category, if you chose an option from above please enter "N/A")', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SortingForm2(FlaskForm):
    newCategory = TextAreaField('New Situation Category (use a short phrase to label the new situation category, if you chose an option from above please enter "N/A")', validators=[DataRequired()])
    submit = SubmitField('Submit')
    


