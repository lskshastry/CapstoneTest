from app import create_app, db
from app.Model.models import Thoughtspositive, Thoughtsnegative, Feelingspositive, Feelingsnegative, Behaviormc

app = create_app()

@app.before_first_request
def initDB(*args, **kwargs):
    if Thoughtspositive.objects.count() == 0:
        thoughtspos = [
                    'With some effort, I can make things better in this situation. If I try hard enough, I can get what I want in this situation. I can handle this difficult task.',
                    'I no longer have to worry about this. A burden has been lifted from my mind. A threat or harm has been removed from this situation.',
                    'Things are going to be fine. Somehow things might work out. In the end, there’s a chance that everything will be OK.',
                    'I am being treated well. Someone else deserves some credit. Someone else is being helpful to me.',
                    'There is nothing I need to be doing right now. Everything is fine for now.',
                    'I had a role in things turning out well. I deserve some credit for what I’ve done. I’m pleased with what I’ve accomplished.',
                    'I’ve gotten what I wanted. This is great.',
                    'This is good. I am accepted. They appreciate me for who I am. They like me.',
                    'This is interesting, engaging. This is something I enjoy giving my full attention to.',
                    'This was enjoyable. I am having a good time. This is fun.',
                    'This is attractive. This is beautiful.',
                    'My support is needed. I am needed. I can be helpful here.',
                    'This was impressive.'
                    ]
        for t in thoughtspos:
            Thoughtspositive(name=t).save()

    if Thoughtsnegative.objects.count() == 0:
        thoughtsneg = ['This is not interesting. I don’t find this engaging at all.',
                    'Someone or something is getting in my way. This is interfering with what I want. My efforts have been blocked.',
                    'I was hoping for better. That was not what I wanted.',
                    'This situation is not what I expected it to be. I never would have guessed that this would happen.',
                    'I don’t see how this bad situation will ever improve. This will never get any better.',
                    'I’ve lost something important to me.',
                    'They don’t like me. I am not wanted. I have been rejected.',
                    'That was unfair. Someone else is to blame for this bad situation.',
                    'I have a different point of view. I disagree.',
                    'I don’t know whether I can handle what is happening or about to happen. I might not be able to deal with it. Something bad might happen.',
                    'I am certain I won’t be able to handle what is happening or about to happen. I know that I won’t be able to deal with it.',
                    'I don’t understand why things are not better. I don’t know why things are going so badly.',
                    'I should have done something differently in this situation. I wish I hadn’t done what I’ve done.',
                    'I am to blame for this bad situation. Things are bad because of me. I’ve done something wrong.',
                    'They are right to be judgmental/critical of my immoral actions/behaviors. They see that I have done something really wrong.',
                    'I look inadequate. I am being awkward. I look foolish to others.'
                    ]
        for t in thoughtsneg:
            Thoughtsnegative(name=t).save()

    if Feelingspositive.objects.count() == 0:
        feelingspos = [
            'Interested, involved, intrigued',
            'Eager, determined',
            'Lighthearted, happy, joyful',
           'Calm, tranquil, serene',
           'Relieved',
           'Surprised, amazed, astonished',
            'Awe, wonder',
           'Hopeful, optimistic',
           'Pleased, proud, triumphant',
           'Appreciative, thankful, grateful',
            'Amused, humorous',
           'Accepted, liked',
           'Excited, stimulated, passionate',
           'Pleasurable, enjoyment, fun',
            'Affection, close, love'
        ]
        for t in feelingspos:
            Feelingspositive(name=t).save()

    if Feelingsnegative.objects.count() == 0:
        feelingsneg = ['Bored, indifferent, apathetic',
        'Guilty, remorseful',
        'Shame, humiliated',
        'Embarrassed',
       'Sad, depressed, unhappy',
        'Disgust, sickened',
        'Annoyed, resentful, irritated',
        'Frustrated, exasperated',
        'Angry, pissed off, mad',
        'Regretful, dissatisfied, disappointed in myself',
        'Disappointed by others, let down',
        'Defeated, resigned',
        'Nervous, anxious, tense',
        'Afraid, fear, scared',
        'Concerned, worried',
        'Confused, bewildered, disoriented'
        ]
        for t in feelingsneg:
            Feelingsnegative(name=t).save()

    if Behaviormc.objects.count() == 0:
        behavior = [
            'To connect, feel closer to someone, accepted/liked',
            'To do something well, be effective, accomplish something',
            'To create something new, make something, be creative',
            'To get something I wanted',
            'To help, offer assistance, be supportive',
            'To understand, learn, figure something out',
            'To be authentic, real, honest',
            'To make my own decision, have a feeling of choice, do what I want',
            'To be in the moment, be appreciative',
            'To correct something that someone else did that was unfair, not right',
            'To have fun, gratify desires, have pleasure',
            'To be safe, to get away from something challenging, threatening, or dangerous',
            'To meet someone else’s expectations, not make them angry or disappoint them',
            'To get away from something that I didn’t like',
            'To get support, help/assistance from others',
            'To make up for harm I’ve caused'
        ]
        for t in behavior:
            Behaviormc(name=t).save()


if __name__ == "__main__":
    app.run(debug=True)