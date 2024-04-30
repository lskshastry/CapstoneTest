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
            {"role": "system", "content": "Identify the survey most similar to the current one based on the provided options."},
            {"role": "user", "content": f"Current survey options: {current_options}"}
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

            # Verify if the choice has the expected attributes
            if hasattr(choice, 'message'):
                # Access the 'content' attribute of the message
                response_text = choice.message.content.strip()
                print(f"Extracted response text: {response_text}")

                # Use regex to extract the similar survey ID
                match = re.search(r"The survey with ID ([a-z0-9]+)", response_text)
                if match:
                    similarSurvey = match.group(1)
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