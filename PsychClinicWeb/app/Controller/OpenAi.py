#import openai
from flask_login import current_user
from app.Model.models import Survey
from openai import OpenAI
import re

# Use your own OpenAI API key
api_key = 'xxx'

client = OpenAI(api_key=api_key)

def analyze_entry(allSurveys, currentSurvey):
    similarSurvey = None

    try:
        # Prepare OpenAI request content and messages
        current_options = [
            currentSurvey.thoughts_pos,
            currentSurvey.feelings_pos,
            currentSurvey.behaviors_mc,
            currentSurvey.thoughts_neg,
            currentSurvey.feelings_neg
        ]

        messages = [
            {"role": "system",
             "content": "Given the current survey and the other surveys, identify the most similar survey to the current one based on their respective options such as thoughts, feelings, and behaviors."},
            {"role": "user",
             "content": f"Current survey options:\nThoughts Positive: {currentSurvey.thoughts_pos}\nFeelings Positive: {currentSurvey.feelings_pos}\nBehaviors: {currentSurvey.behaviors_mc}\nThoughts Negative: {currentSurvey.thoughts_neg}\nFeelings Negative: {currentSurvey.feelings_neg}"}
        ]

        # Iterate through allSurveys and add each survey's options to messages
        for survey in allSurveys:
            if survey.id != currentSurvey.id:
                survey_options = [
                    survey.thoughts_pos,
                    survey.feelings_pos,
                    survey.behaviors_mc,
                    survey.thoughts_neg,
                    survey.feelings_neg
                ]
                messages.append({"role": "user", "content": f"Survey ID {survey.id} options: {survey_options}"})

        # Call OpenAI API with messages
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.5
        )

        # Log the response for debugging
        print(f"OpenAI API response: {response}")

        # Check if there are choices in the response
        if response.choices:
            # Access the first choice
            choice = response.choices[0]

            # Make sure the choice contains a message with content
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                response_text = choice.message.content.strip()
                print(f"Extracted response text: {response_text}")

                # Use the updated regular expression pattern to extract the similar survey ID
                match = re.search(r"Survey ID (\S+)", response_text)
                if match:
                    similarSurvey = match.group(1).strip()
                    print(f"Extracted similar survey ID: {similarSurvey}")
                else:
                    print("Could not extract similar survey ID from response text")
                    similarSurvey = None
            else:
                print("The 'message' or 'content' attribute is missing in the OpenAI API response choice.")
                similarSurvey = None
        else:
            print("No choices returned from OpenAI API.")
            similarSurvey = None

    except Exception as e:
        print(f"An error occurred while calling OpenAI API: {e}")

    # Return the similar survey ID
    return similarSurvey