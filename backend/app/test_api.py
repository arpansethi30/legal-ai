import asyncio
import httpx
import json
import os
from datetime import datetime

async def test_agent():
    base_url = "http://localhost:8000"
    client = httpx.AsyncClient(timeout=60.0)  # Longer timeout for complex agent tasks
    
    # Task 1: Execute a complex legal task
    print("\n=== Testing AI Agent with Complex Task ===")
    agent_task = {
        "task": "Draft a software development agreement between TechCorp and DevConsult LLC. TechCorp wants to retain all IP rights, while DevConsult wants fair compensation for their work and a 12-month maintenance period. There should be penalties for late delivery.",
        "context": {
            "industry": "software",
            "client_profile": "enterprise technology company",
            "vendor_profile": "specialized development consultancy"
        }
    }
    
    print("Sending request to agent...")
    response = await client.post(f"{base_url}/agent/execute", json=agent_task)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Task ID: {result.get('task_id')}")
        print("\nPlan generated:")
        for i, step in enumerate(result.get('result', {}).get('plan', [])):
            print(f"  Step {i+1}: {step.get('action')} - {step.get('expected_output')}")
        
        # Extract the contract if available
        synthesis = result.get('result', {}).get('synthesis', {})
        print("\nExecutive Summary:")
        print(synthesis.get('executive_summary', 'Not available'))
        
        print("\nKey Recommendations:")
        for rec in synthesis.get('recommendations', ['Not available']):
            print(f"- {rec}")
    
    # Task 2: Test mediation
    print("\n=== Testing Dispute Mediation ===")
    mediation_request = {
        "party_a_position": "We believe the software has significant bugs that prevent us from using it as intended. We want a full refund.",
        "party_b_position": "The software meets all specifications in the contract. Any issues are due to the client's hardware configuration.",
        "disputed_terms": ["Quality standards", "Acceptance criteria", "Refund policy"],
        "context": "This is a $50,000 contract for custom inventory management software."
    }
    
    print("Requesting mediation...")
    response = await client.post(f"{base_url}/agent/mediate", json=mediation_request)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print("\nMediation Analysis:")
        print("\nCommon Ground:")
        for item in result.get('common_ground', ['Not found']):
            print(f"- {item}")
            
        print("\nCompromise Solutions:")
        for solution in result.get('compromise_solutions', ['Not found']):
            print(f"- {solution}")
    
    # Save test results
    os.makedirs("test_results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"test_results/agent_test_{timestamp}.json", "w") as f:
        json.dump({
            "agent_task_result": response.json() if response.status_code == 200 else {"error": "Request failed"},
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_agent())
