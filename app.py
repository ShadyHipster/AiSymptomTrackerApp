from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import hashlib
import os
from datetime import datetime
import json
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Database setup
def init_db():
    conn = sqlite3.connect('symptom_tracker.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  email TEXT NOT NULL,
                  age INTEGER,
                  gender TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Medical history table
    c.execute('''CREATE TABLE IF NOT EXISTS medical_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  condition_name TEXT NOT NULL,
                  diagnosis_date DATE,
                  severity TEXT,
                  notes TEXT,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Symptom logs table
    c.execute('''CREATE TABLE IF NOT EXISTS symptom_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  symptoms TEXT NOT NULL,
                  ai_diagnosis TEXT,
                  recommendation TEXT,
                  triage_level TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    conn.commit()
    conn.close()

# Healthcare database simulation
HEALTHCARE_DATABASE = {
    'fever': {
        'diagnoses': ['Common Cold', 'Flu', 'Bacterial Infection', 'COVID-19'],
        'triage': 'doctor_visit',
        'severity': 'moderate'
    },
    'chest pain': {
        'diagnoses': ['Heart Attack', 'Anxiety', 'Muscle Strain', 'Acid Reflux'],
        'triage': 'emergency',
        'severity': 'high'
    },
    'headache': {
        'diagnoses': ['Tension Headache', 'Migraine', 'Sinus Infection', 'Dehydration'],
        'triage': 'home_care',
        'severity': 'low'
    },
    'cough': {
        'diagnoses': ['Common Cold', 'Bronchitis', 'Pneumonia', 'Allergies'],
        'triage': 'doctor_visit',
        'severity': 'moderate'
    },
    'shortness of breath': {
        'diagnoses': ['Asthma', 'Pneumonia', 'Heart Disease', 'Anxiety'],
        'triage': 'emergency',
        'severity': 'high'
    },
    'nausea': {
        'diagnoses': ['Food Poisoning', 'Stomach Bug', 'Motion Sickness', 'Pregnancy'],
        'triage': 'home_care',
        'severity': 'low'
    },
    'fatigue': {
        'diagnoses': ['Sleep Deprivation', 'Anemia', 'Depression', 'Thyroid Issues'],
        'triage': 'doctor_visit',
        'severity': 'moderate'
    }
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_id(user_id):
    conn = sqlite3.connect('symptom_tracker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def ai_diagnose_symptoms(symptoms, user_history=None):
    """Simulate AI diagnosis based on symptoms and user history"""
    symptoms_lower = symptoms.lower()
    
    # Find matching conditions
    possible_diagnoses = []
    triage_level = 'home_care'
    severity = 'low'
    
    for symptom, data in HEALTHCARE_DATABASE.items():
        if symptom in symptoms_lower:
            possible_diagnoses.extend(data['diagnoses'])
            if data['severity'] == 'high':
                triage_level = 'emergency'
                severity = 'high'
            elif data['severity'] == 'moderate' and severity != 'high':
                triage_level = 'doctor_visit'
                severity = 'moderate'
    
    # Remove duplicates and limit to top 3
    possible_diagnoses = list(set(possible_diagnoses))[:3]
    
    if not possible_diagnoses:
        possible_diagnoses = ['Unknown condition - consult healthcare provider']
        triage_level = 'doctor_visit'
    
    # Generate recommendations based on triage level
    recommendations = {
        'emergency': [
            'Seek immediate emergency care',
            'Call 911 or go to the nearest emergency room',
            'Do not delay treatment'
        ],
        'doctor_visit': [
            'Schedule an appointment with your healthcare provider',
            'Monitor symptoms closely',
            'Consider urgent care if symptoms worsen'
        ],
        'home_care': [
            'Rest and stay hydrated',
            'Monitor symptoms for changes',
            'Contact healthcare provider if symptoms persist or worsen'
        ]
    }
    
    return {
        'diagnoses': possible_diagnoses,
        'triage_level': triage_level,
        'recommendations': recommendations[triage_level]
    }

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        age = data.get('age')
        gender = data.get('gender')
        
        if not all([username, password, email]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = sqlite3.connect('symptom_tracker.db')
        c = conn.cursor()
        
        try:
            c.execute('INSERT INTO users (username, password_hash, email, age, gender) VALUES (?, ?, ?, ?, ?)',
                     (username, hash_password(password), email, age, gender))
            user_id = c.lastrowid
            conn.commit()
            session['user_id'] = user_id
            return jsonify({'success': True})
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Username already exists'}), 400
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        conn = sqlite3.connect('symptom_tracker.db')
        c = conn.cursor()
        c.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and user[1] == hash_password(password):
            session['user_id'] = user[0]
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/diagnose', methods=['POST'])
def diagnose():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    symptoms = data.get('symptoms')
    
    if not symptoms:
        return jsonify({'error': 'No symptoms provided'}), 400
    
    # Get user's medical history for better diagnosis
    conn = sqlite3.connect('symptom_tracker.db')
    c = conn.cursor()
    c.execute('SELECT condition_name FROM medical_history WHERE user_id = ?', (session['user_id'],))
    medical_history = [row[0] for row in c.fetchall()]
    
    # AI diagnosis
    diagnosis_result = ai_diagnose_symptoms(symptoms, medical_history)
    
    # Save to symptom logs
    c.execute('INSERT INTO symptom_logs (user_id, symptoms, ai_diagnosis, recommendation, triage_level) VALUES (?, ?, ?, ?, ?)',
              (session['user_id'], symptoms, 
               json.dumps(diagnosis_result['diagnoses']), 
               json.dumps(diagnosis_result['recommendations']),
               diagnosis_result['triage_level']))
    conn.commit()
    conn.close()
    
    return jsonify(diagnosis_result)

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('symptom_tracker.db')
    c = conn.cursor()
    
    # Get symptom history
    c.execute('SELECT * FROM symptom_logs WHERE user_id = ? ORDER BY created_at DESC', (session['user_id'],))
    symptom_history = c.fetchall()
    
    # Get medical history
    c.execute('SELECT * FROM medical_history WHERE user_id = ?', (session['user_id'],))
    medical_history = c.fetchall()
    
    conn.close()
    
    return render_template('history.html', symptom_history=symptom_history, medical_history=medical_history)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        data = request.get_json()
        condition = data.get('condition')
        diagnosis_date = data.get('diagnosis_date')
        severity = data.get('severity')
        notes = data.get('notes')
        
        conn = sqlite3.connect('symptom_tracker.db')
        c = conn.cursor()
        c.execute('INSERT INTO medical_history (user_id, condition_name, diagnosis_date, severity, notes) VALUES (?, ?, ?, ?, ?)',
                  (session['user_id'], condition, diagnosis_date, severity, notes))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    
    user = get_user_by_id(session['user_id'])
    
    # Get medical history
    conn = sqlite3.connect('symptom_tracker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM medical_history WHERE user_id = ?', (session['user_id'],))
    medical_history = c.fetchall()
    conn.close()
    
    return render_template('profile.html', user=user, medical_history=medical_history)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)