import pandas as pd
from app.util.db_connect import db_connection

def getStudent():

    engine = db_connection()

    query = """
        SELECT * FROM student
    """

    df = pd.read_sql(query, engine)
    
    return df