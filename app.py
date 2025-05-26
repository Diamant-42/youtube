from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import json
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
DATA_FILE = 'data.json'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

with open(DATA_FILE, 'r') as f:
    try:
        videos_data = json.load(f)
    except json.JSONDecodeError:
        videos_data = {}

@app.route('/')
def index():
    query = request.args.get('search', '').lower()
    sort_by = request.args.get('sort', 'date')
    videos = list(videos_data.items())
    if query:
        videos = [v for v in videos if query in v[0].lower() or any(query in tag.lower() for tag in v[1].get('tags', []))]
    if sort_by == 'likes':
        videos.sort(key=lambda x: x[1]['likes'], reverse=True)
    elif sort_by == 'views':
        videos.sort(key=lambda x: x[1]['views'], reverse=True)
    else:
        videos.sort(key=lambda x: x[1]['date'], reverse=True)
    return render_template('index.html', videos=videos, query=query, sort_by=sort_by)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['video']
        tags = request.form.get('tags', '').split(',')
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            videos_data[filename] = {
                'likes': 0,
                'views': 0,
                'comments': [],
                'tags': [tag.strip() for tag in tags if tag.strip()],
                'date': datetime.now().isoformat()
            }
            save_data()
            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/watch/<filename>', methods=['GET', 'POST'])
def watch(filename):
    data = videos_data.get(filename)
    if not data:
        return 'Vidéo introuvable', 404
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        comment = request.form['comment']
        if comment.strip():
            data['comments'].append({'pseudo': pseudo, 'text': comment.strip()})
            save_data()
    data['views'] += 1
    save_data()
    return render_template('watch.html', filename=filename, data=data)

@app.route('/like/<filename>')
def like(filename):
    if filename in videos_data:
        videos_data[filename]['likes'] += 1
        save_data()
    return redirect(url_for('watch', filename=filename))

@app.route('/video/<filename>')
def video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(videos_data, f, indent=2)

if __name__ == '__main__':
    app.run(debug=True)
