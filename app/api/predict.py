from fastapi import APIRouter
from app.schemas.input import PredictRequest
from app.services.inference_service import predict_dropout

router = APIRouter(prefix="/predict", tags=["predict"])

# @router.post("")
# def predict(req: StudentInput):
#     prob = predict_dropout(req)
#     return {"dropout_probability": prob}
@router.post("")
def predict(req: PredictRequest):
    
    predict_dropout(req)

    return {"message": "ok"}