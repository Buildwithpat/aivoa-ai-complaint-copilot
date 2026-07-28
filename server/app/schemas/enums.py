from typing import Literal

Severity = Literal["Critical", "Major", "Minor", "Not Assessed"]
Priority = Literal["Urgent", "High", "Medium", "Low", "Not Assessed"]
ComplaintStatus = Literal["Draft", "Under Investigation", "Pending CAPA", "Closed"]
RiskLevel = Literal["High", "Medium", "Low", "Not Assessed"]
ChatRole = Literal["user", "assistant"]
