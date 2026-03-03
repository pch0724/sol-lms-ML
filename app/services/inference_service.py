import pandas as pd
from app.schemas.input import PredictRequest
from app.services.feature.training import get_training_detail

def predict_dropout(req: PredictRequest):    

    training, isHrd = get_training_detail(training_id=req.trainingId)

    if(isHrd) :
        {
        # TODO 1. hrd 과정 - 훈련일지(출석정보)(API) -> feature
        # TODO 2. hrd 과정 - 상담(DB) -> feature
        # TODO 3. hrd 과정 feature 통합
        }
    else :
        {
        # TODO 3. non-hrd 과정 - 훈련일지(출석정보)(DB) -> feature
        # TODO 4. non-hrd 과정 - 상담(DB) -> feature
        # TODO 5. non-hrd 과정 feature 통합
        }
    
    # TODO 7. feature -> model -> prob

    # TODO 8. JAVA return feature 추출

    return 0.42