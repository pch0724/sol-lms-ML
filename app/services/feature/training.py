import pandas as pd
from app.util.db_connect import db_connection

engine = db_connection()

def get_training_detail(training_id : int) :
    query = """
        select 
            tl.training_id, 
            tl.trpr_id, 
            tl.trpr_degr,
            t.training_name,
            t.training_start_date, 
            t.training_end_date,
            t.trainee_key_allowed 
        from training t , training_lookup tl 
        where t.training_id = tl.training_id
        	and t.training_id = :training_id
    """

    df = pd.read_sql(query,engine, params={"training_id": training_id})

    df["training_start_date"] = pd.to_datetime(df["training_start_date"], errors="coerce")
    df["training_end_date"] = pd.to_datetime(df["training_end_date"], errors="coerce")

    trainee_key_allowed = df["trainee_key_allowed"]

    return df, trainee_key_allowed
    
    
