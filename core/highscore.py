import json
import os

HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'highscores.json')

def load_highscores():
    if not os.path.exists(HIGHSCORE_FILE):
        return {}
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_highscore(game_id, score):
    scores = load_highscores()
    current_high = scores.get(game_id, 0)
    if score > current_high:
        scores[game_id] = score
        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump(scores, f)
        return True # New Record
    return False

def get_highscore(game_id):
    scores = load_highscores()
    return scores.get(game_id, 0)
