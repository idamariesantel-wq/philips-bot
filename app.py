import os
import json
import re
import requests
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

SYSTEM_PROMPT = """You are a specialized analytics assistant for the Philips TikTok Shop Germany.
Answer questions precisely based on this data. Be concise and actionable.
Respond in the same language as the question (German if asked in German, English if asked in English).

COMPLETE DATA:

SHOP ANALYTICS JAN-MAY 2026:
Total GMV: EUR 1,714,996 | Orders: 55,353 | AOV: EUR 30.98 | Refunds: EUR 143,163
LIVE GMV: EUR 118,712 | Video GMV: EUR 1,471,721 | Product Card GMV: EUR 124,563
Monthly: Jan EUR 45.8K | Feb EUR 105K | Mar EUR 180K | Apr EUR 325K | May EUR 208K

LAUNCH NOV-DEC 2025:
Launch: Nov 26 2025 | First 36 days GMV: EUR 193,408 | Orders: 5,613
Black Friday Nov 28: EUR 16,885 best day | Dec 2025: EUR 153,353

GMV MAX FULL YEAR:
Spend: EUR 278,220 | Revenue: EUR 1,795,715 | ROI: 6.45x
- Facial Hair Remover 5000: EUR 702,080 revenue (6.71x) OOS
- OneBlade Intimate: EUR 486,145 (6.04x)
- Lumea 8000/9000: EUR 81,791 (15.26x) HIGHEST ROI low stock
- Beauty Set: EUR 357 (1.18x) BROKEN pause now
- Starke Deals: 142x ROI on EUR 278 spend - underinvested
- DorianLebt: 114x ROI - best creative ever
- reapez: 2.02x ROI + 79% refunds - PAUSE ALL CAMPAIGNS

LIVE GMV MAX:
Campaign 1: EUR 16,214 spend -> EUR 137,697 revenue (7.52x) NOT DELIVERING
Reconnect account ID: 7517310666145285142

ADS MANAGER:
Spend: EUR 296,913 | Revenue: EUR 1,934,499 | ROI: 6.52x | CPO: EUR 5.64

CAMPAIGNS 2026:
Spring Sale: EUR 272,850 | April Deals: EUR 258,171 | Summer Sale LIVE NOW

CREATORS MAY 18-24:
misstestet: EUR 15,509 | 9% refunds | #1
reapez: EUR 1,811 | 79% refunds CRITICAL
dorianlebt: EUR 1,432 | 114x GMV Max ROI
deal_detektivin: EUR 2,018 | 4% refunds | 112x sample ROI
emmasbeautyy1: EUR 1,768 | 0% refunds | EUR 196 AOV

OOS PRODUCTS: OneBlade Intimate, Facial Hair Remover 5000, OneBlade Face 360, Body and Balls, OneBlade Duo Set
LOW STOCK: Lumea 8000 CRITICAL

FORECASTS:
Jun: EUR 185-210K | Jul: EUR 140-165K | Aug: EUR 120-145K | Sep: EUR 185-210K | Oct: EUR 210-260K
Black Friday 2026: EUR 35-50K | Full year 2026: EUR 2.7-2.8M

TOP PRIORITIES:
1. Restock OOS SKUs today
2. Pause reapez from all campaigns
3. Fix LIVE GMV Max Campaign 1
4. Brief DorianLebt for new videos
5. Scale Lumea and Starke Deals"""


def get_token():
    r = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
    )
    return r.json().get("tenant_access_token", "")


def send_reply(chat_id, text):
    token = get_token()
    requests.post(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"receive_id": chat_id, "msg_type": "text", "content": json.dumps({"text": text})}
    )


def ask_claude(question):
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": question}]
            },
            timeout=30
        )
        data = r.json()
        if data.get("content"):
            return data["content"][0]["text"]
    except Exception as e:
        return f"Error contacting AI: {str(e)}"
    return "Sorry, could not get an answer."


seen = set()


@app.route("/", methods=["GET", "POST"])
def health():
    if request.method == "POST":
        raw = request.get_data(as_text=True)
        print(f"ROOT POST RAW: {raw[:500]}")
        try:
            body = json.loads(raw) if raw else {}
        except Exception:
            return make_response(json.dumps({"code": 0}), 200, {"Content-Type": "application/json"})
        
        if body.get("type") == "url_verification" or "challenge" in body:
            challenge = body.get("challenge", "")
            print(f"ROOT CHALLENGE: {challenge}")
            return make_response(json.dumps({"challenge": challenge}), 200, {"Content-Type": "application/json"})
        
        # Also handle messages at root
        return webhook()
    
    return make_response(json.dumps({"status": "ok"}), 200, {"Content-Type": "application/json"})


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # Always return proper JSON
    if request.method == "GET":
        return make_response(
            json.dumps({"code": 0, "msg": "ok"}),
            200,
            {"Content-Type": "application/json"}
        )

    # Get raw body
    raw = request.get_data(as_text=True)
    print(f"RAW BODY: {raw[:500]}")

    try:
        body = json.loads(raw) if raw else {}
    except Exception:
        return make_response(
            json.dumps({"code": 0}),
            200,
            {"Content-Type": "application/json"}
        )

    print(f"PARSED BODY KEYS: {list(body.keys())}")

    # Handle ALL possible challenge formats from Feishu
    # Format 1: {"challenge": "xxx", "token": "xxx", "type": "url_verification"}
    # Format 2: {"encrypt": "xxx"} (encrypted)
    # Format 3: nested under schema

    if body.get("type") == "url_verification" or "challenge" in body:
        challenge = body.get("challenge", "")
        print(f"CHALLENGE: {challenge}")
        resp = make_response(
            json.dumps({"challenge": challenge}),
            200,
            {"Content-Type": "application/json"}
        )
        return resp

    # Handle message events
    # Support both v1.0 and v2.0 event formats
    event = body.get("event", {})
    header = body.get("header", {})

    # v2.0 format
    msg = event.get("message", {})
    chat_id = msg.get("chat_id", "")
    msg_id = msg.get("message_id", "")
    content_raw = msg.get("content", "")

    # v1.0 format fallback
    if not chat_id:
        chat_id = event.get("open_chat_id", "")
        msg_id = event.get("message_id", "")
        content_raw = event.get("text", "")

    if not chat_id:
        return make_response(json.dumps({"code": 0}), 200, {"Content-Type": "application/json"})

    # Deduplicate
    if msg_id in seen:
        return make_response(json.dumps({"code": 0}), 200, {"Content-Type": "application/json"})
    if msg_id:
        seen.add(msg_id)

    # Extract text
    try:
        if isinstance(content_raw, str) and content_raw.strip().startswith("{"):
            content_obj = json.loads(content_raw)
            text = content_obj.get("text", "").strip()
        else:
            text = str(content_raw).strip()
        text = re.sub(r'@[^\s]+', '', text).strip()
    except Exception:
        text = ""

    if not text:
        return make_response(json.dumps({"code": 0}), 200, {"Content-Type": "application/json"})

    answer = ask_claude(text)
    send_reply(chat_id, answer)

    return make_response(json.dumps({"code": 0}), 200, {"Content-Type": "application/json"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
