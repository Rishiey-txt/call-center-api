import base64
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def run_real_test():
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("FAILED: API_KEY not found in .env. Setup missing.")
        return

    if not os.path.exists("sample.mp3"):
        print("FAILED: sample.mp3 not matched natively on disk.")
        return

    with open("sample.mp3", "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode('utf-8')

    url = "http://localhost:8000/api/call-analytics"
    print(f"Sending real POST to {url}...")
    
    try:
        response = requests.post(
            url, 
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
            json={
                "language": "Tamil",
                "audioFormat": "mp3",
                "audioBase64": audio_b64
            }
        )
    except Exception as e:
        print(f"FAILED: Connection to API refused. {e}")
        return

    if response.status_code != 200:
        print(f"FAILED: Expected HTTP 200 via network, got {response.status_code}")
        print("Error Trace:", response.text)
        return

    data = response.json()
    print("--- REAL JSON RESPONSE BOUNDARY ---\n")
    print(json.dumps(data, indent=2))
    print("\n-----------------------------------")

    passed = True

    for key in ["status", "language", "transcript", "summary", "sop_validation", "analytics", "keywords"]:
        if key not in data or data[key] in ["", None]:
            print(f"FAILED: Missing schema root field: {key}")
            passed = False

    for skey in ["greeting", "identification", "problemStatement", "solutionOffering", "closing", "complianceScore", "adherenceStatus", "explanation"]:
        if skey not in data.get("sop_validation", {}):
            print(f"FAILED: Missing nested structure: {skey}")
            passed = False

    score = data.get("sop_validation", {}).get("complianceScore", -1)
    if not isinstance(score, float) or not (0.0 <= score <= 1.0):
        print(f"FAILED: complianceScore {score} violates Float boundary context")
        passed = False

    if data.get("analytics", {}).get("paymentPreference") not in ["EMI", "FULL_PAYMENT", "PARTIAL_PAYMENT", "DOWN_PAYMENT"]:
        print("FAILED: Invalid enum match for paymentPreference")
        passed = False
        
    if data.get("analytics", {}).get("rejectionReason") not in ["HIGH_INTEREST", "BUDGET_CONSTRAINTS", "ALREADY_PAID", "NOT_INTERESTED", "NONE"]:
        print("FAILED: Invalid enum match for rejectionReason")
        passed = False

    if data.get("analytics", {}).get("sentiment") not in ["Positive", "Negative", "Neutral"]:
        print("FAILED: Invalid enum match for sentiment")
        passed = False
        
    if data.get("sop_validation", {}).get("adherenceStatus") not in ["FOLLOWED", "NOT_FOLLOWED"]:
        print("FAILED: adherenceStatus bypasses boolean computation boundaries")
        passed = False

    if passed:
        print("\nPASSED: Request succeeded executing fully through local hardware natively!")
    else:
        print("\nFAILED: Discrepancy observed. System halted.")

if __name__ == "__main__":
    run_real_test()
