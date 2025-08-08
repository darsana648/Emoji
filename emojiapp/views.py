from django.shortcuts import render, redirect
from django.urls import reverse
from transformers import pipeline
import emoji 

classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=True,
)

EMOJI_NAME_MAP = {
    "admiration": "smiling_face_with_heart-eyes",
    "amusement": "face_with_tears_of_joy",
    "anger": "angry_face",
    "annoyance": "unamused_face",
    "approval": "thumbs_up",
    "caring": "hugging_face",
    "confusion": "thinking_face",
    "curiosity": "face_with_monocle",
    "desire": "smiling_face_with_hearts",
    "disappointment": "disappointed_face",
    "disapproval": "thumbs_down",
    "disgust": "nauseated_face",
    "embarrassment": "flushed_face",
    "excitement": "star-struck",
    "fear": "fearful_face",
    "gratitude": "folded_hands",
    "grief": "broken_heart",
    "joy": "smiling_face_with_smiling_eyes",
    "love": "red_heart",
    "nervousness": "grimacing_face",
    "optimism": "slightly_smiling_face",
    "pride": "relieved_face",
    "realization": "light_bulb",
    "relief": "face_exhaling",
    "remorse": "pensive_face",
    "sadness": "crying_face",
    "surprise": "astonished_face",

    "tired": "sleeping_face",
    "exhausted": "weary_face",
    "lonely": "pensive_face",
    "hope": "smiling_face_with_smiling_eyes",  
    "conflicted": "confused_face",
    "bored": "expressionless_face",
    "sleepy": "sleeping_face",
    "calm": "relieved_face",
    "thankful": "folded_hands",
    "frustration": "face_with_steam_from_nose",
    "anxious": "worried_face",
    "joyful": "grinning_face_with_smiling_eyes",
    "grateful": "folded_hands",
    "curious": "face_with_monocle",
}

FALLBACK_EMOJI = "slightly_smiling_face"  

SITUATION_EMOJI_NAME_MAP = {
    "birthday": "party_popper",
    "congratulations": "confetti_ball",
    "party": "partying_face",
    "celebrate": "tada",
    "festival": "fireworks",
    "wedding": "bride_with_veil",
    "anniversary": "heart_with_ribbon",

    "happy": "smiling_face_with_smiling_eyes",
    "joy": "grinning_face_with_smiling_eyes",
    "love": "red_heart",
    "heart": "red_heart",
    "sad": "crying_face",
    "angry": "angry_face",
    "anger": "angry_face",
    "fear": "fearful_face",
    "tired": "sleeping_face",
    "exhausted": "weary_face",
    "sleep": "sleeping_face",
    "nervous": "grimacing_face",
    "confused": "confused_face",
    "surprise": "astonished_face",
    "disappointed": "disappointed_face",
    "disgust": "nauseated_face",
    "embarrassed": "flushed_face",
    "excited": "star-struck",
    "proud": "relieved_face",
    "calm": "relieved_face",
    "hope": "face_with_rolling_eyes",  
    "thank": "folded_hands",
    "sorry": "pensive_face",
    "miss": "pleading_face",
    "lonely": "pensive_face",
    "hurt": "broken_heart",
    "heartbreak": "broken_heart",

    "sick": "face_with_thermometer",
    "fever": "thermometer",
    "cold": "cold_face",
    "hot": "hot_face",
    "rain": "cloud_with_rain",
    "sun": "sun_with_face",
    "hungry": "fork_and_knife",
    "thirsty": "cup_with_straw",

    "friend": "handshake",
    "friends": "handshake",
    "family": "family",
    "kiss": "kiss_mark",
    "hug": "hugging_face",
    "love you": "red_heart",
    "baby": "baby",
    "child": "child",
    "parent": "family",
    "teacher": "mortar_board",
    "work": "briefcase",
    "job": "briefcase",

    "music": "musical_note",
    "dance": "person_dancing",
    "coffee": "hot_beverage",
    "tea": "teacup_without_handle",
    "food": "plate_with_cutlery",
    "drink": "tumbler_glass",
    "travel": "airplane",
    "holiday": "palm_tree",
    "dream": "thought_balloon",
    "study": "books",
    "book": "book",

    "ok": "ok_hand",
    "thumbs up": "thumbs_up",
    "thumbs down": "thumbs_down",
    "clap": "clapping_hands",
    "wave": "waving_hand",
    "peace": "victory_hand",
    "rock on": "sign_of_the_horns",
    "sleepy": "sleeping_face",
    "yawn": "sleeping_face",

    "yes": "white_check_mark",
    "no": "cross_mark",
    "stop": "raised_hand",
    "help": "raised_hand",
    "love": "red_heart",


}

def find_situational_label_and_emoji(text):
    text_lower = text.lower()
    for keyword, emoji_name in SITUATION_EMOJI_NAME_MAP.items():
        if keyword in text_lower:
            return keyword.capitalize(), emoji.emojize(f":{emoji_name}:", language='en')
    return None, None
def map_label_to_emoji_with_context(label, text, score, index=0):
    if index == 0:
        situ_label, situ_emoji = find_situational_label_and_emoji(text)
        if situ_emoji:
            return situ_label, situ_emoji
    emoji_name = EMOJI_NAME_MAP.get(label.lower(), FALLBACK_EMOJI)
    return label, emoji.emojize(f":{emoji_name}:", language='en')


def top_k_emotions(text, k=3):
    all_scores = classifier(text)[0]
    sorted_scores = sorted(all_scores, key=lambda x: x['score'], reverse=True)
    return sorted_scores[:k]

def home(request):
    if request.method == "POST":
        sentence = request.POST.get("sentence", "").strip()
        if not sentence:
            return redirect(reverse("home"))

        top = top_k_emotions(sentence, k=3)
        prepared = []
        for i, item in enumerate(top):
            label = item['label']
            score = float(item['score'])
            display_label, emoji_char = map_label_to_emoji_with_context(label, sentence, score, index=i)
            prepared.append({
                "label": display_label,
                "emoji": emoji_char,
                "score": round(score, 4),
                "percentage": round(score * 100)
            })



        request.session['mood_result'] = {
            "sentence": sentence,
            "top": prepared
        }
        return redirect(reverse("home"))

    result = request.session.pop('mood_result', None)
    return render(request, "home.html", {"result": result})
