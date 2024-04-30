from __future__ import print_function
import sys
import logging
from bson import ObjectId
from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request

from app.Controller.OpenAi import analyze_entry
from config import Config
from flask_login import current_user, login_required
from app import db
from app.Model.models import User, Survey, SituationList, Signature, Thoughtspositive, Thoughtsnegative, \
    Feelingspositive, Feelingsnegative, Behaviormc
from app.Controller.forms import SituationForm, WhatHappened, Thoughts, Feelings, Behavior, SortingForm2, \
    AdminQsortForm, SortingForm
from datetime import datetime
from sqlalchemy.sql import func
from flask import Flask
from sqlalchemy import desc
import os
from flask import session

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_fallback_key')

bp_routes = Blueprint('routes', __name__)
bp_routes.template_folder = Config.TEMPLATE_FOLDER  # '..\\View\\templates'

logging.basicConfig(level=logging.DEBUG)

@bp_routes.route('/', methods=['GET'])
@bp_routes.route('/index', methods=['GET'])
@login_required
def index():
    if current_user.admin != 0:
        return redirect(url_for('auth.login'))

    surveys = Survey.objects(user=current_user)
    ifs = Signature.objects(user=current_user)

    return render_template('index.html', title="PsychClinic Web", posts=surveys, signature=ifs)


@bp_routes.route('/admin_view_surveys', methods=['GET'])
@login_required
def admin_view_survey():
    if current_user.admin != 1:
        return redirect(url_for('auth.login'))
    allUsers = User.objects(admin=0).all()
    return render_template('admin_view_surveys.html', title="PsychClinic Web", users=allUsers)


@bp_routes.route('/admin_index', methods=['GET'])
@login_required
def admin_index():
    if current_user.admin != 1:
        return redirect(url_for('auth.login'))

    all_users = User.objects(admin=0)
    return render_template('admin_index.html', title="PsychClinic Web", users=all_users)


@bp_routes.route('/information', methods=['GET'])
@login_required
def information():
    return render_template('information.html', title="PsychClinic Web")


@bp_routes.route('/pastSituations', methods=['GET'])
@login_required
def pastSituations():
    if current_user.admin != 0:
        return redirect(url_for('auth.login'))

    surveys = Survey.objects(user=current_user)
    ifs = Signature.objects(user=current_user)

    return render_template('pastSituations.html', title="PsychClinic Web", posts=surveys, signature=ifs)


@bp_routes.route('/search', methods=['GET'])
@login_required
def search():
    return render_template('search.html', title="PsychClinic Web")


@bp_routes.route('/pica', methods=['GET'])
@login_required
def pica():
    return render_template('PICA.html', title="PsychClinic Web")


@bp_routes.route('/qsort', methods=['GET', 'POST'])
@login_required
def qsort():
    qsortForm = AdminQsortForm()
    qsortForm.thought_pos.choices = [(str(t.id), t.name) for t in Thoughtspositive.objects]
    qsortForm.thought_neg.choices = [(str(t.id), t.name) for t in Thoughtsnegative.objects]
    qsortForm.feelings_pos.choices = [(str(t.id), t.name) for t in Feelingspositive.objects]
    qsortForm.feelings_neg.choices = [(str(t.id), t.name) for t in Feelingsnegative.objects]
    qsortForm.behavior_mc.choices = [(str(t.id), t.name) for t in Behaviormc.objects]

    if qsortForm.validate_on_submit():

        unique_user = User.objects(id=qsortForm.user_id.data).first()
        if unique_user is None:
            flash("No user found with that ID")
            return redirect(url_for('routes.qsort'))
        else:
            if qsortForm.choice.data == 'True':
                situation_category_value = "Mostly positive feelings"
            else:
                situation_category_value = "Mostly negative feelings"

            newSurvey = Survey(user=qsortForm.user_id.data,
                               what_happened=qsortForm.prototypicalSituation.data,
                               situation=situation_category_value)

            newSurvey.save_thoughts(
                thoughts_pos=qsortForm.thought_pos.data,
                thoughts_neg=qsortForm.thought_neg.data,
                thoughts_meaning_of_event=qsortForm.protoThought.data
            )
            newSurvey.save_feelings(
                feelings_pos=qsortForm.feelings_pos.data,
                feelings_neg=qsortForm.feelings_neg.data
            )
            newSurvey.save_behaviors(
                behaviors_mc=qsortForm.behavior_mc.data,
                behaviors_description=qsortForm.protoBehavior.data,
                behaviors_outcome=qsortForm.protoGoal.data
            )

            newIfThen = Signature(ifThen=qsortForm.ifthenSignature.data, user=unique_user)
            newIfThen.save()
            newSurvey.save()
            if qsortForm.situationList.data:
                temp = qsortForm.situationList.data.split(',')
                for t in temp:
                    sitList = SituationList(signature=newIfThen, situation=t)
                    sitList.save()
            newSurvey.signature = newIfThen
            newSurvey.save()

            return redirect(url_for('routes.admin_index'))
    return render_template('qsort.html', form=qsortForm)


@bp_routes.route('/surveyPost/<survey_id>', methods=['GET'])
@login_required
def surveyPost(survey_id):
    unique_survey = Survey.objects(id=survey_id).first()
    signature = Signature.objects(id=unique_survey.signature.id).first()
    return render_template('surveyPost.html', title="PsychClinic Web", post=unique_survey,
                           time=unique_survey.timestamp.strftime('%B %d %Y '), signature=signature.ifThen)


@bp_routes.route('/userSurveys/<user_id>', methods=['GET'])
@login_required
def userSurveys(user_id):
    unique_user = User.objects(id=user_id).first()
    ifs = Signature.objects(user=unique_user)
    return render_template('userSignatures.html', user=unique_user, signature=ifs.all())


@bp_routes.route('/ifThenSurveys/<user_id>/<signature_id>', methods=['GET'])
@login_required
def ifThenSurveys(user_id, signature_id):
    unique_user = User.objects.get(id=ObjectId(user_id))
    surveys = Survey.objects(user=unique_user, signature=ObjectId(signature_id)).order_by('-timestamp')
    ifs = Signature.objects(user=unique_user, id=ObjectId(signature_id)).first()

    return render_template('userSurveys.html', user=unique_user, surveys=surveys, title=ifs.ifThen)


@bp_routes.route('/situation_category', methods=['GET', 'POST'])
@login_required
def situation_category():
    feelingForm = SituationForm()
    # get pos neg value from URL
    pos_neg_checker = request.args.get('pos_neg', session.get('pos_neg_checker', 'False'))

    if feelingForm.validate_on_submit():
        if feelingForm.choice.data == 'True':
            situation_category_value = "Mostly positive feelings"
            pos_neg_checker = "True"
        else:
            situation_category_value = "Mostly negative feelings"
            pos_neg_checker = "False"

        new_survey = Survey(user=current_user, situation=situation_category_value)
        new_survey.save()

        # Helps to store answer for back buttons
        session['pos_neg_checker'] = pos_neg_checker

        return redirect(url_for('routes.what_happened', survey_id=new_survey.id, pos_neg=pos_neg_checker, back=0))

    # only get the previous value when form is resubmitted; this helps so the form isn't filled on the first opening
    if request.method == 'POST':
        feelingForm.choice.data = pos_neg_checker

    return render_template('feelings_page.html', form=feelingForm, pos_neg=pos_neg_checker, back=0)


@bp_routes.route('/what_happened/<survey_id>/<pos_neg>/<back>', methods=['GET', 'POST'])
@login_required
def what_happened(survey_id, pos_neg, back):
    # create a back that deletes the survey if the user goes back
    whatHappenedForm = WhatHappened()
    unique_survey = Survey.objects(id=survey_id, user=current_user).first()

    if back == '1':  # if back is 1, then we want to clear the what happened field
        print("testing")
        if unique_survey:
            unique_survey.what_happened = ""
            unique_survey.save()

    pos_neg_checker = session.get('pos_neg_checker', 'False')

    if whatHappenedForm.validate_on_submit():
        if unique_survey:
            unique_survey.what_happened = whatHappenedForm.answer.data
            unique_survey.save()

        return redirect(url_for('routes.thoughts', survey_id=unique_survey.id, pos_neg=pos_neg_checker, back='0'))

    return render_template('whatHappened.html', form=whatHappenedForm, pos_neg=pos_neg_checker, back='0')


@bp_routes.route('/thoughts/<survey_id>/<pos_neg>/<back>', methods=['GET', 'POST'])
@login_required
def thoughts(survey_id, pos_neg, back):
    thoughtsForm = Thoughts()
    unique_survey = Survey.objects(id=survey_id, user=current_user).first()

    thoughtsForm.thought_pos.choices = [(str(t.id), t.name) for t in Thoughtspositive.objects]
    thoughtsForm.thought_neg.choices = [(str(t.id), t.name) for t in Thoughtsnegative.objects]

    if back == '1':  # if back is 1, then we want to clear the thoughts field
        print("testing")
        if unique_survey:
            unique_survey.thoughts_pos = []
            unique_survey.thoughts_neg = []
            unique_survey.thoughts_meaning_of_event = ""
            unique_survey.thoughts_summary = ""
            unique_survey.save()

    if thoughtsForm.validate_on_submit():
        if unique_survey:
            unique_survey.save_thoughts(
                thoughts_pos=thoughtsForm.thought_pos.data,
                thoughts_neg=thoughtsForm.thought_neg.data,
                thoughts_meaning_of_event=thoughtsForm.meaning_of_event.data
            )
        return redirect(url_for('routes.feelings', survey_id=unique_survey.id, pos_neg=pos_neg, back='0'))

    return render_template('thoughts.html', form=thoughtsForm, pos_neg=pos_neg, back='0', survey_id=survey_id)


@bp_routes.route('/feelings/<survey_id>/<pos_neg>/<back>', methods=['GET', 'POST'])
@login_required
def feelings(survey_id, pos_neg, back=0):
    feelingsForm = Feelings()
    unique_survey = Survey.objects(id=survey_id).first()

    feelingsForm.feelings_pos.choices = [(str(t.id), t.name) for t in Feelingspositive.objects]
    feelingsForm.feelings_neg.choices = [(str(t.id), t.name) for t in Feelingsnegative.objects]

    if back == '1':
        print("testing")
        unique_survey.feelings_pos = []
        unique_survey.feelings_neg = []
        unique_survey.save()
        # return redirect(url_for('routes.thoughts', survey_id = unique_survey.id, pos_neg=pos_neg, back='0'))
    if feelingsForm.validate_on_submit():
        if unique_survey:
            unique_survey.save_feelings(
                feelings_pos=feelingsForm.feelings_pos.data,
                feelings_neg=feelingsForm.feelings_neg.data
            )
        return redirect(url_for('routes.behavior', survey_id=unique_survey.id, pos_neg=pos_neg, back='0'))

    return render_template('feelings.html', form=feelingsForm, pos_neg=pos_neg, back='0', survey_id=survey_id)


@bp_routes.route('/behavior/<survey_id>/<pos_neg>/<back>', methods=['GET', 'POST'])
@login_required
def behavior(survey_id, pos_neg, back='0'):
    behaviorForm = Behavior()
    unique_survey = Survey.objects(id=survey_id).first()

    if not unique_survey:
        flash("Survey not found.")
        return redirect(url_for('routes.index'))

    behaviorForm.behaviors_mc.choices = [(str(t.id), t.name) for t in Behaviormc.objects]

    if behaviorForm.validate_on_submit():
        if pos_neg == "False":
            unique_survey.save_behaviors_negative(
                behaviors_mc=behaviorForm.behaviors_mc.data,
                behaviors_description=behaviorForm.description.data,
                behaviors_outcome=behaviorForm.outcome.data
            )
        else:
            unique_survey.save_behaviors_positive(
                behaviors_mc=behaviorForm.behaviors_mc.data,
                behaviors_description=behaviorForm.description.data
            )

        # Analyze similar surveys
        allSurveys = Survey.objects(user=current_user, signature__exists=True)
        similarSurvey = analyze_entry(allSurveys, unique_survey)

        # Determine what value to pass for allSimilarList
        # Provide a default value if you don't have one
        allSimilarList = []

        print(f"Proceeding to sorting with similarSurvey: {similarSurvey}")

        # Flash message if similarSurvey is None
        if similarSurvey is None:
            flash("No surveys match your entries. You can add a new category for the survey on the sorting page.")
            # Redirect to sorting page, set allSimilarList as an empty list or a placeholder
            return redirect(url_for('routes.sorting', survey_id=unique_survey.id, pos_neg=pos_neg, back='0', similarSurvey=-1, allSimilarList=allSimilarList))

        # Redirect to sorting page
        return redirect(url_for('routes.sorting', survey_id=unique_survey.id, pos_neg=pos_neg, back='0', similarSurvey=similarSurvey, allSimilarList=allSimilarList))

    return render_template('behavior.html', form=behaviorForm, pos_neg=pos_neg, back=back, survey_id=survey_id)

@bp_routes.route('/sorting/<survey_id>/<pos_neg>/<back>/<similarSurvey>/<allSimilarList>', methods=['GET', 'POST'])
@login_required
def sorting(survey_id, pos_neg, back, similarSurvey, allSimilarList):
    unique_survey = Survey.objects.filter(id=survey_id).first()
    allUserSignatures = Signature.objects.filter(user=current_user.id).all()

    # Step 1: Integrate OpenAI code
    # Obtain all surveys to compare against current survey
    allSurveys = Survey.objects(user=current_user)
    similarSurvey = analyze_entry(allSurveys, unique_survey)

    # Step 2: Use OpenAI response to set similarSurvey
    # If analyze_entry returns a similar survey ID, update similarSurvey variable
    if similarSurvey:
        test = Survey.objects.filter(id=similarSurvey).first()
        signature_id = test.signature.id
        anotherthing = Signature.objects.filter(id=signature_id).first()
        situationlist = SituationList.objects.filter(signature=anotherthing.id).all()
    else:
        test = None
        anotherthing = None
        situationlist = []

    # Step 3: Use the old logic for sorting and saving
    sortform2 = SortingForm2()
    sortingForm = SortingForm()

    # The rest of your old code logic goes here, handling form submissions, saving, and redirecting
    # For example:
    if sortingForm.validate_on_submit():
        if sortingForm.choice.data == 'True':
            # Handle when user agrees with the similar survey
            if test:
                unique_survey.signature = anotherthing
                unique_survey.save()
                new_situation = SituationList(signature=anotherthing, situation=unique_survey.what_happened)
                new_situation.save()
        else:
            # Handle when user disagrees with the similar survey
            option = request.form.getlist('options')
            option2 = request.form.getlist('options2')

            # Your existing logic for handling options, options2, and new category input

        return redirect(url_for('routes.index'))

    # Render the template as per your existing logic
    return render_template('sorting.html', similarSurvey=similarSurvey, form=sortingForm, pos_neg=pos_neg, back=back,
                           survey_id=survey_id, situationlist=situationlist, form2=sortform2,
                           allUserSignatures=allUserSignatures, allSimilarList=allSimilarList)


def intersection(survey, currentSurvey):
    result = []
    for s in survey:
        if s in currentSurvey:
            result.append(s)
    print(result)
    return len(result)


def convertList(list):
    string = ""
    for l in list:
        string = string + str(l) + ','
    if string == "":
        string = "-1"
    else:
        string = string[:-1]
    return string


def convertString(list):
    return list.split(',')


@app.route('/analyze/<int:survey_id>')
@login_required
def analyze_survey(survey_id):
    currentSurvey = Survey.query.get(survey_id)
    allSurveys = Survey.query.filter(Survey.user_id == current_user.id).all()

    similarSurvey, allSimilarList = analyze_entry(allSurveys, currentSurvey)

    if not similarSurvey:
        return "No similar survey found or error in analysis.", 400

    # Redirect or render a template with the results
    return redirect(url_for('show_results', similarSurvey=similarSurvey, allSimilarList=allSimilarList))


@app.route('/results')
@login_required
def show_results():
    similarSurvey = request.args.get('similarSurvey')
    allSimilarList = request.args.get('allSimilarList')
    return render_template('results.html', similarSurvey=similarSurvey, allSimilarList=allSimilarList)


if __name__ == '__main__':
    app.run(debug=True)