import time
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://app:app@localhost:3306/lab0'
db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/notes', methods=['GET'])
def get_notes():
    return jsonify([{'id': n.id, 'text': n.text} for n in Note.query.all()])

@app.route('/api/notes', methods=['POST'])
def add_note():
    data = request.get_json()
    note = Note(text=data['text'])
    db.session.add(note)
    db.session.commit()
    return jsonify({'id': note.id, 'text': note.text}), 201

if __name__ == '__main__':
    for _ in range(30):
        try:
            with app.app_context():
                db.create_all()
            break
        except OperationalError:
            time.sleep(1)
    app.run(host='0.0.0.0', port=5000, debug=True)