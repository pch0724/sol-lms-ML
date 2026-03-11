import joblib
import traceback
import os
from apscheduler.schedulers.background import BackgroundScheduler
from ml.train import train_model
from models.model_manage import update_model, MODEL_PATH

scheduler = BackgroundScheduler()

def training_job():

    try:
        new_model = train_model()        
        # 모델 저장
        joblib.dump(new_model, MODEL_PATH + ".tmp")
        os.replace(MODEL_PATH + ".tmp", MODEL_PATH)
        update_model(new_model)
    except Exception:
        traceback.print_exc()

def start_scheduler():
    scheduler.add_job(training_job, "cron", day_of_week="4", hour="23", minute="0", second="0") # 매주 금요일 오후 11시 학습
    scheduler.start()        