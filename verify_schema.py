import sys
import json
import os

# Add to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.response import CallAnalyticsResponse, SOPValidation, Analytics

def verify_response_schema():
    # Constructing a valid Response mimicking what the pipeline should output
    data = {
      "status": "success",
      "language": "Tamil",
      "transcript": "Agent: Vanakkam, ungaloda outstanding EMI amount 5000 iruku. Can you pay today?\nCustomer: I can pay 2000 now and the rest next month.",
      "summary": "Agent discussed outstanding EMI of ₹5000. Customer requested partial payment due to budget constraints.",
      "sop_validation": SOPValidation(
        greeting=True,
        identification=False,
        problemStatement=True,
        solutionOffering=True,
        closing=True,
        complianceScore=0.8,
        adherenceStatus="NOT_FOLLOWED",
        explanation="The agent did not verify the customer's identity. All other stages were present."
      ),
      "analytics": Analytics(
        paymentPreference="PARTIAL_PAYMENT",
        rejectionReason="BUDGET_CONSTRAINTS",
        sentiment="Neutral"
      ),
      "keywords": [
        "EMI",
        "outstanding amount",
        "partial payment",
        "5000",
        "budget"
      ]
    }
    
    try:
        response = CallAnalyticsResponse(**data)
        print("Schema Validation: PASS")
        print("Generated JSON Response:")
        print(response.model_dump_json(indent=2))
    except Exception as e:
        print("Schema Validation: FAIL")
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    verify_response_schema()
