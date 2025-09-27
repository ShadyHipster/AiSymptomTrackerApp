# AI Symptom Tracker App

A comprehensive healthcare web application that uses AI to analyze symptoms, provide intelligent diagnoses, and offer personalized triage recommendations. Built for ShellHack (Hackathon) 2025.

## 🚀 Features

- **AI-Powered Symptom Analysis**: Input symptoms in natural language and receive intelligent diagnoses based on healthcare databases
- **Smart Triage System**: Get personalized recommendations for:
  - 🏠 Home care
  - 👨‍⚕️ Doctor visit
  - 🚨 Emergency care
- **User Profiles**: Create and manage personal healthcare profiles with medical history
- **Symptom History**: Track all your symptoms and AI diagnoses over time
- **Medical History Integration**: AI considers your medical history for more accurate diagnoses
- **Responsive Design**: Modern, mobile-friendly interface

## 📸 Screenshots

### Homepage
![Homepage](https://github.com/user-attachments/assets/8327472a-1a73-4275-9768-448b51f1559f)

### AI Diagnosis in Action
![AI Diagnosis](https://github.com/user-attachments/assets/dde9b578-5a0e-4be2-a518-58695d093f12)

### Profile Management
![Profile Management](https://github.com/user-attachments/assets/477fbb1d-df7e-4655-a00f-86a05f4a8fa8)

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **AI Engine**: Custom healthcare database with intelligent matching algorithms

## 📋 Requirements

- Python 3.7+
- Flask 2.3.3
- SQLite (included with Python)

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ShadyHipster/AiSymptomTrackerApp.git
   cd AiSymptomTrackerApp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your web browser
   - Navigate to `http://127.0.0.1:5000`
   - Create an account to get started

## 📖 How to Use

1. **Register/Login**: Create an account with your basic information
2. **Add Medical History**: Update your profile with existing medical conditions
3. **Input Symptoms**: Describe your symptoms in detail on the dashboard
4. **Get AI Diagnosis**: Receive instant analysis with possible diagnoses
5. **Follow Recommendations**: Get triage-level recommendations for next steps
6. **Track History**: View all your previous symptom consultations

## 🏥 AI Healthcare Database

The application includes a simulated healthcare database covering common symptoms:

- **Emergency Conditions**: Chest pain, shortness of breath
- **Doctor Visit**: Fever, cough, fatigue
- **Home Care**: Headaches, nausea, minor aches

Each symptom analysis provides:
- Multiple possible diagnoses
- Severity assessment
- Appropriate triage recommendations
- Personalized advice based on medical history

## 🔒 Data Privacy

- All data is stored locally in SQLite database
- User passwords are hashed for security
- Application is designed for educational purposes
- Always consult healthcare professionals for medical decisions

## 🚨 Important Disclaimer

**This application is for educational and informational purposes only.** It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.

## 🎯 Project Structure

```
AiSymptomTrackerApp/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── symptom_tracker.db    # SQLite database (auto-created)
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── history.html
│   ├── profile.html
│   ├── login.html
│   └── register.html
└── static/               # Static assets
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## 🏆 Competition Details

- **Event**: ShellHack (Hackathon) 2025
- **Category**: Healthcare/Computer Science
- **Goal**: Create an AI-powered healthcare diagnostic tool
- **Focus**: User-friendly interface with intelligent symptom analysis

## 🤝 Contributing

This is a hackathon project, but contributions are welcome! Please feel free to:
- Report issues
- Suggest improvements
- Submit pull requests

## 📄 License

This project is open source and available under the MIT License. 
