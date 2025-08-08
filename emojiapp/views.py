from django.shortcuts import render, redirect
from django.urls import reverse
from transformers import pipeline

# Load once
emotion_analyzer = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=False)

def guess_mood(text):
    result = emotion_analyzer(text)[0]
    mood = result['label'].lower()

    emoji_map = {
        'joy': "😊",
        'sadness': "😢",
        'anger': "😡",
        'fear': "😨",
        'love': "❤️",
        'surprise': "😲",
    }
    emoji = emoji_map.get(mood, "😐")
    return mood, emoji

def home(request):
    if request.method == "POST":
        sentence = request.POST.get('sentence', '')
        mood, emoji_icon = guess_mood(sentence)

        request.session['mood'] = mood
        request.session['emoji'] = emoji_icon

        return redirect(reverse('home'))

    mood = request.session.pop('mood', None)
    emoji_icon = request.session.pop('emoji', None)

    return render(request, 'home.html', {
        'mood': mood,
        'emoji': emoji_icon
    })
