import requests
import sys

ENDPOINT = "http://localhost:8000/health"

def check_service_health():
    try:
        response = requests.get(ENDPOINT, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return False

if __name__ == "__main__":
    if check_service_health():
        sys.exit(0)
    else:
        sys.exit(1)