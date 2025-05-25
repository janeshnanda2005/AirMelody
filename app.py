import requests
from flask import Flask, render_template, request

app = Flask(__name__)

LOUDLY_API_KEY = "4uj1cRM5Y7I0fv02DgFguOk2D9XqD8Prteui17UNRLw"
SONGS_API_URL = "https://soundtracks.loudly.com/api/ai/songs"

GENRES = ["Ambient", "EDM", "Hip Hop", "Electro Chill"]

def download_music_file(url, filename):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            return False
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html', genres=GENRES, selected_genre=None)

@app.route('/generate', methods=['POST'])
def generate_music():
    genre = request.form.get('genre', 'Ambient')

    files = {
        'genre': (None, genre),
        'genre_blend': (None, ''),
        'duration': (None, ''),
        'energy': (None, ''),
        'bpm': (None, ''),
        'key_root': (None, ''),
        'key_quality': (None, ''),
        'instruments': (None, ''),
        'structure_id': (None, ''),
        'test': (None, ''),
    }

    headers = {
        'API-KEY': LOUDLY_API_KEY,
        'Accept': 'application/json',
    }

    response = requests.post(SONGS_API_URL, headers=headers, files=files)

    if response.status_code == 200:
        data = response.json()

        # Extract music file path from response
        music_url = data.get('music_file_path') or data.get('audio_url') or data.get('url')

        if music_url:
            # Save locally with a safe filename
            filename = f"{data.get('title', 'music').replace(' ', '_')}.mp3"
            success = download_music_file(music_url, filename)
            if success:
                message = f"Music downloaded locally as {filename}"
            else:
                message = "Failed to download music file locally."
        else:
            message = "No music file URL found in API response."

        return render_template('index.html', audio_url=music_url, response_data=data, genres=GENRES, selected_genre=genre, message=message)
    else:
        return f"API Error {response.status_code}: {response.text}"

if __name__ == '__main__':
    app.run(debug=True)
