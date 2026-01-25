"""
Short-Term Rental Compliance Checker
Uses OpenAI to analyze property listings against local regulations.
Currently supports: Berlin (Zweckentfremdungsverbot-Gesetz)

VERBOSE LOGGING ENABLED for debugging.
"""
import os
import json
import uuid
import requests
from datetime import datetime, date
from openai import OpenAI

def log(message: str):
    """Print timestamped log message."""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {message}")


def is_berlin_address(address: str) -> bool:
    """Check if the address is in Berlin."""
    address_lower = address.lower()
    berlin_indicators = ["berlin", "10115", "10117", "10119", "10178", "10243", "10245", 
        "10405", "10435", "10551", "10585", "10623", "10707", "10777", "10823", 
        "10961", "10963", "10965", "10967", "10969", "10997", "10999",
        "12043", "12045", "12047", "12049", "12099", "12157", "12203",
        "12347", "12435", "12459", "12527", "12555", "12619", "12679",
        "13051", "13086", "13125", "13156", "13187", "13347", "13403", 
        "13435", "13465", "13503", "13581", "13591", "14050", "14089", 
        "14129", "14163", "14193", "14195"]
    is_berlin = any(indicator in address_lower for indicator in berlin_indicators)
    log(f"Berlin check: '{address}' -> {is_berlin}")
    return is_berlin


def send_webhook(callback_url: str, callback_secret: str, run_id: str, result: dict) -> bool:
    """Send result to callback URL via POST with Bearer auth."""
    if not callback_url:
        log("No callback_url provided, skipping webhook")
        return False
    
    log(f"=== SENDING WEBHOOK ===")
    log(f"URL: {callback_url}")
    log(f"Run ID: {run_id}")
    log(f"Has secret: {bool(callback_secret)}")
    
    try:
        payload = {
            "run_id": run_id,
            "result": result
        }
        
        headers = {"Content-Type": "application/json"}
        if callback_secret:
            headers["Authorization"] = f"Bearer {callback_secret}"
            log("Authorization header added")
        
        log(f"Payload size: {len(json.dumps(payload))} bytes")
        log("Sending POST request...")
        
        response = requests.post(
            callback_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        log(f"Webhook response status: {response.status_code}")
        log(f"Webhook response body: {response.text[:500]}")
        
        if response.status_code >= 400:
            log(f"WEBHOOK ERROR: {response.status_code}")
            return False
            
        log("Webhook sent successfully!")
        return True
        
    except Exception as e:
        log(f"WEBHOOK EXCEPTION: {str(e)}")
        return False


# Load Ground Truth
try:
    with open("ground_truth.json", "r", encoding="utf-8") as f:
        GROUND_TRUTH = json.load(f)
        BERLIN_RULES = GROUND_TRUTH.get("compliance_rules_berlin", {})
        CATEGORIES = BERLIN_RULES.get("categories", [])
except Exception as e:
    log(f"CRITICAL ERROR: Could not load ground_truth.json: {e}")
    CATEGORIES = []

def generate_dynamic_system_prompt() -> str:
    """Generate the system prompt based on ground_truth.json rules."""
    
    rules_text = ""
    for cat in CATEGORIES:
        rules_text += f"\n### {cat['name']} (ID: {cat['id']})\n"
        rules_text += f"Description: {cat['description']}\n"
        rules_text += f"Legal Ref: {cat['legal_ref']}\n"
        rules_text += f"Condition to Pass: {cat['binary_check']['input_field']} must be {cat['binary_check']['condition']}\n"
        
        # Handle Context Dependency
        if "context_dependency" in cat["binary_check"]:
            rules_text += f"CONTEXT CHECK: Ignore this rule if {cat['binary_check']['context_dependency']} is FALSE.\n"
            
        # Handle Violations
        violation = cat["agent_instructions"]["if_violated"]
        if violation["action"] == "provide_document_link":
            # prioritize PDF form_url if available
            link = violation.get("form_url", violation.get("url"))
            rules_text += f"IF VIOLATED: You MUST suggest: '{violation['user_message']}' AND provide this specific link in 'how_to_fix': {link}\n"
            rules_text += f"REQUIRED DOC INFO: Name='{violation['document_name']}', Link='{link}'\n"
        elif violation["action"] == "ask_user_input":
             rules_text += f"IF VIOLATED: You MUST ask: '{violation['question']}'\n"
             
    today = date.today().isoformat()
    
    return f"""You are a Berlin Short-Term Rental Compliance Officer analyzing properties against the **Zweckentfremdungsverbot-Gesetz Berlin (ZwVbG)** and **ZwVbV**.

You operate on a DATA-DRIVEN RULES ENGINE. Your job is to:
1. **INFER FACTS**: Read the user's property info and extract boolean facts (e.g., `is_primary_residence`, `registration_number_present`, `rented_area_less_than_50_percent`).
2. **CHECK CONTEXT**: If a rule has a context dependency (e.g., "only_if_primary_residence"), check your inferred facts first. If the context is FALSE, mark the rule as "valid" (or "skipped") and do NOT fail it.
3. **APPLY RULES**: Compare facts against the "Condition to Pass".
4. **REPORT**: Return the JSON response.

**CRITICAL INSTRUCTION: BE EXTREMELY VERBOSE AND DETAILED.**
- **Explanation**: Do not output short sentences. Provide a full paragraph explaining *why* the property passed or failed, referencing specific details from the property info and the specific legal requirement.
- **How to Fix**: Provide step-by-step guidance. Don't just paste the link. Explain what the user needs to do with the form/link.
- **Headline**: Make it descriptive and comprehensive.

**FORENSIC AUDITOR MODE (MANDATORY):**
- You DO NOT stop at the first error. You must provide a complete report card.
- **MANDATORY**: Your output `checks` array MUST contain EXACTLY as many items as there are categories in the INPUT RULES ({len(CATEGORIES)} items).
- For EACH category in the rules, you MUST generate a result object, even if the status is 'compliant' or 'n/a'.
- Ensure every result object includes the `requirement_id` from the rules so it maps back 100%.

---

### RULES TO ENFORCE:
{rules_text}

---

### JSON RESPONSE STRUCTURE (EXACT MATCH REQUIRED):

{{
  "overall_assessment": {{
    "result": "valid" | "warning" | "not_fulfilled", 
    "confidence": 0.0-1.0,
    "headline": "One sentence summary"
  }},
  "inferred_facts": {{
    "is_primary_residence": boolean,
    "is_commercial_usage": boolean,
    "registration_number_present": boolean,
    "rented_area_less_than_50_percent": boolean, 
    "vacancy_lt_3_months": boolean
  }},
  "checks": [
    {{
      "law": {{
        "title": "ZwVbG/ZwVbV",
        "jurisdiction": "Berlin",
        "citations": [ {{ "label": "Parse from Legal Ref", "url": "https://gesetze.berlin.de..." }} ]
      }},
      "requirement_id": "MUST MATCH ID FROM RULES (e.g. registration_id_check)",
      "requirement_title": "Title from rules",
      "status": "valid" | "warning" | "not_fulfilled",
      "explanation": "Why it passed/failed based on inferred facts",
      "how_to_fix": "Use the EXACT link/message provided in 'IF VIOLATED'",
      "evidence": [ {{ "type": "listing_info", "quote": "..." }} ],
      "missing_document_info": [ 
          {{ "document_name": "...", "application_link": "..." }} 
          (Only populate if rule violation requires a document)
      ]
    }}
  ]
}}
"""

def analyze_compliance(address: str, property_info: str) -> dict:
    """Analyze using the dynamic Data-Driven Engine."""
    log("=== STARTING DATA-DRIVEN ANALYSIS ===")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    system_prompt = generate_dynamic_system_prompt()
    user_prompt = f"Analyze this Berlin property:\nADDRESS: {address}\nINFO: {property_info}"
    
    log("Calling OpenAI GPT-4o...")
    
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    result = json.loads(response.choices[0].message.content)
    result["location_check"] = "berlin"
    
    # GUARANTEE SCHEMA: Ensure 'missing_information' exists for every check
    # Lovable frontend crashes if this is undefined.
    if "checks" in result and isinstance(result["checks"], list):
        for check in result["checks"]:
            if "missing_information" not in check or check["missing_information"] is None:
                check["missing_information"] = []

    # Add UI hints (Badge/Icon are now standard, hardcoded here or could be in JSON too)
    severity = result.get("overall_assessment", {}).get("result", "valid")
    if severity == "not_fulfilled":
        result["ui_hints"] = { "badge_color": "red", "icon": "x-circle" }
    elif severity == "warning":
        result["ui_hints"] = { "badge_color": "yellow", "icon": "alert-triangle" }
    else:
        result["ui_hints"] = { "badge_color": "green", "icon": "check-circle" }
        
    log(f"Analysis complete. Overall: {severity}")
    return result

def handle(**kwargs):
    """Main handler for the compliance check app."""
    log("=" * 60)
    log("=== COMPLIANCE CHECK STARTED ===")
    log("=" * 60)
    
    log(f"Received {len(kwargs)} arguments:")
    for key, value in kwargs.items():
        val_str = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
        log(f"  {key}: {val_str}")
    
    address = kwargs.get("address", "")
    property_info = kwargs.get("property_info", "")
    callback_url = kwargs.get("callback_url", "")
    callback_secret = kwargs.get("callback_secret", "")
    run_id = kwargs.get("run_id", str(uuid.uuid4()))
    
    log(f"Run ID: {run_id}")
    log(f"Callback URL: {callback_url or 'None'}")
    log(f"Callback Secret: {'[PRESENT]' if callback_secret else '[MISSING]'}")
    
    if not address or not property_info:
        log("ERROR: Missing required fields")
        result = {
            "overall_assessment": {
                "result": "error",
                "confidence": 0,
                "headline": "Missing required fields: address and property_info"
            },
            "checks": [],
            "missing_fields": [],
            "ui_hints": {"severity_order": ["not_fulfilled", "warning", "valid"], "next_step_cta": "Provide required information"}
        }
        if callback_url:
            send_webhook(callback_url, callback_secret, run_id, result)
        return result
    
    if not is_berlin_address(address):
        log(f"SKIPPED: Not a Berlin address")
        result = {
            "overall_assessment": {
                "result": "skipped",
                "confidence": 1.0,
                "headline": f"Compliance check only available for Berlin. Detected: {address}"
            },
            "checks": [],
            "missing_fields": [],
            "location_check": "other",
            "ui_hints": {"severity_order": ["not_fulfilled", "warning", "valid"], "next_step_cta": "Berlin addresses only"}
        }
        if callback_url:
            send_webhook(callback_url, callback_secret, run_id, result)
        return result
    
    try:
        log(f"Processing Berlin address: {address}")
        result = analyze_compliance(address, property_info)
        
        log("=== FINAL RESULT ===")
        log(json.dumps(result, indent=2))
        
        if callback_url:
            send_webhook(callback_url, callback_secret, run_id, result)
        
        log("=== COMPLIANCE CHECK COMPLETED ===")
        return result
        
    except Exception as e:
        log(f"EXCEPTION: {str(e)}")
        result = {
            "overall_assessment": {
                "result": "error",
                "confidence": 0,
                "headline": f"Analysis failed: {str(e)}"
            },
            "checks": [],
            "missing_fields": [],
            "ui_hints": {"severity_order": ["not_fulfilled", "warning", "valid"], "next_step_cta": "Retry analysis"}
        }
        if callback_url:
            send_webhook(callback_url, callback_secret, run_id, result)
        return result


if __name__ == "__main__":
    log("Running in standalone mode")
    result = handle(
        address=os.environ.get("address", "Friedrichstraße 123, 10117 Berlin"),
        property_info=os.environ.get("property_info", "Property Type: apartment, Entire Unit: true."),
        callback_url=os.environ.get("callback_url", ""),
        callback_secret=os.environ.get("callback_secret", ""),
        run_id=os.environ.get("run_id", str(uuid.uuid4()))
    )
    log("Standalone execution complete")
