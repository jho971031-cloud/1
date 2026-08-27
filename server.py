import os, datetime, requests
from flask import Flask, jsonify, send_from_directory

BASE=os.path.dirname(os.path.abspath(__file__))
app=Flask(__name__,static_folder=BASE,static_url_path="")
SEC_UA=os.getenv("SEC_USER_AGENT","Whale13F/1.0 contact@example.com")
MANAGERS={
 "Berkshire Hathaway (Buffett)":"0001067983",
 "Pershing Square (Ackman)":"0001336528",
 "Appaloosa (Tepper)":"0001656456",
 "Tiger Global (Coleman)":"0001167483",
 "Third Point (Loeb)":"0001040273",
 "Baupost (Klarman)":"0001061768",
}
@app.get("/")
def home(): return send_from_directory(BASE,"index.html")
@app.get("/<path:name>")
def static_files(name): return send_from_directory(BASE,name)
@app.get("/api/health")
def health(): return jsonify(ok=True,time=datetime.datetime.now(datetime.timezone.utc).isoformat())
@app.get("/api/13f/recent")
def recent():
 out=[]
 for name,cik in MANAGERS.items():
  try:
   r=requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json",
    headers={"User-Agent":SEC_UA},timeout=20); r.raise_for_status()
   d=r.json()["filings"]["recent"]
   for i,f in enumerate(d.get("form",[])):
    if f in ("13F-HR","13F-HR/A"):
     out.append({"manager":name,"filing_date":d["filingDate"][i],"form":f}); break
  except Exception as e: out.append({"manager":name,"error":str(e)})
 return jsonify(updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),filings=out)
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.getenv("PORT","10000")))
