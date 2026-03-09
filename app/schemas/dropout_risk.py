from pydantic import BaseModel
from datetime import date
from typing import Optional
from app.schemas.risk_level import RiskLevel

class DropoutRiskOutput(BaseModel):
    riskId : Optional[int] = None
    studentId : int #학생ID
    evaluationDate : date #평가일자
    absentCount : int # 결석일수
    attendanceCount : int #출석일수
    consecutiveAbsentDays : int #연속결석일수
    negativeCounselingScore : int #위험도 상담 점수
    riskScore : float # 위험 점수
    riskLevel : RiskLevel # 위험 단계
