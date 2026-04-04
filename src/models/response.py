from pydantic import BaseModel, Field
from typing import Literal, List

class SOPValidation(BaseModel):
    greeting: bool
    identification: bool
    problemStatement: bool
    solutionOffering: bool
    closing: bool
    complianceScore: float = Field(ge=0.0, le=1.0)
    adherenceStatus: Literal["FOLLOWED", "NOT_FOLLOWED"]
    explanation: str

class Analytics(BaseModel):
    paymentPreference: Literal[
        "EMI",
        "FULL_PAYMENT",
        "PARTIAL_PAYMENT",
        "DOWN_PAYMENT"
    ]
    rejectionReason: Literal[
        "HIGH_INTEREST",
        "BUDGET_CONSTRAINTS",
        "ALREADY_PAID",
        "NOT_INTERESTED",
        "NONE"
    ]
    sentiment: Literal["Positive", "Negative", "Neutral"]

class CallAnalyticsResponse(BaseModel):
    status: Literal["success", "error"]
    language: str
    transcript: str
    summary: str
    sop_validation: SOPValidation
    analytics: Analytics
    keywords: List[str]
