"""
SmartTender AI - Enterprise-grade decision-support system for tender response optimization.

This service provides 6-step analysis:
1. Tender requirement extraction
2. CV extraction
3. Matching analysis
4. Bid validation paragraph
5. Rejection email (if applicable)
6. Export-ready summary

ABSOLUTE RULES:
- Extract ONLY explicitly present information
- NEVER infer, guess, or assume
- Return "Not specified" or 0 for missing data
- Support human decisions (not autonomous)
"""

import re
import json


def extract_tender_requirements(tender_text):
    """
    STEP 1: Extract tender requirements from tender document.
    
    Returns:
    {
      "tender": {
        "role": "",
        "required_skills": [],
        "minimum_experience_years": 0,
        "required_certifications": [],
        "sector": ""
      }
    }
    """
    
    def extract_field(label, text):
        """Extract field value by label. Supports alternation with |"""
        labels_list = label.split('|')
        
        for single_label in labels_list:
            pattern = rf'{single_label}[\s:]*\n*(.*?)(?=\n[A-Z]|\n\n|$)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match and match.group(1):
                result = match.group(1).replace('\n', ' ').strip()
                if result:
                    return result
        
        return "Not specified"
    
    def extract_list(label, text):
        """Extract comma or bullet-separated list. Supports alternation with |"""
        val = extract_field(label, text)
        if val == "Not specified":
            return []
        
        # Try bullet points first
        labels_list = label.split('|')
        for single_label in labels_list:
            bullet_pattern = rf'{single_label}.*?\n((?:[ \t]*[-*•].*?\n)+)'
            bullet_match = re.search(bullet_pattern, text, re.IGNORECASE)
            if bullet_match:
                items = re.findall(r'[-*•]\s*(.*?)(?:\n|$)', bullet_match.group(1))
                result = [i.strip() for i in items if i.strip()]
                if result:
                    return result
        
        # Try comma-separated
        if ',' in val:
            return [s.strip() for s in val.split(',') if s.strip()]
        
        # Single value
        return [val] if val != "Not specified" else []
    
    def extract_years(text):
        """Extract minimum years required."""
        patterns = [
            r'minimum\s+(?:of\s+)?(\d+)\s+years?',
            r'(\d+)\s*\+?\s*years?(?:\s+(?:of|experience))?',
            r'experience[\s:]*(\d+)\s+years?'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        return 0
    
    # Extract all fields
    role = extract_field("Role|Title|Position", tender_text)
    required_skills = extract_list("Skills|Requirements|Qualifications", tender_text)
    minimum_experience = extract_years(tender_text)
    required_certs = extract_list("Certifications|Licenses", tender_text)
    sector = extract_field("Sector|Industry|Vertical", tender_text)
    
    return {
        "tender": {
            "role": role,
            "required_skills": required_skills,
            "minimum_experience_years": minimum_experience,
            "required_certifications": required_certs,
            "sector": sector
        }
    }


def extract_cv_data(cv_text, filename="CV"):
    """
    STEP 2: Extract CV data from CV document.
    
    Returns:
    {
      "candidate": {
        "full_name": "",
        "experience_years": 0,
        "skills": [],
        "certifications": [],
        "sector": ""
      }
    }
    """
    
    def extract_name():
        """Extract candidate name from first non-empty line."""
        lines = [line.strip() for line in cv_text.split('\n') if line.strip()]
        if not lines:
            return "Not specified"
        
        first_line = lines[0]
        
        # Remove common prefixes like "Name: " or "Name:"
        first_line = re.sub(r'^(name|applicant|candidate|consultant)[\s:]+', '', first_line, flags=re.IGNORECASE).strip()
        
        # Reject if looks like a title/label
        if any(word.lower() in first_line.lower() for word in ['resume', 'cv', 'curriculum', 'vitae', 'about']):
            if len(lines) > 1:
                second_line = re.sub(r'^(name|applicant|candidate|consultant)[\s:]+', '', lines[1], flags=re.IGNORECASE).strip()
                return second_line if second_line else "Not specified"
            return "Not specified"
        
        # Check length (names typically < 50 chars)
        if len(first_line) > 50:
            return "Not specified"
        
        return first_line if first_line else "Not specified"
    
    def extract_section(labels):
        """Extract section by label."""
        if isinstance(labels, str):
            labels = labels.split('|')
        elif not isinstance(labels, list):
            labels = list(labels)
        
        for label in labels:
            pattern = rf'{label}s?[\s:]*\n*(.*?)(?=\n[A-Z][a-z]+[\s:]|\n\n|$)'
            match = re.search(pattern, cv_text, re.IGNORECASE | re.DOTALL)
            if match and match.group(1):
                content = match.group(1).replace('\n', ', ')
                if content.strip():
                    return content.strip()
        return ""
    
    def extract_section_list(labels):
        """Extract section as list."""
        section = extract_section(labels)
        if not section:
            return []
        
        # Split by comma, bullet, or newline
        items = re.split(r'[,•*]|\n-', section)
        return [s.strip() for s in items if s.strip() and len(s.strip()) > 1]
    
    def extract_years():
        """Extract total years of experience."""
        patterns = [
            r'(\d+)\s*\+?\s*years?(?:\s+(?:of|professional|experience))?',
            r'experience[\s:]*(\d+)\s+years?'
        ]
        for pattern in patterns:
            match = re.search(pattern, cv_text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        return 0
    
    # Extract all fields
    full_name = extract_name()
    experience_years = extract_years()
    skills = extract_section_list(['Skills', 'Technical Skills', 'Core Competencies', 'Expertise'])
    certifications = extract_section_list(['Certifications', 'Licenses', 'Education', 'Qualifications'])
    sector = extract_section(['Sector', 'Industry', 'Domain', 'Specialization']) or "Not specified"
    
    return {
        "candidate": {
            "full_name": full_name,
            "experience_years": experience_years,
            "skills": skills,
            "certifications": certifications,
            "sector": sector
        }
    }


def analyze_matching(tender_data, candidate_data):
    """
    STEP 3: Analyze matching between tender requirements and candidate profile.
    
    Returns:
    {
      "matching": {
        "experience_match": "Yes / No",
        "experience_comparison": "X vs Y required",
        "sector_match": "Yes / No",
        "matched_skills": [],
        "missing_skills": [],
        "matched_certifications": [],
        "certification_status": "Satisfied / Not satisfied"
      }
    }
    """
    
    tender = tender_data["tender"]
    candidate = candidate_data["candidate"]
    
    # Experience matching
    candidate_exp = candidate["experience_years"]
    required_exp = tender["minimum_experience_years"]
    
    if required_exp > 0:
        experience_match = "Yes" if candidate_exp >= required_exp else "No"
        experience_comparison = f"{candidate_exp} vs {required_exp} required"
    else:
        experience_match = "Not specified"
        experience_comparison = "Not specified vs unspecified required"
    
    # Sector matching (exact match only)
    candidate_sector = candidate["sector"].lower() if candidate["sector"] != "Not specified" else ""
    tender_sector = tender["sector"].lower() if tender["sector"] != "Not specified" else ""
    
    sector_match = "Yes" if (candidate_sector and tender_sector and candidate_sector == tender_sector) else "No"
    
    # Skills matching
    tender_skills_lower = [s.lower() for s in tender["required_skills"]]
    candidate_skills_lower = [s.lower() for s in candidate["skills"]]
    
    matched_skills = []
    for candidate_skill in candidate["skills"]:
        if any(candidate_skill.lower() == ts or candidate_skill.lower() in ts or ts in candidate_skill.lower() 
               for ts in tender_skills_lower):
            matched_skills.append(candidate_skill)
    
    missing_skills = []
    for tender_skill in tender["required_skills"]:
        if not any(tender_skill.lower() == cs or tender_skill.lower() in cs or cs in tender_skill.lower() 
                   for cs in candidate_skills_lower):
            missing_skills.append(tender_skill)
    
    # Certifications matching
    tender_certs_lower = [c.lower() for c in tender["required_certifications"]]
    candidate_certs_lower = [c.lower() for c in candidate["certifications"]]
    
    matched_certs = []
    for candidate_cert in candidate["certifications"]:
        if any(candidate_cert.lower() == tc or candidate_cert.lower() in tc or tc in candidate_cert.lower() 
               for tc in tender_certs_lower):
            matched_certs.append(candidate_cert)
    
    certification_status = "Satisfied" if (len(tender["required_certifications"]) == 0 or len(matched_certs) > 0) else "Not satisfied"
    
    return {
        "matching": {
            "experience_match": experience_match,
            "experience_comparison": experience_comparison,
            "sector_match": sector_match,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "matched_certifications": matched_certs,
            "certification_status": certification_status
        }
    }


def generate_validation_paragraph(tender_data, candidate_data, matching_data):
    """
    STEP 4: Generate professional bid validation paragraph.
    
    Returns: Plain text paragraph (4-5 sentences)
    """
    
    tender = tender_data["tender"]
    candidate = candidate_data["candidate"]
    matching = matching_data["matching"]
    
    sentences = []
    
    # Opening
    sentences.append(f"{candidate['full_name']} has submitted an application for the {tender['role']} role.")
    
    # Experience assessment
    if matching["experience_match"] == "Yes":
        sentences.append(f"The candidate meets the experience requirement with {candidate['experience_years']} years of professional experience against the {tender['minimum_experience_years']} years required.")
    elif matching["experience_match"] == "No":
        sentences.append(f"The candidate has {candidate['experience_years']} years of experience, which is below the required {tender['minimum_experience_years']} years.")
    else:
        sentences.append("Experience information could not be verified against requirements.")
    
    # Skills assessment
    if matching["matched_skills"]:
        matched_list = ", ".join(matching["matched_skills"][:3])
        if len(matching["matched_skills"]) > 3:
            matched_list += f", and {len(matching['matched_skills']) - 3} others"
        sentences.append(f"The candidate demonstrates proficiency in {matched_list}.")
    
    if matching["missing_skills"]:
        missing_list = ", ".join(matching["missing_skills"][:2])
        if len(matching["missing_skills"]) > 2:
            missing_list += f", and {len(matching['missing_skills']) - 2} others"
        sentences.append(f"However, the candidate lacks explicit experience in {missing_list}.")
    
    # Certifications
    if tender["required_certifications"]:
        if matching["certification_status"] == "Satisfied":
            sentences.append(f"The candidate holds the required certification(s): {', '.join(matching['matched_certifications'])}.")
        else:
            sentences.append(f"The candidate does not possess the required certifications.")
    
    # Sector match
    if tender["sector"] != "Not specified" and matching["sector_match"] == "No" and candidate["sector"] != "Not specified":
        sentences.append(f"The candidate's sector experience ({candidate['sector']}) does not align with the tender requirement ({tender['sector']}).")
    
    # Final recommendation
    is_suitable = (matching["experience_match"] == "Yes" and 
                   not matching["missing_skills"] and 
                   matching["certification_status"] == "Satisfied")
    
    if is_suitable:
        sentences.append(f"Based on the above analysis, {candidate['full_name']} is a suitable candidate for this tender.")
    else:
        sentences.append(f"Based on the above analysis, {candidate['full_name']} does not fully meet the tender requirements.")
    
    # Combine and limit to 4-5 sentences
    paragraph = " ".join(sentences[:5])
    return paragraph


def generate_rejection_email(tender_data, candidate_data, matching_data):
    """
    STEP 5: Generate professional rejection email (only if not suitable).
    
    Suitable = experience meets AND no missing skills AND certs satisfied
    
    Returns: Plain text email body (4-5 sentences)
    """
    
    is_suitable = (matching_data["matching"]["experience_match"] == "Yes" and 
                   not matching_data["matching"]["missing_skills"] and 
                   matching_data["matching"]["certification_status"] == "Satisfied")
    
    if is_suitable:
        return None  # No rejection email needed
    
    tender = tender_data["tender"]
    candidate = candidate_data["candidate"]
    matching = matching_data["matching"]
    
    email_lines = []
    
    email_lines.append(f"Dear {candidate['full_name']},")
    email_lines.append("")
    
    # Body
    reason_lines = []
    
    if matching["experience_match"] == "No":
        reason_lines.append(f"your professional experience ({candidate['experience_years']} years) does not meet the minimum requirement of {tender['minimum_experience_years']} years")
    
    if matching["missing_skills"]:
        missing = ", ".join(matching["missing_skills"][:2])
        reason_lines.append(f"you lack documented experience in key required skills such as {missing}")
    
    if matching["certification_status"] == "Not satisfied" and tender["required_certifications"]:
        reason_lines.append(f"you do not hold the required certifications")
    
    if reason_lines:
        reason_text = ", and ".join(reason_lines)
        email_lines.append(f"Unfortunately, we are unable to proceed with your application at this time. While we appreciate your interest, {reason_text}.")
    else:
        email_lines.append(f"Unfortunately, we are unable to proceed with your application at this time.")
    
    email_lines.append("")
    email_lines.append("We encourage you to strengthen your experience and qualifications in the identified areas, and we would welcome your future applications.")
    email_lines.append("")
    email_lines.append("Best regards,")
    email_lines.append("Tender Review Team")
    
    return "\n".join(email_lines)


def generate_export_summary(tender_data, candidate_data, matching_data):
    """
    STEP 6: Generate export-ready summary.
    
    Returns:
    {
      "export_summary": {
        "candidate_name": "",
        "role": "",
        "experience": "",
        "sector": "",
        "skills_matched": [],
        "certifications_matched": [],
        "overall_status": "Suitable / Not suitable"
      }
    }
    """
    
    tender = tender_data["tender"]
    candidate = candidate_data["candidate"]
    matching = matching_data["matching"]
    
    # Determine overall status
    is_suitable = (matching["experience_match"] == "Yes" and 
                   not matching["missing_skills"] and 
                   matching["certification_status"] == "Satisfied")
    
    overall_status = "Suitable" if is_suitable else "Not suitable"
    
    return {
        "export_summary": {
            "candidate_name": candidate["full_name"],
            "role": tender["role"],
            "experience": f"{candidate['experience_years']} years",
            "sector": candidate["sector"],
            "skills_matched": matching["matched_skills"],
            "certifications_matched": matching["matched_certifications"],
            "overall_status": overall_status
        }
    }


def run_full_analysis(tender_text, cv_text, cv_filename="CV"):
    """
    RUN COMPLETE 6-STEP ANALYSIS.
    
    Input:
    - tender_text: Extracted tender document text
    - cv_text: Extracted CV document text
    - cv_filename: Filename of CV (for reference only)
    
    Output: Complete analysis package with all 6 steps
    """
    
    try:
        # Step 1: Extract tender requirements
        tender_data = extract_tender_requirements(tender_text)
        
        # Step 2: Extract CV data
        candidate_data = extract_cv_data(cv_text, cv_filename)
        
        # Step 3: Matching analysis
        matching_data = analyze_matching(tender_data, candidate_data)
        
        # Step 4: Validation paragraph
        validation_paragraph = generate_validation_paragraph(tender_data, candidate_data, matching_data)
        
        # Step 5: Rejection email (only if not suitable)
        rejection_email = generate_rejection_email(tender_data, candidate_data, matching_data)
        
        # Step 6: Export summary
        export_summary = generate_export_summary(tender_data, candidate_data, matching_data)
        
        # Combine all outputs
        return {
            "status": "success",
            "analysis": {
                **tender_data,
                **candidate_data,
                **matching_data,
                "validation_paragraph": validation_paragraph,
                "rejection_email": rejection_email,
                **export_summary
            }
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
