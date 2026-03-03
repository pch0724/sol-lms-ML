import joblib
from threading import Lock

model = None
model_lock = Lock()

MODEL_PATH = "hrd_dropout_model.pkl"

def load_model() : 
    global model
    with model_lock:
        model = joblib.load(MODEL_PATH)
    print("Model Load Complete")

def get_model() :
    with model_lock:
        return model
    
def update_model(new_model):
    global model
    with model_lock :
        model = new_model
    print("Model Update Complete")