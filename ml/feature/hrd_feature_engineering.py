import pandas as pd
from ml.dataset.hrd.attendance import get_hrd_feature
from ml.dataset.hrd.counseling import get_counsel_feature

def build_hrd_features():

    attendance_feature = pd.DataFrame(get_hrd_feature())
    attendance_feature = attendance_feature.rename(
        columns={"trneeCstmrId": "trnee_id"}
    )

    counsel_feature = pd.DataFrame(get_counsel_feature())

    attendance_feature["trnee_id"] = attendance_feature["trnee_id"].astype(str)
    counsel_feature["trnee_id"] = counsel_feature["trnee_id"].astype(str)    

    final_features = (
        attendance_feature
        .merge(counsel_feature, on="trnee_id", how="left")
        .fillna(0)
    )

    return final_features