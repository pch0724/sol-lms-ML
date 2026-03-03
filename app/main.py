from fastapi import FastAPI
from app.api import predict
from ml.scheduler.training_scheduler import start_scheduler
from models.model_manage import load_model

app = FastAPI(title="SOL-LMS-ML")
app.include_router(predict.router)

model = None

# 서버 기동 시 스케쥴러 시작
@app.on_event("startup")
def startup_event():
    # 최초 기동 시 모델 로드
    load_model()
    # ML 스케쥴러 시작
    start_scheduler()

@app.get("/")
def root():
    return {"message": "SOL-LMS-ML API running"}