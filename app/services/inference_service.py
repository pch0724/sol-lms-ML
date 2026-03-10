import pandas as pd
from datetime import date
from app.schemas.dropout_risk import DropoutRiskOutput
from sqlalchemy import text
from app.util.db_connect import db_connection
from models.model_manage import get_model_bundle
from app.schemas.input import PredictRequest
from app.services.feature.attendance import get_attendance
from app.services.feature.counseling import get_counsel_feature
from app.services.feature.training import get_training_detail

NEGATIVE_COLS = [
'complaint_facility_sum',
'complaint_instructor_sum',
'complaint_trainee_sum',
'total_severity_avg',
'depression_count',
'panic_count',
'low_intel_count',
'physical_issue_count',
'family_economic_count',
'family_conflict_count',
'family_care_count',
'motivation_decline_count',
'understanding_deficit_count',
'bad_attitude_count',
'career_confusion_count',
'avoidance_count',
'attention_seeking_count',
'selfish_count',
'non_communication_count'
]

def predict_dropout(req: PredictRequest):    
    
    training = get_training_detail(req.training_id)
    
    student_cnt = int(training.iloc[0]["student_cnt"])

    if student_cnt != 0:    
        attendance_feature = get_attendance(req.training_id, req.trainee_key_allowed)
        attendance_feature = attendance_feature.rename(
            columns={"trnee_cstmr_id": "trnee_id"}
        )

        counsel_feature = get_counsel_feature(req.training_id, req.trainee_key_allowed)

        # Feature Merge
        attendance_feature["trnee_id"] = attendance_feature["trnee_id"].astype(str)
        counsel_feature["trnee_id"] = counsel_feature["trnee_id"].astype(str)

        final_features = (
            attendance_feature
            .merge(counsel_feature, on="trnee_id", how="left")
            .fillna(0)
        )   

        bundle = get_model_bundle()
        
        model = bundle["model"]
        
        feature_columns = bundle["features"]
        
        # 1. 학습 때 feature 순서 맞추기
        model = bundle["model"]
        feature_columns = bundle["features"]

        X = final_features.copy()
        for col in feature_columns:
            if col not in X.columns:
                X[col] = 0

        X = X[feature_columns]
        X = X.apply(pd.to_numeric, errors="coerce")
        
        # 3. 확률 예측
        probs = model.predict_proba(X)[:, 1]

        final_features["dropout_prob"] = probs

        df_student = get_student(req.training_id)
        
        df_response = pd.merge(
            final_features,
            df_student,
            on="trnee_id",
            how="left"
        )
        df_response["risk_grade"] = df_response["dropout_prob"].apply(risk_grade)    
        df_response["negativeCounselingScore"] = df_response[NEGATIVE_COLS].sum(axis=1)
        
        result = get_output(df_response)
        
        return result
    else :
        return None
    
def get_student(training_id) :
    
    engine = db_connection()
    
    query = text("""
        select 
            s.student_id,
            s.trnee_id
        from student s 
        where s.training_id = :training_id
        order by s.trnee_id
    """)
    
    df_student = pd.read_sql(query,engine,params={"training_id" : training_id})
    
    df_student["trnee_id"] = df_student["trnee_id"].astype(str)
    
    return df_student

def risk_grade(prob):
    if prob >= 0.8:
        return "HIGH"
    elif prob >= 0.5:
        return "MEDIUM"
    else:
        return "LOW"
    
def get_output(df_response) :
    today = date.today()
    
    result = []
    
    for row in df_response.itertuples(index=False):
        item = DropoutRiskOutput(
            studentId=row.student_id,
            evaluationDate=today,
            absentCount=row.absence_days,
            attendanceCount=row.total_days,
            consecutiveAbsentDays=row.max_consecutive_absent,
            negativeCounselingScore=int(row.negativeCounselingScore),
            riskScore=row.dropout_prob,
            riskLevel=row.risk_grade
        )

        result.append(item)
        
    return result