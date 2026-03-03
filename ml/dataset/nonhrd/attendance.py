# dataframe 
import pandas as pd
from dateutil.relativedelta import relativedelta
# API 호출 관련
import requests
from app.util.session import create_session
import json
import time
# .env
import os

from app.util.db_connect import db_connection
from ml.dataset.common.training import get_hrd_trainings

def get_non_hrd_attendance() :
    engine = db_connection()

    query = """
        select 
            tnal.trnee_cstmr_id,
            tnal.cstmr_nm,
            tnal.attendance_state,
            tnal.atend_de,		
            t0.training_id,
            t0.training_name,
            t0.training_session,
            t0.training_start_date,
            t0.training_end_date 
        from training_non_api_log tnal 
        left join (
            select * from training t where t.trainee_key_allowed = 0 
        ) t0
        on tnal.training_id  = t0.training_id        
    """

    df_nhrd_attend = pd.read_sql(query, engine)
    return df_nhrd_attend

def modify_non_hrd_attendance() :
    df_att = pd.DataFrame(get_non_hrd_attendance())
    df_att["atend_de"] = pd.to_datetime(df_att["atend_de"], format="%Y%m%d")
    df_att = df_att.sort_values(["trnee_cstmr_id", "atend_de"])

    status_map_nh = {
        "0": 1,    # 출석
        "1": 0,    # 결석
        "2": 0.8,  # 휴가
        "3": 0.5,  # 지각
        "4": 0.4,  # 조퇴
        "5": 0.7,  # 외출
        "6": 0.3,  # 질병/입원
        "7": 0.2,  # 기타
    }

    df_att["attendance_score"] = df_att["attendance_state"].map(status_map_nh)
    df_att["attendance_score"] = df_att["attendance_score"].fillna(1)

    df_att["is_absent"] = (df_att["attendance_score"] == 0).astype(int)

    df_att["consecutive_absent"] = (
        df_att.groupby("trnee_cstmr_id")["is_absent"]
        .transform(lambda x: x * (x.groupby((x != x.shift()).cumsum()).cumcount() + 1))
    )

    return df_att

def get_hrd_feature() :
    
    hrd_attendance_by_training = modify_non_hrd_attendance()
    df_att = pd.DataFrame(hrd_attendance_by_training)
    attendance_features = (
        df_att
        .groupby("trnee_cstmr_id")
        .agg(
            total_days=("attendance_score", "count"),
            absence_days=("attendance_score", lambda x: (x == 0).sum()),
            absence_ratio=("attendance_score", lambda x: (x == 0).mean()),
            max_consecutive_absent=("consecutive_absent", "max"),
        )
        .reset_index()
    )

    attendance_features["has_5day_consecutive_absent"] = (
        attendance_features["max_consecutive_absent"] >= 5
    ).astype(int)

    return attendance_features
