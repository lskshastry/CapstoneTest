from __future__ import print_function
import sys

from bson import ObjectId
from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request

from app.Controller.OpenAi import analyze_entry
from config import Config
from flask_login import  current_user, login_required
from app import db
from app.Model.models import User, Survey, SituationList, Signature, Thoughtspositive, Thoughtsnegative, \
    Feelingspositive, Feelingsnegative, Behaviormc
from app.Controller.forms import SituationForm, WhatHappened, Thoughts, Feelings, Behavior, SortingForm2, AdminQsortForm, SortingForm
from datetime import datetime
from sqlalchemy.sql import func

from sqlalchemy import desc

from flask import session


bp_routes = Blueprint('routes', __name__)
bp_routes.template_folder = Config.TEMPLATE_FOLDER #'..\\View\\templates'

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
    return render_template('admin_view_surveys.html', title="PsychClinic Web", users = allUsers)

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

            newSurvey = Survey(user = qsortForm.user_id.data,
                               what_happened = qsortForm.prototypicalSituation.data,
                               situation = situation_category_value)

            newSurvey.save_thoughts(
                thoughts_pos=qsortForm.thought_pos.data,
                thoughts_neg=qsortForm.thought_neg.data,
                thoughts_meaning_of_event = qsortForm.protoThought.data
            )
            newSurvey.save_feelings(
                feelings_pos=qsortForm.feelings_pos.data,
                feelings_neg=qsortForm.feelings_neg.data
            )
            newSurvey.save_behaviors(
                behaviors_mc = qsortForm.behavior_mc.data,
                behaviors_description = qsortForm.protoBehavior.data,
                behaviors_outcome = qsortForm.protoGoal.data
            )

            newIfThen = Signature( ifThen = qsortForm.ifthenSignature.data, user = unique_user)
            newIfThen.save()
            newSurvey.save()
            if qsortForm.situationList.data:
                temp = qsortForm.situationList.data.split(',')
                for t in temp:
                    sitList = SituationList(signature = newIfThen, situation = t)
                    sitList.save()
            newSurvey.signature = newIfThen
            newSurvey.save()
           
            return redirect(url_for('routes.admin_index'))
    return render_template('qsort.html', form = qsortForm)
@bp_routes.route('/surveyPost/<survey_id>', methods=['GET'])
@login_required
def surveyPost(survey_id):
    unique_survey = Survey.objects(id=survey_id).first()
    signature = Signature.objects(id=unique_survey.signature.id).first()
    return render_template('surveyPost.html', title="PsychClinic Web", post=unique_survey, time =unique_survey.timestamp.strftime('%B %d %Y '), signature = signature.ifThen)

@bp_routes.route('/userSurveys/<user_id>', methods=['GET'])
@login_required
def userSurveys(user_id):
    unique_user=User.objects(id=user_id).first()
    ifs = Signature.objects(user=unique_user)
    return render_template('userSignatures.html', user=unique_user,  signature = ifs.all())

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
            pos_neg_checker= "False"

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
def what_happened(survey_id,pos_neg, back):
    #create a back that deletes the survey if the user goes back
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
def thoughts(survey_id, pos_neg,back):
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
        return redirect(url_for('routes.behavior', survey_id = unique_survey.id, pos_neg=pos_neg, back='0'))
       
    return render_template('feelings.html', form=feelingsForm, pos_neg=pos_neg, back='0', survey_id=survey_id)


@bp_routes.route('/behavior/<survey_id>/<pos_neg>/<back>', methods=['GET', 'POST'])
@login_required
def behavior(survey_id, pos_neg,back=0):
    print("pos_neg", pos_neg)
    behaviorForm = Behavior()
    # unique survey is the current user survey the future new one
    unique_survey = Survey.objects(id=survey_id).first()

    behaviorForm.behaviors_mc.choices = [(str(t.id), t.name) for t in Behaviormc.objects]

    if back == '1':
        print("testing")
        unique_survey.behaviors_mc = []
        unique_survey.behaviors_description = ""
        unique_survey.behaviors_outcome = ""

        # return redirect(url_for('routes.feelings', survey_id = unique_survey.id, pos_neg=pos_neg, back=back))
    if behaviorForm.validate_on_submit():
        if unique_survey:
            if pos_neg == "False":
                unique_survey.save_behaviors_negative(
                    behaviors_mc = behaviorForm.behaviors_mc.data,
                    behaviors_description = behaviorForm.description.data,
                    behaviors_outcome = behaviorForm.outcome.data
                )
            else:
                unique_survey.save_behaviors_positive(
                    behaviors_mc = behaviorForm.behaviors_mc.data,
                    behaviors_description = behaviorForm.description.data
                )



            #allSurveys = Survey.objects(user=current_user)
            allSurveys = Survey.objects(user=current_user, signature__exists=True)


            analyze_entry(allSurveys, unique_survey)

            print("all surveys", allSurveys)
            allSimilarSurveyID = []
            similarSurvey = ""
            
            compareTP = []
            compareFP = []
            compareB = []
            compareTN = []
            compareFN = []
            # print(type(unique_survey.thoughts_pos))
            currentListTP = []
            currentListFP = []
            currentListB = []
            currentListTN = []
            currentListFN = []

            #gather all information of choose all that apply questions for current survey
            currentListTP = unique_survey.thoughts_pos
            currentListFP = unique_survey.feelings_pos
            currentListB = unique_survey.behaviors_mc
            currentListTN = unique_survey.thoughts_neg
            currentListFN = unique_survey.feelings_neg

            # print(currentList)
            intersectionCountTP = 0
            intersectionCountFP = 0
            intersectionCountB = 0
            intersectionCountTN = 0
            intersectionCountFN = 0
           # loop through all surveys to find similar surveys
            # only want similar surveys with signature ids
            print("new change")
            for survey in allSurveys:
                #print("survey signature id", survey.signature)

                if survey.signature is not None:
                    if str(survey.id) != survey_id:
                        # collects data on survey in all of the surveys if positive situation collect data here
                        if unique_survey.situation == 'Mostly positive feelings' :
                            if survey.situation == 'Mostly positive feelings':
                                if pos_neg == 'True':
                                    print("IN TRUE")

                                    # adds the IDs the comparing
                                    compareTP = survey.thoughts_pos
                                    compareFP = survey.feelings_pos
                                    compareB = survey.behaviors_mc
                                    # calculates the intersection between the two
                                    intersectionCountTP = intersection(compareTP, currentListTP)
                                    intersectionCountFP = intersection(compareFP, currentListFP)
                                    intersectionCountB = intersection(compareB, currentListB)
                                    # print(intersectionCount/len(compareTP))

                                    # check for similarity based on metrics of everything being atleast 50% in common
                                    if (len(compareTP) !=0) and (len(compareFP) != 0) and (len(compareB) != 0):
                                        if (intersectionCountTP/len(compareTP) >=0.50) and (intersectionCountFP/len(compareFP) >=0.50) and (intersectionCountB/len(compareB) >=0.50):
                                            # creating list that will hold all similar survey ids
                                            allSimilarSurveyID.append(survey.id)
                                            # converts current similar survey id to a string
                                            similarSurvey = str(survey.id)
                                    elif ((len(compareTP) == 0 and len(currentListTP) == 0 )  or (len(compareFP) == 0 and len(currentListFP) == 0 )  or (len(compareB) == 0 and len(currentListB) == 0)):
                                        allSimilarSurveyID.append(survey.id)
                                        similarSurvey = str(survey.id)
                                    compareTP = []
                                    compareFP = []
                                    compareB = []
                        if unique_survey.situation == 'Mostly negative feelings':
                            if survey.situation == 'Mostly negative feelings':
                       #if survey that were searching through all surveys is negative collect data here
                                if pos_neg == 'False':
                                    print("IN FALSE")
                                    # need to fill the compare lists that will be used against the survey entries
                                    compareTN = survey.thoughts_neg
                                    compareFN = survey.feelings_neg
                                    compareB = survey.behaviors_mc

                                    intersectionCountTN = intersection(compareTN, currentListTN)
                                    intersectionCountFN = intersection(compareFN, currentListFN)
                                    intersectionCountB = intersection(compareB, currentListB)

                                    # check for similarity based on metrics of everything being atleast 50% in common
                                    if (len(compareTN) !=0) and (len(compareFN) != 0) and (len(compareB) != 0):
                                        if (intersectionCountTN/len(compareTN) >=0.50) and (intersectionCountFN/len(compareFN) >=0.50) and (intersectionCountB/len(compareB) >=0.50):
                                            allSimilarSurveyID.append(survey.id)
                                            similarSurvey = str(survey.id)
                                    elif ((len(compareTN) == 0 and len(currentListTN) == 0 )  or (len(compareFN) == 0 and len(currentListFN) == 0 )  or (len(compareB) == 0 and len(currentListB) == 0)):
                                        allSimilarSurveyID.append(survey.id)
                                        similarSurvey = str(survey.id)
                                    compareTN = []
                                    compareFN = []
                                    compareB = []
            # if there are no similar surveys initialize similar survey string to -1
            if similarSurvey == "":
                # changing int to a str to be the same as when similarSurvey is assigned to the object id
                similarSurveyNum = "-1"
                similarSurvey = str(similarSurveyNum)

            # convert the similar survey list to a string to pass it into sorting route
            convertSTR = convertList(allSimilarSurveyID)
            print("similar survey", similarSurvey)

           # posted the new survey in the databse before assigning a signature
            
        return redirect(url_for('routes.sorting', survey_id = unique_survey.id, pos_neg=pos_neg, back='0', similarSurvey = similarSurvey, allSimilarList = convertSTR))
       
    return render_template('behavior.html', form=behaviorForm, pos_neg=pos_neg, back='0', survey_id=survey_id)

@bp_routes.route('/sorting/<survey_id>/<pos_neg>/<back>/<similarSurvey>/<allSimilarList>', methods=['GET', 'POST'])
@login_required
def sorting(survey_id, pos_neg, back, similarSurvey, allSimilarList):
    test = Survey()
    unique_survey = Survey.objects.filter(id=survey_id).first()
    allUserSignatures = Signature.objects.filter(user = current_user.id).all()

    sign = []
    for s in allUserSignatures:
        signature_id = ObjectId(str(s.id))
        surveyTemp = Survey.objects.filter(signature = signature_id).all()
        for t in surveyTemp:
            print("surveytemp", surveyTemp)
            if t.situation == "Mostly positive feelings" and pos_neg == "True":
                if s.ifThen not in sign:
                    sign.append(s.ifThen)
            elif t.situation == "Mostly negative feelings" and pos_neg == "False":
                if s.ifThen not in sign:
                    sign.append(s.ifThen)

    print("sign::")
    print(sign)
    
    sortform2 = SortingForm2()
    sortingForm = SortingForm()
    anotherthing = Signature()
    total = []
    result = []
    print("similar survey num", similarSurvey)
    # if there are similar surveys similar survey will NOT be equal to -1
    if similarSurvey != "-1":
        # test is a survey it gets the first similar survey to the current survey from the database returns Survey x
        # some surveys do not have a signature id
        test = Survey.objects(id = similarSurvey).first()
        print("test", test)

        # another thing is a signature
        # it is getting the signature of test - which is the similar survey
        # anotherthing = Signature.query.filter_by(id = test.signature_id).first()
        signature_id = test.signature.id
        anotherthing = Signature.objects(id = signature_id).first()
        print("anotherthing", anotherthing)

        if(anotherthing):
            totalSit = SituationList.objects(signature = anotherthing.id).all()
        
            total = []
            
            print("total sit", totalSit)
            for t in totalSit:
                total.append(t)
      
        allID = convertString(allSimilarList)

        allSimilarSurvey = []
        result = []
        # add all the similar survey's signature id's into allSimilarSurvey list
        for id in allID:
            temp = Survey.objects(id = id).first()
            signature_id = temp.signature.id
            if signature_id not in allSimilarSurvey:
                allSimilarSurvey.append(signature_id)
        print("all similar survey ", allSimilarSurvey)
        # remove the current similar id from the list
        if(anotherthing):
            if anotherthing.id in allSimilarSurvey:
                allSimilarSurvey.remove(anotherthing.id)
            print("all similar survey", allSimilarSurvey)

        # get all the actuall if then signature from the common surveys
        for t in allSimilarSurvey:
            temp = Signature.objects(id=t).first()
            if temp is not None:
                result.append(temp.ifThen)
                if temp.ifThen in sign:
                    sign.remove(temp.ifThen)

        if sortingForm.validate_on_submit():

        # after selecting that the situation goes to same category
            if sortingForm.choice.data == 'True':
                if len(similarSurvey) > 0:
                    # get the similar survey
                    test = Survey.objects(id = similarSurvey).first()
                    # get the if then signature for that survey
                    signature_id = test.signature.id
                    anotherthing = Signature.objects(id = signature_id).first()
                    # print("check Pont")
                    print("signature", anotherthing)
                    # set the signature to the current survey and add the situation to the situation list table
                    unique_survey.signature = anotherthing
                    unique_survey.save()
                    newSituation = SituationList(signature = anotherthing, situation = unique_survey.what_happened)
                    newSituation.save()
                    
            else: # pick false new survey is not similar
                option = request.form.getlist('options')
                option2 = request.form.getlist('options2')
                if(len(option) > 0 and len(option2)> 0):
                    flash("Please choose from one either the similar signatures OR all signatures section")
                    return redirect(url_for('routes.sorting', survey_id = survey_id, pos_neg=pos_neg, back='0', similarSurvey = similarSurvey, allSimilarList = allSimilarList))
                elif(len(option2) > 1):
                    flash("please only choose one option")
                    return redirect(url_for('routes.sorting', survey_id = survey_id, pos_neg=pos_neg, back='0', similarSurvey = similarSurvey, allSimilarList = allSimilarList))
                elif len(option2) == 1:
                    getIfThen = Signature.objects(ifThen = option2[0]).first()
                    print(getIfThen)
                    unique_survey.signature = getIfThen
                    unique_survey.save()
                    newSituation = SituationList(signature = getIfThen, situation = unique_survey.what_happened)
                    newSituation.save()
                # flash message if user chose more than one similar survey
                elif len(option) > 1:
                    flash("please only choose one option")
                    return redirect(url_for('routes.sorting', survey_id = survey_id, pos_neg=pos_neg, back='0', similarSurvey = similarSurvey, allSimilarList = allSimilarList))
                # user choice one of the other similar surveys provided to them
                elif len(option) == 1:
                    getIfThen = Signature.objects(ifThen = option[0]).first()
                    unique_survey.signature = getIfThen
                    unique_survey.save()
                    newSituation = SituationList(signature = getIfThen, situation = unique_survey.what_happened)
                    newSituation.save()
                # user entered in a new category
                else:
                    input = sortingForm.newCategory.data
                    newIfthen = Signature(ifThen = input, user = current_user.id)
                    newIfthen.save()
                    unique_survey.signature = newIfthen
                    unique_survey.save()
                    newSituation = SituationList(signature = newIfthen, situation = unique_survey.what_happened)
                    newSituation.save()

            return redirect(url_for('routes.index'))
    # convert similar survey back to int check its -1
    elif int(similarSurvey) == -1:
        # sortform2 = SortingForm2()
        if sortform2.validate_on_submit():
            option2 = request.form.getlist('options2')
            if(len(option2) > 1):
                flash("please only choose one option")
                return redirect(url_for('routes.sorting', survey_id = survey_id, pos_neg=pos_neg, back='0', similarSurvey = similarSurvey, allSimilarList = allSimilarList))
            elif len(option2) == 1:
                getIfThen = Signature.objects(ifThen = option2[0]).first()
                unique_survey.signature = getIfThen
                unique_survey.save()
                newSituation = SituationList(signature = getIfThen, situation = unique_survey.what_happened)
                newSituation.save()
            elif len(option2) == 0:
                # creates new signature non exist for pos neg
                input = sortform2.newCategory.data
                newIfthen = Signature(ifThen = input, user = current_user)
                newIfthen.save()

                # set signature field in survey
                unique_survey = Survey.objects.get(id=survey_id)
                unique_survey.signature = newIfthen
                unique_survey.save()
                new_situation = SituationList(signature=newIfthen, situation=unique_survey.what_happened)
                new_situation.save()

            return redirect(url_for('routes.index'))
    return render_template('sorting.html', similarSurvey = similarSurvey, form=sortingForm, pos_neg=pos_neg, back='0', survey_id=survey_id, id =anotherthing.ifThen, situationlist = total, 
                           allSimilar = result, form2 =sortform2, allUserSignatures = sign)


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
