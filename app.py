
import os
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import PyPDF2
import docx
import llm_service
import smarttender_service
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

# Simple mail sender (for demo; replace with real SMTP config)
def send_validation_mail(to_email, status, reason):
    sender_email = os.environ.get('MAIL_SENDER', 'noreply@smarttender.local')
    smtp_server = os.environ.get('SMTP_SERVER', 'localhost')
    smtp_port = int(os.environ.get('SMTP_PORT', 1025))
    subject = f"Tender Validation Result: {'Success' if status == 'Suitable' else 'Rejection'}"
    body = f"Dear Candidate,\n\nYour application result: {status}.\n\n{reason}\n\nBest regards,\nTender Review Team"
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.sendmail(sender_email, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Mail send error: {e}")
        return False

@app.route('/api/send-validation-mail', methods=['POST'])
def send_validation_mail_api():
    data = request.get_json()
    email = data.get('email')
    status = data.get('status')
    reason = data.get('reason')
    if not email or not status or not reason:
        return jsonify({"error": "Missing email, status, or reason"}), 400
    success = send_validation_mail(email, status, reason)
    if success:
        return jsonify({"message": "Mail sent successfully"}), 200
    else:
        return jsonify({"error": "Failed to send mail"}), 500

# In-memory storage for the prototype
stored_data = {
    "tender_text": "",
    "tender_requirements": None,  # Store extracted requirements once
    "cv_texts": [] # list of dicts: {"filename": "", "text": ""}
}

def extract_text_from_file(file):
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    text = ""
    
    try:
        if ext == 'pdf':
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif ext in ['doc', 'docx']:
            doc = docx.Document(file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            text = file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")
        text = ""
        
    return text

def parse_tender_requirements(text):
    def extract_field(label, text):
        # Look for Label followed by colon or newline, capturing up to the next newline or common delimiter
        match = re.search(rf'{label}[\s:]+(.*?)(?=\n[A-Z]|$)', text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).replace('\n', ' ').strip()
        return ""
        
    def extract_list(label, text):
        val = extract_field(label, text)
        if not val:
            # fallback: look for a block that might look like a list
            match = re.search(rf'{label}.*?\n((?:[ \t]*[-*•].*?\n)+)', text, re.IGNORECASE)
            if match:
                items = re.findall(r'[-*•]\s*(.*)', match.group(1))
                return [i.strip() for i in items if i.strip()]
            return []
        
        # Split by comma or bullet points if present
        if ',' in val:
            return [s.strip() for s in val.split(',') if s.strip()]
        else:
            # might just be a single item
            return [val] if val else []

    # Try to find experience
    exp_text = extract_field("Experience", text)
    if not exp_text:
        # Fallback to looking for "X years experience"
         exp_match = re.search(r'(\d+)\+?\s*years?', text, re.IGNORECASE)
         exp_years = exp_match.group(1) if exp_match else "Not specified"
    else:
         exp_years_match = re.search(r'\d+', exp_text)
         exp_years = exp_years_match.group() if exp_years_match else "Not specified"

    return {
        "role": extract_field("Role", text) or extract_field("Title", text) or extract_field("Position", text) or "Not specified",
        "skills": extract_list("Skills", text) or extract_list("Requirements", text) or extract_list("Qualifications", text),
        "experience_years": exp_years,
        "certifications": extract_list("Certifications", text),
        "sector": extract_field("Sector", text) or extract_field("Industry", text) or "Not specified",
        "constraints": extract_list("Constraints", text)
    }

def parse_candidate_profile(text, filename):
    def extract_section(labels):
        # looks for any of the labels, captures text up to next double newline or strong header
        for label in labels:
            match = re.search(rf'{label}s?[\s:]*\n*(.*?)(?=\n\s*\n|\n[A-Z][a-z]+:|$)', text, re.IGNORECASE | re.DOTALL)
            if match:
                cleaned = match.group(1).replace('\n', ', ')
                return cleaned.strip()
        return ""
    
    # Try to extract Name from first line
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    name = lines[0] if lines else filename.split('.')[0]
    
    # Clean name if it's too long
    if len(name) > 30 or "resume" in name.lower() or "cv" in name.lower():
        name = filename.split('.')[0]
    
    # Experience
    exp_match = re.search(r'(\d+)\+?\s*years?(?:\s+of)?\s+experience', text, re.IGNORECASE)
    experience_years = exp_match.group(1) if exp_match else "Not specified"
    
    skills_str = extract_section(['Skills', 'Core Competencies', 'Technical Skills', 'Expertise'])
    skills = []
    if skills_str:
        # Split by comma or bullet
        parts = re.split(r'[,•*]|\n-', skills_str)
        skills = [s.strip() for s in parts if s.strip() and len(s.strip()) > 1]
    
    certs_str = extract_section(['Certifications', 'Licenses', 'Education'])
    certs = []
    if certs_str:
        parts = re.split(r'[,•*]|\n-', certs_str)
        certs = [s.strip() for s in parts if s.strip() and len(s.strip()) > 1]
    
    sector_str = extract_section(['Sector', 'Industry', 'Domain'])
    sector = []
    if sector_str:
        parts = re.split(r'[,•*]|\n-', sector_str)
        sector = [s.strip() for s in parts if s.strip() and len(s.strip()) > 1]

    # NLP Matching needs *some* raw text if strict structured sections fail.
    # Fallback: token extraction for skills if list is empty
    if not skills:
        # Very rudimentary fallback: Look for common tech words in text
        common_skills = ['react', 'node.js', 'aws', 'python', 'java', 'sql', 'docker', 'kubernetes', 'azure', 'gcp', 'javascript', 'typescript', 'c++', 'c#', 'agile', 'scrum']
        found = [s for s in common_skills if s in text.lower()]
        skills.extend([f.title() for f in found])

    return {
        "name": name.title(),
        "skills": skills[:15], # Limit to avoid massive payloads
        "experience_years": experience_years,
        "certifications": certs[:5],
        "sector_experience": sector[:5]
    }

def generate_matching_explanation(tender, profile):
    req_skills = [s.lower() for s in tender['skills']]
    prof_skills = [s.lower() for s in profile['skills']]
    
    matched_skills = [s for s in profile['skills'] if any(rs in s.lower() or s.lower() in rs for rs in req_skills)]
    missing_skills = [rs for rs in tender['skills'] if not any(rs.lower() in ps or ps in rs.lower() for ps in prof_skills)]
    
    req_years = int(tender['experience_years']) if tender.get('experience_years') and tender['experience_years'].isdigit() else 0
    prof_years = int(profile['experience_years']) if profile.get('experience_years') and profile['experience_years'].isdigit() else 0
    
    if req_years > 0 and prof_years > 0:
        exp_match = "Meets" if prof_years >= req_years else "Does not meet"
    else:
        exp_match = "Not specified"
        
    req_sector = tender.get('sector', '').lower()
    if req_sector and isinstance(profile.get('sector_experience'), list) and len(profile['sector_experience']) > 0:
        has_sect = any(req_sector in s.lower() or s.lower() in req_sector for s in profile['sector_experience'])
        sector_match = "Yes" if has_sect else "No"
    else:
        sector_match = "Not specified"
        
    matched_certs = [c for c in profile.get('certifications', []) if any(rc.lower() in c.lower() or c.lower() in rc.lower() for rc in tender.get('certifications', []))]
    
    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "experience_match": exp_match,
        "sector_match": sector_match,
        "certification_match": matched_certs
    }

def generate_bid_draft(tender, profile, explanation):
    name = profile.get("name", "The consultant")
    role = tender.get("role", "the required position")
    years = f"{profile.get('experience_years', '')} years" if profile.get('experience_years') and profile['experience_years'].isdigit() else "relevant"
    
    draft = f"{name} is a highly suitable candidate for the {role} position, offering {years} of professional experience. "
    
    if explanation["matched_skills"]:
        draft += f"They demonstrate strong proficiency in critical required areas including {', '.join(explanation['matched_skills'][:3])}. "
    
    if explanation["certification_match"]:
        draft += f"Furthermore, they hold the required {' and '.join(explanation['certification_match'])}, ensuring compliance with technical standards. "
        
    if explanation["sector_match"] == "Yes":
        draft += "Their background strongly aligns with the requested sector domain. "
        
    return draft.strip()


@app.route('/api/upload-tender', methods=['POST'])
def upload_tender():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
        
    text = extract_text_from_file(file)
    stored_data["tender_text"] = text
    
    # Extract tender requirements using Groq AI once
    try:
        if llm_service.is_llm_configured():
            print("Extracting tender requirements with Groq AI...")
            stored_data["tender_requirements"] = llm_service.extract_tender_requirements(text)
            return jsonify({
                "message": "Tender uploaded and analyzed successfully", 
                "text_length": len(text),
                "ai_used": True
            })
    except Exception as e:
        print(f"AI extraction failed: {e}. Using regex fallback.")
        stored_data["tender_requirements"] = None  # Will use regex fallback
    
    # Fallback: use regex-based extraction
    stored_data["tender_requirements"] = parse_tender_requirements(text)
    return jsonify({
        "message": "Tender uploaded successfully (using fallback extraction)", 
        "text_length": len(text),
        "ai_used": False
    })


@app.route('/api/upload-cvs', methods=['POST'])
def upload_cvs():
    if 'files' not in request.files:
        return jsonify({"error": "No files provided"}), 400
        
    files = request.files.getlist('files')
    stored_data["cv_texts"] = []
    
    for file in files:
        if file.filename == '':
            continue
        text = extract_text_from_file(file)
        stored_data["cv_texts"].append({
            "filename": secure_filename(file.filename),
            "text": text
        })
        
    return jsonify({"message": f"{len(stored_data['cv_texts'])} CVs uploaded successfully"})


@app.route('/api/intelligence/analyze', methods=['GET'])
def get_analysis():
    if not stored_data["tender_text"]:
        return jsonify({"error": "No tender document uploaded"}), 400
        
    if not stored_data["cv_texts"]:
        return jsonify({"error": "No CV documents uploaded"}), 400
    
    # Use previously extracted tender requirements (from upload step)
    tender_reqs = stored_data["tender_requirements"]
    
    # If somehow extraction wasn't done, fall back to regex
    if not tender_reqs:
        print("Tender requirements missing. Using regex fallback.")
        tender_reqs = parse_tender_requirements(stored_data["tender_text"])
    
    # Rule-based matching for ALL CVs (no AI per candidate)
    results = []
    for idx, cv_data in enumerate(stored_data["cv_texts"]):
        profile = parse_candidate_profile(cv_data["text"], cv_data["filename"])
        explanation = generate_matching_explanation(tender_reqs, profile)
        
        num_req_skills = len(tender_reqs['skills'])
        matched = len(explanation['matched_skills'])
        score = int(round((matched / num_req_skills) * 100)) if num_req_skills > 0 else 0
        
        results.append({
            "id": idx + 1,
            "profile": profile,
            "matchingInfo": {"matching_explanation": explanation},
            "bidDraft": generate_bid_draft(tender_reqs, profile, explanation),
            "score": score,
            "justification_paragraph": ""  # Will be filled for top match only
        })
    
    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Generate AI justification ONLY for the top-matched candidate
    if results and llm_service.is_llm_configured():
        top_candidate = results[0]
        try:
            print("Generating AI justification for top-matched candidate...")
            justification = llm_service.generate_justification_paragraph(
                tender_reqs,
                top_candidate["profile"],
                top_candidate["matchingInfo"]["matching_explanation"]
            )
            results[0]["justification_paragraph"] = justification
            ai_used = True
        except Exception as e:
            print(f"AI justification failed: {e}. Using fallback.")
            ai_used = False
    else:
        ai_used = llm_service.is_llm_configured()
    
    return jsonify({
        "tender_requirements": tender_reqs,
        "candidates": results,
        "total_candidates": len(results),
        "ai_extraction_used": stored_data["tender_requirements"] is not None,
        "ai_justification_used": ai_used
    })


@app.route('/api/smarttender/analyze', methods=['POST'])
def smarttender_analyze():
    """
    SmartTender AI: Enterprise-grade tender response optimization.
    
    REQUEST JSON:
    {
      "tender_text": "...",
      "cv_text": "...",
      "cv_filename": "optional_filename.pdf"
    }
    
    RESPONSE: Complete 6-step analysis package
    """
    
    data = request.get_json()
    
    # Validate input
    if not data or 'tender_text' not in data or 'cv_text' not in data:
        return jsonify({
            "error": "Missing required fields: tender_text and cv_text"
        }), 400
    
    tender_text = data.get('tender_text', '').strip()
    cv_text = data.get('cv_text', '').strip()
    cv_filename = data.get('cv_filename', 'CV')
    
    if not tender_text or not cv_text:
        return jsonify({
            "error": "Tender text and CV text cannot be empty"
        }), 400
    
    # Run full 6-step analysis
    analysis_result = smarttender_service.run_full_analysis(
        tender_text=tender_text,
        cv_text=cv_text,
        cv_filename=cv_filename
    )
    
    if analysis_result["status"] == "error":
        return jsonify({
            "error": analysis_result["error"]
        }), 500
    
    return jsonify(analysis_result["analysis"]), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
