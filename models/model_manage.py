import joblib
from threading import Lock

model_bundle = None
model_lock = Lock()

MODEL_PATH = "hrd_dropout_model.pkl"

def load_model():
    global model_bundle
    with model_lock:
        model_bundle = joblib.load(MODEL_PATH)
    print("Model Load Complete")

def get_model_bundle():
    with model_lock:
        return model_bundle
    
def update_model(new_bundle):
    global model_bundle
    with model_lock:
        model_bundle = new_bundle
    print("Model Update Complete")