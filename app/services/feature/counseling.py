import pandas as pd
from sqlalchemy import text
from app.util.db_connect import db_connection

def get_hrd_counseling_data(training_id, trainee_key_allowed):
    engine = db_connection()
    
    query = text("""
    select
        c.counseling_id,
        c.counseling_date,
        c.counseling_type,
        c.counselor,
        b.name,
        b.status,
        b.training_id,
        b.trnee_id,
        c.health_depression,
        c.health_panic,
        c.health_low_intelligence,
        c.health_physical,
        c.health_severity,
        c.family_economic,
        c.family_conflict,
        c.family_care,
        c.family_severity,
        c.learning_motivation_decline,
        c.learning_understanding_deficit,
        c.learning_attitude,
        c.learning_career,
        c.learning_severity,
        c.tendency_avoidance,
        c.tendency_attention_seeking,
        c.tendency_selfish,
        c.tendency_non_communication,
        c.tendency_severity,
        c.complaint_facility,
        c.complaint_instructor,
        c.complaint_trainee
    from counseling c,
    (
        select
            s.student_id,
            s.name,
            s.status,
            s.trnee_id,
            s.training_id
        from student s
        where s.training_id in
            (select training_id from training where trainee_key_allowed = :trainee_key_allowed)
    ) b
    where c.student_id = b.student_id
        AND b.training_id = :training_id
    order by c.counseling_date, b.training_id
    """)

    counsel_df = pd.read_sql(query, engine, params={"training_id":training_id, "trainee_key_allowed":trainee_key_allowed})

    counsel_df["counseling_date"] = pd.to_datetime(
        counsel_df["counseling_date"], errors="coerce"
    )

    return counsel_df

def get_counsel_feature(training_id, trainee_key_allowed) :
    counsel_df = get_hrd_counseling_data(training_id, trainee_key_allowed)

    label_df = (
        counsel_df
        .groupby("trnee_id")
        .agg(
            dropout_label=("status", lambda x: (x.max() == 4))
        )
        .reset_index()
    )
    label_df["dropout_label"] = label_df["dropout_label"].astype(int)   

    detailed_features = (
        counsel_df
        .groupby("trnee_id")
        .agg(
            # 건강 세부
            depression_count=("health_depression", "sum"),
            panic_count=("health_panic", "sum"),
            low_intel_count=("health_low_intelligence", "sum"),
            physical_issue_count=("health_physical", "sum"),

            # 가족 세부
            family_economic_count=("family_economic", "sum"),
            family_conflict_count=("family_conflict", "sum"),
            family_care_count=("family_care", "sum"),

            # 학습 세부
            motivation_decline_count=("learning_motivation_decline", "sum"),
            understanding_deficit_count=("learning_understanding_deficit", "sum"),
            bad_attitude_count=("learning_attitude", "sum"),
            career_confusion_count=("learning_career", "sum"),

            # 성향 세부
            avoidance_count=("tendency_avoidance", "sum"),
            attention_seeking_count=("tendency_attention_seeking", "sum"),
            selfish_count=("tendency_selfish", "sum"),
            non_communication_count=("tendency_non_communication", "sum"),
        )
        .reset_index()
    )

    risk_features = (
        counsel_df
        .assign(is_risk=lambda x: (x["counseling_type"] == "위험군 상담").astype(int))
        .groupby("trnee_id")
        .agg(
            has_risk_counseling=("is_risk", "max"),      # 한번이라도 있었는지
            risk_counseling_count=("is_risk", "sum"),    # 총 몇 번 있었는지
        )
        .reset_index()
    )

    severity_feature = (
        counsel_df
        .groupby("trnee_id")
        .agg(
            # 상담 횟수
            counsel_count=("counseling_id", "count"),

            # 건강 영역
            health_severity_avg=("health_severity", "mean"),
            health_severity_max=("health_severity", "max"),

            # 가족 영역
            family_severity_avg=("family_severity", "mean"),
            family_severity_max=("family_severity", "max"),

            # 학습 영역
            learning_severity_avg=("learning_severity", "mean"),
            learning_severity_max=("learning_severity", "max"),

            # 성향 영역
            tendency_severity_avg=("tendency_severity", "mean"),
            tendency_severity_max=("tendency_severity", "max"),

            # 민원 관련
            complaint_facility_sum=("complaint_facility", "sum"),
            complaint_instructor_sum=("complaint_instructor", "sum"),
            complaint_trainee_sum=("complaint_trainee", "sum"),
        )
        .reset_index()
    )
    severity_feature["total_severity_avg"] = (
        severity_feature["health_severity_avg"] +
        severity_feature["family_severity_avg"] +
        severity_feature["learning_severity_avg"] +
        severity_feature["tendency_severity_avg"]
    )
    
    final_counsel_df = (
        severity_feature
        .merge(detailed_features, on="trnee_id")
        .merge(risk_features, on="trnee_id")
        .merge(label_df, on="trnee_id")
        .fillna(0)
    )

    return final_counsel_df