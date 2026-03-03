import pandas as pd
from app.util.db_connect import db_connection

engine = db_connection()

def get_hrd_trainings() :
    query = """
        select 
            tl.training_id, 
            tl.trpr_id, 
            tl.trpr_degr,
            t.training_name,
            t.training_start_date, 
            t.training_end_date 
        from training t , training_lookup tl 
        where t.training_id = tl.training_id 
            and t.trainee_key_allowed = 1        
    """

    df = pd.read_sql(query,engine)

    df["training_start_date"] = pd.to_datetime(df["training_start_date"], errors="coerce")
    df["training_end_date"] = pd.to_datetime(df["training_end_date"], errors="coerce")

    return df

# TODO : 필요한지 확인해봐야함 2026.02.27 기준 사용 X
def get_non_hrd_trainings() :

    query = """
        select 
            tl.training_id, 
            tl.trpr_id, 
            tl.trpr_degr,
            t.training_name,
            t.training_start_date, 
            t.training_end_date              
        from training t , training_lookup tl
        where t.training_id = tl.training_id
            and t.trainee_key_allowed = 0
    """

    df = pd.read_sql(query, engine)

    df["training_start_date"] = pd.to_datetime(df["training_start_date"], errors="coerce")
    df["training_end_date"] = pd.to_datetime(df["training_end_date"], errors="coerce")

    return df