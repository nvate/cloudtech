import time
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
import os

PORT = int(os.environ.get('PORT', 5000))
INSTANCE_ID = f"backend-{PORT}"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://app:app@localhost:3306/lab0'
db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)

@app.route('/api/notes', methods=['GET'])
def get_notes():
    notes = [{'id': n.id, 'text': n.text} for n in Note.query.all()]
    return jsonify({'backend': INSTANCE_ID, 'notes': notes}), 200, {'X-Backend-Id': INSTANCE_ID}

@app.route('/api/notes', methods=['POST'])
def add_note():
    data = request.get_json()
    note = Note(text=data['text'])
    db.session.add(note)
    db.session.commit()
    return jsonify({'backend': INSTANCE_ID, 'id': note.id, 'text': note.text}), 201, {'X-Backend-Id': INSTANCE_ID}

if __name__ == '__main__':
    for _ in range(30):
        try:
            with app.app_context():
                db.create_all()
            break
        except OperationalError:
            time.sleep(1)
    app.run(host='0.0.0.0', port=PORT, debug=True)