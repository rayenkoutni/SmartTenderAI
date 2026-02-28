import os
import json
from dotenv import load_dotenv

load_dotenv()

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama3-70b-8192"

def is_llm_configured():
    return bool(HAS_GROQ and GROQ_API_KEY and GROQ_API_KEY != "PASTE_YOUR_GROQ_API_KEY_HERE")

def extract_tender_requirements(tender_text):
    """Extract structured requirements from tender document using Groq."""
    if not is_llm_configured():
        raise ValueError("GROQ_API_KEY is not configured.")
    
    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = f"""Extract structured requirements from the following tender document.
Return ONLY valid JSON with no additional text or markdown formatting.

TENDER DOCUMENT:
<<<
{tender_text[:10000]}
>>>

Return this exact JSON structure:
{{
  "role": "",
  "skills": [],
  "minimum_experience_years": "",
  "required_certifications": [],
  "sector": ""
}}

Rules:
- Use ONLY information explicitly present in the tender
- Return "Not specified" for missing information
- Skills and certifications should be lists
- Do NOT invent or assume information"""

    print("Calling Groq: Extract Tender Requirements...")
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        text = message.content[0].text.strip()
        # Strip markdown code fences if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        data = json.loads(text)
        return {
            "role": data.get("role", "Not specified"),
            "skills": data.get("skills", []),
            "experience_years": str(data.get("minimum_experience_years", "")),
            "certifications": data.get("required_certifications", []),
            "sector": data.get("sector", "Not specified"),
            "constraints": []
        }
    except Exception as e:
        raw_text = message.content[0].text if message.content else 'No response text'
        with open('llm_error.log', 'w', encoding='utf-8') as f:
            f.write(f"ERROR: {e}\n\nTEXT:\n{raw_text}")
        print(f"Failed to parse Groq JSON: {e}")
        raise e

def generate_justification_paragraph(tender_reqs, candidate_profile, matching_explanation):
    """Generate professional justification paragraph for best-matched candidate."""
    if not is_llm_configured():
        raise ValueError("GROQ_API_KEY is not configured.")
    
    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = f"""Generate a short professional justification paragraph (max 5 lines) explaining why this consultant is suitable for the tender.

TENDER REQUIREMENTS:
- Role: {tender_reqs.get('role', 'Not specified')}
- Required Skills: {', '.join(tender_reqs.get('skills', []))}
- Experience Required: {tender_reqs.get('experience_years', 'Not specified')} years
- Sector: {tender_reqs.get('sector', 'Not specified')}

CONSULTANT PROFILE:
- Name: {candidate_profile.get('name', 'Unknown')}
- Skills: {', '.join(candidate_profile.get('skills', []))}
- Experience: {candidate_profile.get('experience_years', 'Not specified')} years
- Sector Experience: {', '.join(candidate_profile.get('sector_experience', []))}

MATCH SUMMARY:
- Matched Skills: {', '.join(matching_explanation.get('matched_skills', []))}
- Missing Skills: {', '.join(matching_explanation.get('missing_skills', []))}
- Experience Match: {matching_explanation.get('experience_match', 'Not specified')}
- Sector Match: {matching_explanation.get('sector_match', 'Not specified')}

Rules:
- Use ONLY the provided data above
- No invented or assumed claims
- Keep it professional and formal
- Max 5 lines, 1 paragraph only
- No marketing language"""

    print("Calling Groq: Generate Justification...")
    message = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        text = message.content[0].text.strip()
        return text
    except Exception as e:
        raw_text = message.content[0].text if message.content else 'No response text'
        with open('llm_error.log', 'w', encoding='utf-8') as f:
            f.write(f"ERROR in generate_justification: {e}\n\nTEXT:\n{raw_text}")
        print(f"Failed to generate justification: {e}")
        return ""
