import feedparser
import requests
import datetime

# ✅ 설정
OPENAI_API_KEY = "sk-..."  # ← OpenAI API 키 입력
TEAMS_WEBHOOK_URL = "https:..."  # ← Teams Webhook URL 입력
KEYWORD = "다이소"
RSS_FEED = f"https://news.google.com/rss/search?q={KEYWORD}&hl=ko&gl=KR&ceid=KR:ko"

# 1️⃣ 뉴스 10개 수집
feed = feedparser.parse(RSS_FEED)
articles = feed.entries[:10]  # ← 10개 이상으로 변경
if len(articles) < 5:
    raise Exception("뉴스 수가 너무 적습니다. 키워드 또는 RSS 피드를 확인하세요.")

# 2️⃣ 뉴스 리스트 정리
news_items = []
for i, entry in enumerate(articles, 1):
    news_items.append(f"{i}. 제목: {entry.title}\n   링크: {entry.link}")

news_block = "\n".join(news_items)

# 3️⃣ GPT 프롬프트 구성
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
prompt = f"""
다음은 '{KEYWORD}'와 관련된 최근 뉴스 기사 10건입니다.
이 내용을 기반으로 다음 형식에 따라 한국어 리서치 리포트를 작성해 주세요.

📢 오늘의 {KEYWORD} 시장 동향 리서치 요약

🔹 제목: [핵심 키워드를 담은 분석 제목]

🔹 핵심 요약:
[전체 기사 흐름을 간결하지만 풍부하게 3~4줄로 요약]

🔹 주요 이슈 분석:
- [이슈 1: 설명]
- [이슈 2: 설명]
- ...

🔹 업계 및 시장 반응:
[시장/소비자/업계의 반응을 분석]

🔹 향후 전망 및 시사점:
[GPT 관점의 예측 및 조언 포함]

⏱ 리포트 생성 시각: {now}

뉴스 목록:
{news_block}
"""

# 4️⃣ GPT API 호출
headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "system", "content": "너는 시장 동향 분석 리포트를 작성하는 리서치 전문가야.핵심 내용, 배경, 영향 등을 포함해서 풍부하고 정확하게 설명해줘."},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.7
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
summary = response.json()["choices"][0]["message"]["content"]

# 5️⃣ Teams 전송
teams_payload = {
    "text": summary + "\n\n📰 참고 기사 목록:\n" + news_block
}
res = requests.post(TEAMS_WEBHOOK_URL, json=teams_payload)

# 6️⃣ 상태 출력
if res.status_code == 200:
    print("✅ Teams 전송 완료")
else:
    print(f"❌ Teams 전송 실패: {res.status_code}\n{res.text}")
