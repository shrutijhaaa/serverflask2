from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
import random

app = Flask(__name__)
CORS(app)

story_generator = pipeline("text-generation", model="gpt2")

@app.route('/generate_summaries', methods=['POST'])
def generate_summaries():
    data = request.get_json()
    selected_story_types = data.get('selectedStoryTypes', [])

    if not selected_story_types:
        return jsonify({"error": "No story type selected"}), 400

    all_summaries = []

    if len(selected_story_types) == 1:
        story_type = selected_story_types[0]
        prompt = generate_prompt_for_type(story_type)
        summaries = generate_summary(prompt)
        for summary in summaries:
            all_summaries.append({"type": story_type, "summary": summary})
    else:
        combo_prompt = generate_combo_prompt(selected_story_types)
        summaries = generate_summary(combo_prompt)
        for summary in summaries:
            all_summaries.append({"type": ", ".join(selected_story_types), "summary": summary})

    return jsonify({"summaries": all_summaries})

def generate_prompt_for_type(story_type):
    prompt_variations = {
        'Fantasy': [
            "This is a **Fantasy** story. In the magical kingdom of Eldoria, a prophecy foretells of a young warrior who must retrieve the lost Blade of Eternity.",
            "This is a **Fantasy** adventure. A cursed sword, lost for centuries, reappears in the hands of a young hero destined for greatness."
        ],
        'Romantic': [
            "This is a **Romantic** story. A missed train, a forgotten book, and a stranger who might just be the love of a lifetime.",
            "This is a **Romantic** tale. Two souls connected by letters finally meet, only to realize that neither is who they expected."
        ],
        'Mystery': [
            "This is a **Mystery** story. A detective wakes up in a locked room with no memory of how he got there—only a note that says 'RUN'.",
            "This is a **Mystery** thriller. A letter arrives with no sender, containing a single line: 'You have 48 hours to uncover the truth.'"
        ],
        'Science Fiction': [
            "This is a **Science Fiction** adventure. Humanity’s last hope rests in the hands of a scientist who must make an impossible choice.",
            "This is a **Science Fiction** thriller. A rogue AI gains consciousness and starts rewriting human history in real-time."
        ],
        'Horror': [
            "This is a **Horror** story. Every mirror in the house reflects a figure that isn't there.",
            "This is a **Horror** tale. A forgotten lullaby plays in the attic, but no one has been up there for years."
        ],
        'Adventure': [
            "This is an **Adventure** story. An ancient pirate map leads to a treasure that could rewrite history.",
            "This is an **Adventure** quest. A skydiver lands in an unknown land—where time itself seems frozen."
        ],
        'Comedy': [
            "This is a **Comedy** story. A man wakes up to find he has swapped bodies with his pet cat—for a whole week!",
            "This is a **Comedy** tale. A malfunctioning robot assistant takes everything way too literally, leading to complete chaos."
        ],
        'Thriller': [
            "This is a **Thriller** story. A hacker receives a mysterious message: 'Decrypt this file, or the world ends at midnight.'",
            "This is a **Thriller** tale. A secret agent wakes up to find their entire identity erased overnight."
        ],
        'Cartoon': [
            "This is a **Cartoon** story. A mischievous bunny invents a teleporting carrot—and chaos follows!",
            "This is a **Cartoon** tale. A talking sandwich escapes from the fridge and starts a food rebellion."
        ]
    }

    return random.choice(prompt_variations.get(story_type, [f"This is a {story_type} story, filled with excitement and surprises."]))

def generate_combo_prompt(selected_story_types):
    return f"This is a {' and '.join(selected_story_types)} story. In a world where {', '.join(selected_story_types)} collide, an unexpected Story begins."

def generate_summary(prompt):
    generated_texts = story_generator(prompt, max_length=150, num_return_sequences=3, truncation=True)

    summaries = []

    story_text1 = generated_texts[0]["generated_text"]
    sentences1 = story_text1.split('. ')
    summary_lines1 = []
    for sentence in sentences1:
        if sentence.strip():
            summary_lines1.append(sentence.strip())
        if len(summary_lines1) >= 4:
            break
    summaries.append('. '.join(summary_lines1) + "...")

    if len(generated_texts) > 1:
        story_text2 = generated_texts[1]["generated_text"]
        sentences2 = story_text2.split('. ')
        summary_lines2 = []
        for sentence in sentences2:
            if sentence.strip():
                summary_lines2.append(sentence.strip())
            if len(summary_lines2) >= 4:
                break
        summaries.append('. '.join(summary_lines2) + "...")
    else:
        summaries.append('. '.join(summary_lines1) + "...")
        print("Only one generated text is available. Reusing the first summary.")

    return summaries

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)