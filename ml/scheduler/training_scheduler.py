import joblib
import traceback
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from ml.train import train_model
from models.model_manage import update_model, MODEL_PATH

scheduler = BackgroundScheduler()

def training_job():
    print(f"[{datetime.now()}] 🧠 training job triggered")

    try:
        new_model = train_model()        
        # 모델 저장
        joblib.dump(new_model, MODEL_PATH + ".tmp")

        os.replace(MODEL_PATH + ".tmp", MODEL_PATH)

        update_model(new_model)
        print("✅ Model training completed")
    except Exception as e:
        print("❎ Model training failed")
        print("Error : ", str(e))
        traceback.print_exc()

def start_scheduler():
    scheduler.add_job(training_job, "cron", hour="0", minute="0", second="0")
    # scheduler.add_job(training_job, "interval", minutes=3)
    # scheduler.add_job(training_job, "interval", seconds=5)
    scheduler.start()        