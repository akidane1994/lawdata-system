from pydoc import resolve
import requests
import time

def fetch_law_data(law_id):
    """
    指定されたLawIDの法理データをe-gov APIからJSON形式で取得する。
    """
    url = f"https://laws.e-gov.go.jp/api/2/law_data/{law_id}"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0(LawMonitorBot/1.0)"
    }

    print(f"Fetching: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()


        # レスポンスがJSONか確認
        content_type = response.headers.get("Content-Type", "")
        if "json" in content_type or response.text.strip().startswith("{"):
            return response.json()
        else:
            print(f"Error: レスポンスがJSONではありません。Content-Type; {content_type}")
            return None

    except Exception as e:
        print(f"API Request Faild: {e}")
        return None