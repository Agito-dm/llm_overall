from enum import Enum
from typing import Literal


class Category(str, Enum):
    SUPPORT = "support"
    FEEDBACK = "feedback"
    COMPLAINT = "complaint"
    SALES = "sales"
    GENERAL_QUESTION = "general_question"


Intent = Literal[
    "troubleshooting",
    "how_to",
    "praise",
    "suggestion",
    "refund_request",
    "service_issue",
    "pricing",
    "comparison",
    "information",
    "other",
]
