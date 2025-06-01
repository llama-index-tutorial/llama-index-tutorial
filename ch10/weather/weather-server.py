from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from mcp.server.fastmcp import FastMCP
from llama_index.core.llms import ChatMessage
import requests
import os

load_dotenv()

weatherapi_key = os.getenv("WEATHER_API_KEY")
llm = OpenAI(model="gpt-4o-mini")

mcp = FastMCP('weather-server')

def extract_city_name_with_llm(query: str) -> str:
    prompt = (
        f"다음 문장에서 날씨를 묻는 도시명이 있다면 그 도시명을 영어로만 출력하세요. "
        f"도시가 없다면 반환하지 않습니다. 오직 도시명 하나만 영어로 출력하세요.\n"
        f"예: Seoul, Busan, Jeju\n"
    )
    
    messages = [
        ChatMessage(role="system", content=prompt),
        ChatMessage(role="user", content=query),
    ]
    
    response = llm.chat(
        messages=messages,
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=10,
    )
    return response.message.content.strip()


def get_geo(city: str, limit: int=1) -> str:
    """도시명을 입력받아 OpenWeatherMap 지오코딩 API를 호출하여 위도와 경도를 가져옴"""
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={limit}&appid={weatherapi_key}"
    
    res = requests.get(url)
    data = res.json()
    return data[0]


def get_today_weather(city: str) -> str:
    """[오늘 날씨 조회 API] OpenWeatherMap current weather API를 이용해 오늘 현재 날씨를 조회"""
    geo = get_geo(city)
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={geo['lat']}&lon={geo['lon']}&appid={weatherapi_key}"
    
    res = requests.get(url)
    if res.status_code != 200:
        return f"{city}의 날씨 정보를 가져오지 못했습니다."

    data = res.json()

    city = data["name"]
    temp_k = data["main"]["temp"]
    feelslike_k = data["main"]["feels_like"]
    condition = data["weather"][0]["description"]

    # 켈빈(K) -> 섭씨(°C)로 변환
    temp_c = round(temp_k - 273.15, 1)
    feelslike_c = round(feelslike_k - 273.15, 1)

    return f"{city}의 현재 날씨는 {condition}, 기온은 {temp_c}°C, 체감온도는 {feelslike_c}°C입니다."


from datetime import datetime, timedelta

def get_tomorrow_weather(city: str) -> str:
    """[내일 날씨 조회 API] OpenWeatherMap forecast API를 이용해 내일 날씨를 조회"""
    geo = get_geo(city)
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={geo['lat']}&lon={geo['lon']}&appid={weatherapi_key}"
    
    res = requests.get(url)
    if res.status_code != 200:
        return f"{city}의 내일 날씨 정보를 가져오지 못했습니다."

    data = res.json()
    tomorrow = datetime.utcnow() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")

    # 내일 중 정오 (12:00:00) 시간 데이터 우선
    tomorrow_forecasts = [item for item in data["list"] if item["dt_txt"].startswith(tomorrow_str)]
    target = next((item for item in tomorrow_forecasts if "12:00:00" in item["dt_txt"]), tomorrow_forecasts[0])

    temp_k = target["main"]["temp"]
    condition = target["weather"][0]["description"]
    temp_c = round(temp_k - 273.15, 1)

    return f"{city}의 내일 날씨는 {condition}, 예상 기온은 {temp_c}°C입니다."


@mcp.tool()
def today_weather_query(city: str = None) -> str:
    """[MCP Tool] 파라미터로 받은 도시 또는 세션의 도시로 오늘 날씨를 반환"""
    print(f"[today_weather_query] city={city}")

    if city is None:
        return "도시 정보가 없습니다. 먼저 도시명을 알려주세요."

    return get_today_weather(city)

@mcp.tool()
def tomorrow_weather_query(city: str = None) -> str:
    """[MCP Tool] 파라미터로 받은 도시 또는 세션의 도시로 내일 날씨를 반환"""
    print(f"[tomorrow_weather_query] city={city}")

    if city is None:
        return "도시 정보가 없습니다. 먼저 도시명을 알려주세요."

    return get_tomorrow_weather(city)

if __name__ == "__main__":

    query = "서울 오늘 날씨 알려줘"
    print(extract_city_name_with_llm(query))

    query = "부산 내일 비오나요?"
    print(extract_city_name_with_llm(query))
    
    city_info = get_geo("Seoul")
    print(city_info['lat'], city_info['lon'])

    today_weather = get_today_weather("Seoul")
    print(today_weather)
    
    tomorrow_weather = get_tomorrow_weather("Seoul")
    print(tomorrow_weather)

    mcp.run(transport="sse")