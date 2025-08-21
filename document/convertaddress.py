import json
import pandas as pd
import requests

# secrets.json에서 API 키 불러오기
with open("../secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
REST_API_KEY = secrets["KAKAO_API_KEY"]

def get_lat_lng(address):
    """주소를 기반으로 위도/경도 반환"""
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {REST_API_KEY}"}
    params = {"query": address, "size": 1}
    response = requests.get(url, headers=headers, params=params)
    
    # API 호출 상태 및 응답 내용 출력
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")

    if response.status_code != 200:
        return None, None
    
    data = response.json()
    if data["documents"]:
        doc = data["documents"][0]
        y = float(doc["y"])  # 위도
        x = float(doc["x"])  # 경도
        return y, x
    else:
        return None, None

# 엑셀 읽기
df = pd.read_csv("addresses.csv", encoding="cp949")

# 새 컬럼 추가
df["위도"] = ""
df["경도"] = ""

for idx, row in df.iterrows():
    address = row["소재지"]  # C열 주소 기준
    lat, lng = get_lat_lng(address)
    print(f"주소: {address} -> 위도: {lat}, 경도: {lng}")  # 여기 추가
    df.at[idx, "위도"] = lat
    df.at[idx, "경도"] = lng
    print(f"{idx+1}/{len(df)} 완료: {lat}, {lng}")

# 새 CSV로 저장
df.to_csv("addresses_with_coords.csv", index=False, encoding="utf-8-sig")
print("완료! addresses_with_coords.csv 확인")