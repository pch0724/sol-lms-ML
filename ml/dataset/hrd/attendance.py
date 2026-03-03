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

from ml.dataset.common.training import get_hrd_trainings

def get_hrd_attendance() :
    api_base_url = os.getenv("HRD_ATTEND_URL")
    api_keys = os.getenv("HRD_AUTH_KEY")

    training_list = get_hrd_trainings()
    hrd_attendance_by_training = []
    today = pd.Timestamp.today().replace(day=1)

    session = create_session()

    for training in training_list.itertuples(index=False) :
        current = training.training_start_date.replace(day=1)        
        end = training.training_end_date.replace(day=1)

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
            except requests.RequestException as e:        
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
    
    return hrd_attendance_by_training

def modify_hrd_attendance() :

    hrd_attendance_by_training = get_hrd_attendance()

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

    return df_att

def get_hrd_feature() :
    
    hrd_attendance_by_training = modify_hrd_attendance()
    df_att = pd.DataFrame(hrd_attendance_by_training)
    attendance_features = (
        df_att
        .groupby("trneeCstmrId")
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

