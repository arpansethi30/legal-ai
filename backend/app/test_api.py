import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, data, description):
    print(f"\n===== Testing: {description} =====")
    start_time = time.time()
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Response received in {time.time() - start_time:.2f} seconds")
            return result
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

# 1. Test legal reasoning
legal_reasoning_data = {
    "legal_text": "The parties agree that all intellectual property created during the term of this agreement shall be owned exclusively by the Client, and Contractor hereby assigns all rights to such intellectual property to Client.",
    "question": "Who owns the intellectual property created during the agreement?",
    "methods": ["Textual Analysis", "Statutory Interpretation"]
}

reasoning_result = test_endpoint(
    "/workflow/reasoning", 
    legal_reasoning_data,
    "Legal Reasoning with Multiple Methods"
)

# 2. Test expert consultation
expert_consultation_data = {
    "question": "Is this non-compete clause enforceable?",
    "document": "The Contractor agrees not to engage in any competing business within the entire United States for a period of 5 years after termination of this Agreement.",
    "experts": ["Contract Law Expert", "Employment Law Expert", "Litigation Expert"]
}

consultation_result = test_endpoint(
    "/workflow/consult", 
    expert_consultation_data,
    "Expert Consultation Simulation"
)

# 3. Test issue identification
issue_identification_data = {
    "document": "This agreement shall commence on January 1, 2025 and continue until terminated by either party with 30 days notice. Payment terms are net 30. All disputes shall be resolved through binding arbitration."
}

issues_result = test_endpoint(
    "/workflow/identify-issues", 
    issue_identification_data,
    "Legal Issue Identification"
)

# 4. Test client memo generation (if we have previous results)
if reasoning_result:
    client_memo_data = {
        "analysis": reasoning_result,
        "client_info": {
            "name": "Acme Corporation",
            "contact": "John Smith",
            "matter": "IP Agreement Review"
        }
    }
    
    memo_result = test_endpoint(
        "/workflow/client-memo", 
        client_memo_data,
        "Client Memo Generation"
    )

print("\n===== All Tests Completed =====")