# dataframe 
import pandas as pd
from dateutil.relativedelta import relativedelta
# API 호출 관련
import requests
from app.util.session import create_session
import json
import time
# .env
import os

from app.services.feature.training import get_training_detail

def get_attendance() :
    return 1