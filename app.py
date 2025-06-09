from flask import Flask, render_template, request, redirect, url_for, session
import uuid
import json
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Secure session management

def get_user_file():
    user_id = session.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        session["user_id"] = user_id
    return f"notes/{user_id}.json"

def load_notes():
    filepath = get_user_file()
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

def save_notes(notes):
    filepath = get_user_file()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(notes, f)

@app.route('/')
def home():
    notes = load_notes()
    return render_template('home.html', notes=notes)

@app.route('/new')
def new_note():
    return render_template('note.html', note_id=None, note={"title": "", "content": ""})

@app.route('/save', methods=["POST"])
def save_new_note():
    notes = load_notes()
    note_id = str(uuid.uuid4())
    notes[note_id] = {
        "title": request.form["title"],
        "content": request.form["content"]
    }
    save_notes(notes)
    return redirect(url_for('home'))

@app.route('/note/<note_id>', methods=["GET", "POST"])
def note(note_id):
    notes = load_notes()
    if note_id not in notes:
        return redirect(url_for('home'))
    if request.method == "POST":
        notes[note_id]["title"] = request.form["title"]
        notes[note_id]["content"] = request.form["content"]
        save_notes(notes)
        return redirect(url_for('home'))
    return render_template('note.html', note_id=note_id, note=notes[note_id])

@app.route('/delete/<note_id>', methods=["POST"])
def delete_note(note_id):
    notes = load_notes()
    if note_id in notes:
        del notes[note_id]
        save_notes(notes)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()