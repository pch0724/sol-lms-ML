# dataframe 
import pandas as pd
from dateutil.relativedelta import relativedelta
# API 호출 관련
import requests as rq
from app.util.session import create_session
import json
import time
# .env
import os
from sqlalchemy import text

from app.util.db_connect import db_connection
from app.services.feature.training import get_training_detail

def get_attendance(training_id, trainee_key_allowed) :
    
    modified_feature = None
    
    if (trainee_key_allowed) : 
        modified_feature = hrd_training_attendance(training_id)    
    else : 
        modified_feature = non_hrd_training_attendance(training_id)

    return get_hrd_feature(modified_feature)

def hrd_training_attendance(training_id):

    api_base_url = os.getenv("HRD_ATTEND_URL")
    api_keys = os.getenv("HRD_AUTH_KEY")

    training_list= get_training_detail(training_id)
    
    hrd_attendance_by_training = []
    today = pd.Timestamp.today().replace(day=1)

    session = create_session()

    for training in training_list.itertuples(index=False) :
        current = training.training_start_date.replace(day=1)        
        end = training.training_end_date.replace(day=1)

        if training.student_cnt == 0 :
            continue
        
        if end > today : 
            end = today

        while current <= end :
            print(f"[{training.trpr_id}-{training.training_name}-{training.trpr_degr}회차] {current}출석상세 호출 중...")
            attend_mo = current.strftime("%Y%m")

            params = {
                "srchTrprId": training.trpr_id,
                "srchTrprDegr": training.trpr_degr,
                "atendMo": attend_mo,
                "srchTorgId": "student_detail",
                "authKey": api_keys,
                "outType": 2,
                "returnType": "JSON",          
            }

            try:
                response = session.get(
                    api_base_url,
                    params=params,
                    timeout=60,
                )
                response.raise_for_status()
            except rq.RequestException as e:        
                print(f"{e}")
                continue

            data = response.json()

            inner_str = data.get("returnJSON")
            inner_json = json.loads(inner_str)
            atab_list = inner_json.get("atabList", [])

            if atab_list:
                hrd_attendance_by_training.extend(atab_list)

            time.sleep(0.5)

            current += relativedelta(months=1)
    
    df_att = pd.DataFrame(hrd_attendance_by_training)
    df_att["atendDe"] = pd.to_datetime(df_att["atendDe"], format="%Y%m%d")
    df_att = df_att.sort_values(["trneeCstmrId", "atendDe"])

    status_map = {
        "01": 1,   # 정상출석
        "02": 0,   # 결석
        "03": 0.5, # 지각
        "05": 0.4, # 조퇴
    }

    df_att["attendance_score"] = df_att["atendSttusCd"].map(status_map)
    df_att["attendance_score"] = df_att["attendance_score"].fillna(1)

    df_att["is_absent"] = (df_att["attendance_score"] == 0).astype(int)

    df_att["consecutive_absent"] = (
        df_att.groupby("trneeCstmrId")["is_absent"]
        .transform(lambda x: x * (x.groupby((x != x.shift()).cumsum()).cumcount() + 1))
    )

    df_att = df_att.rename(
        columns={"trneeCstmrId":"trnee_cstmr_id"}
    )
    
    return df_att

def non_hrd_training_attendance(training_id):
    engine = db_connection()

    query = text("""
        select 
            tnal.trnee_cstmr_id,
            tnal.cstmr_nm,
            tnal.attendance_state,
            tnal.atend_de,		
            t0.training_id,
            t0.student_id,
            t0.training_name,
            t0.training_session,
            t0.training_start_date,
            t0.training_end_date 
        from training_non_api_log tnal 
        left join (
            select 
                t.training_id,
                t.training_name,
                t.training_session,
                t.training_start_date,
                t.training_end_date,
                t.status,
                t.trainee_key_allowed,
                s.student_id,
                s.trnee_id 
            from student s, training t   
            where s.training_id  = t.training_id 
                and t.trainee_key_allowed = 0 
        ) t0
        on tnal.trnee_cstmr_id   = t0.trnee_id 
        where tnal.training_id = :training_id
    """)

    df_nhrd_attend = pd.read_sql(query, engine, params={"training_id": training_id})
    
    df_att = pd.DataFrame(df_nhrd_attend)
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

def get_hrd_feature(modified_feature) :
    
    df_att = modified_feature
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