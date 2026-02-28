# 🚀 SmartTender AI
## Automated Tender & CV Matching Platform

> **Hackathon Project – Inetum Challenge**  
> An AI-assisted, explainable system to automate tender analysis and consultant CV matching.

---

## 🧠 Overview

**SmartTender AI** is a proof-of-concept platform designed to automate the most time-consuming and error-prone parts of the tendering workflow.

Organizations responding to tenders must analyze complex requirements, manually review consultant CVs, and prepare validation documents under tight deadlines. This process is repetitive, slow, and prone to human error.

SmartTender AI addresses these challenges by combining **deterministic rule-based matching** with **optional AI assistance**, while keeping all decisions **transparent and human-validated**.

---

## 🎯 Project Objectives

- Reduce manual effort in tender analysis
- Accelerate CV screening and candidate selection
- Improve accuracy and explainability
- Support decision-making under tight deadlines

---

## ✨ Key Features

- 📄 Tender requirement extraction (skills, experience, certifications, sector)
- 👤 Automated CV-to-requirement matching
- 📊 Explainable matching results (met vs missing requirements)
- 🧠 Optional AI-generated justification paragraph for the top candidate
- 📧 Automated candidate communication (selection & rejection emails)
- 📤 Exportable validation report
- 🧩 Human-in-the-loop decision support

---

## 🛠️ Tech Stack

### Frontend
- ⚛️ React (JavaScript / JSX)
- ⚡ Vite
- 🎨 CSS Modules
- 🖼️ Lucide React Icons
- 📧 EmailJS (emailjs-com)

### Backend
- 🐍 Python 3
- 🌐 Flask (REST API)
- 🔓 Flask-CORS
- 📄 PyPDF2 (PDF extraction)
- 📝 python-docx (DOCX extraction)
- 🧮 Custom rule-based matching engine
- 🤖 Optional Groq API (LLM) for AI justification

---

## 🧱 System Architecture

Frontend (React)  
⬇ Upload tender & CV documents  
Backend (Flask API)  
⬇ Text extraction & parsing  
⬇ Rule-based matching engine  
⬇ Optional AI justification  
Results dashboard  
⬇  
Export report & send emails

---

## 🔄 Data Flow

1. User uploads a tender document and multiple CVs via the frontend  
2. Frontend sends files to the Flask backend  
3. Backend extracts and structures data from documents  
4. Rule-based logic matches candidates to tender requirements  
5. Backend returns scores, explanations, and justification  
6. Frontend displays results and enables export and email notifications  

---

## 🧠 Matching & AI Strategy

### Rule-Based Matching
- Compares required skills, years of experience, certifications, and sector
- Produces transparent and explainable results
- Fully deterministic and audit-friendly

### AI Assistance (Optional)
- Uses a Large Language Model (Groq)
- Generates a professional justification paragraph for the top candidate
- AI does not score or select candidates
- Human validation remains mandatory

---

## 📧 Candidate Communication

- Email delivery handled via EmailJS
- Two professional templates:
  - ✅ Selection / validation email
  - ❌ Rejection email
- Emails never mention AI or internal scoring
- Communication remains respectful and standardized

---

## ▶️ Demo Video

🎥 Demo video link:  
https://drive.google.com/file/d/1Yj-TCUOiLPbqrLItlRGuABj1EC3tKVSe/view?usp=sharing
---

## ⚙️ How to Run the Project

### Backend (Flask)

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
Backend runs on: http://localhost:5000


Frontend (React)
npm install
npm run dev

Frontend runs on: http://localhost:5173

🔐 Environment Variables


GROQ_API_KEY=your_groq_api_key_here
EMAILJS_SERVICE_ID=your_service_id
EMAILJS_TEMPLATE_SELECTION=your_template_id
EMAILJS_TEMPLATE_REJECTION=your_template_id
EMAILJS_PUBLIC_KEY=your_public_key



⚠️ Limitations

No persistent database (in-memory processing only)

No authentication or role management

AI justification generated only for the top candidate

Basic error handling

Designed as an MVP / proof of concept

🔮 Future Improvements

Smart tender detection from online platforms

Advanced NLP-based matching models

User authentication and role-based access

Persistent storage and analytics dashboard

Production-grade logging and monitoring

📌 Conclusion

SmartTender AI demonstrates a coherent, scalable, and technically feasible approach to automating tender analysis and CV matching.

By combining explainable rule-based logic with targeted AI assistance, the platform reduces manual workload while maintaining transparency and human control.


👤 Author

Hackathon Project – Inetum Challenge


---



