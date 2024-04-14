#import openai
from flask_login import current_user

from app.Model.models import Survey

from openai import OpenAI
api_key = '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'

client = OpenAI(api_key=api_key)

def analyze_entry(allSurveys, currentSurvey):


    # Extract checkbox options from the current survey
    current_options = [
        currentSurvey.thoughts_pos,
        currentSurvey.feelings_pos,
        currentSurvey.behaviors_mc,
        currentSurvey.thoughts_neg,
        currentSurvey.feelings_neg
    ]

    # Initialize variables to store the most similar survey and its similarity score
    most_similar_survey = None
    highest_similarity_score = 0

    for survey in allSurveys:
        # Extract checkbox options from the user survey
        survey_options = [
            survey.thoughts_pos,
            survey.feelings_pos,
            survey.behaviors_mc,
            survey.thoughts_neg,
            survey.feelings_neg
        ]


    # Call OpenAI's API to analyze the entry

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
            "content": "You will be provided with the checkbox answers from the current survey, and all previous "
                       "surveys for one user. Identify the survey that is most similar to the current one by 75%."
            },
            {
                "role": "user",
                "content": "\n1. {current_options}\n2. {survey_options)\n"
            }
        ],
        max_tokens=100,
        temperature=0.5

    )
    # Extract similarity score from OpenAI's response







