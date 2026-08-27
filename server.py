import os, datetime, requests, re, json
from flask import Flask, jsonify, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
SEC_UA = os.getenv("SEC_USER_AGENT", "Whale13F/1.0 contact@example.com")

MANAGERS = [
    {"name":"Berkshire Hathaway","person":"Warren Buffett","cik":"0001067983","tier":"A+"},
    {"name":"Pershing Square","person":"Bill Ackman","cik":"0001336528","tier":"A"},
    {"name":"Appaloosa","person":"David Tepper","cik":"0001656456","tier":"A"},
    {"name":"Tiger Global","person":"Chase Coleman","cik":"0001167483","tier":"A-"},
    {"name":"Third Point","person":"Dan Loeb","cik":"0001040273","tier":"A-"},
    {"name":"Baupost","person":"Seth Klarman","cik":"0001061768","tier":"A"},
]

# 초기 관심종목 데이터: UI가 비어 보이지 않도록 제공하는 앱의 기본 watchlist.
# 실제 13F 원문은 SEC API의 최근 제출일을 별도로 표시합니다.
STOCKS = [
    {"symbol":"GOOGL","name":"Alphabet","score":94,"reason":"퀄리티 + 현금흐름 + AI"},
    {"symbol":"DHR","name":"Danaher","score":91,"reason":"장기 복리 + 헬스케어"},
    {"symbol":"MSFT","name":"Microsoft","score":90,"reason":"AI + 클라우드 + 해자"},
    {"symbol":"AMZN","name":"Amazon","score":89,"reason":"클라우드 + 광고 + 성장"},
    {"symbol":"META","name":"Meta Platforms","score":87,"reason":"광고 효율 + AI"},
]

@app.get("/")
def index():
    return send_from_directory(BASE, "index.html")

@app.get("/api/health")
def health():
    return jsonify(ok=True, updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat())

@app.get("/api/overview")
def overview():
    filings=[]
    for m in MANAGERS:
        item=dict(m)
        try:
            r=requests.get(
                f"https://data.sec.gov/submissions/CIK{m['cik']}.json",
                headers={"User-Agent":SEC_UA}, timeout=15
            )
            r.raise_for_status()
            d=r.json().get("filings",{}).get("recent",{})
            for i, form in enumerate(d.get("form",[])):
                if form in ("13F-HR","13F-HR/A"):
                    item["filing_date"]=d["filingDate"][i]
                    item["accession"]=d["accessionNumber"][i]
                    item["primary_document"]=d["primaryDocument"][i]
                    break
        except Exception as e:
            item["error"]="SEC 연결 지연"
        filings.append(item)
    return jsonify(
        updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        managers=filings, stocks=STOCKS
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT","10000")))
