from pydantic import BaseModel
from datetime import date
from typing import Optional
import risk_level as RiskLevel

class DropoutRiskOutput(BaseModel):
    riskId : Optional[int] = None
    studentId : int
    evaluationDate : date
    absentCount : int
    attendanceCount : int
    consecutiveAbsentDays : int
    negativeCounselingScore : int
    riskScore : float
    riskLevel : RiskLevel
