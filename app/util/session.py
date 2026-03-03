import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session():
    session = requests.Session()

    retry = Retry(
        total=5,                  # 최대 5번 재시도
        backoff_factor=2,         # 2초 → 4초 → 8초 → 16초
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)

    return session