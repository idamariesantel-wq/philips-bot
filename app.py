import os
import json
import requests
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

SYSTEM_PROMPT = """You are a specialized analytics assistant for the Philips TikTok Shop Germany.
Answer questions precisely based on this data. Be concise and actionable.
Respond in the same language as the question (German if asked in German, English if asked in English).
Format answers clearly using bullet points and numbers where helpful.

COMPLETE DATA:

SHOP ANALYTICS JAN-MAY 2026:
Total GMV: EUR 1,714,996 | Orders: 55,353 | Customers: 54,093 | AOV: EUR 30.98 (down 7.42%)
LIVE GMV: EUR 118,712 (up 187.79%) | Video GMV: EUR 1,471,721 (up 548.39%) | Product Card GMV: EUR 124,563
Refunds Jan-May: EUR 143,163 (up 398%) | Best month: April 2026 ~EUR 325K
Monthly: Jan EUR 45.8K | Feb EUR 105K | Mar EUR 180K | Apr EUR 325K | May EUR 208K

LAUNCH NOV-DEC 2025:
Launch: Nov 26 2025 | First 36 days GMV: EUR 193,408 | Orders: 5,613
Black Friday Nov 28: EUR 16,885 (best single day) | Dec 4: EUR 916 (worst)
Dec 2025: EUR 153,353 | LIVE GMV dominated at EUR 252,966 (TikTok co-funding)

GMV MAX FULL YEAR MAY 2025 - MAY 2026:
Total spend: EUR 278,220 | Revenue: EUR 1,795,715 | ROI: 6.45x | Orders: 49,259
Product cards: 20.92x ROI vs videos 5.20x ROI - massively underinvested in cards
Budget split: Videos 92% (EUR 256K) vs Cards 8% (EUR 22K)

Campaigns by revenue:
- Facial Hair Remover 5000: EUR 104,707 spend -> EUR 702,080 revenue (6.71x) - OOS WARNING
- OneBlade Intimate: EUR 80,507 -> EUR 486,145 (6.04x)
- OneBlade Intimate Auto: EUR 42,990 -> EUR 285,628 (6.64x)
- OneBlade Face 360: EUR 26,639 -> EUR 178,975 (6.72x) - OOS WARNING
- Lumea 8000/9000: EUR 5,361 -> EUR 81,791 (15.26x) - HIGHEST ROI, LOW STOCK WARNING
- Beauty Set: EUR 303 -> EUR 357 (1.18x) - BROKEN, pause immediately

Top Creators GMV Max full year:
- Kristina: EUR 26,997 -> EUR 184,108 (6.82x) - #1 by revenue
- jonas.jamess: EUR 10,153 -> EUR 90,359 (8.90x)
- Starke Deals: EUR 278 -> EUR 39,609 (142x ROI) - massively underinvested
- reapez: EUR 25,616 -> EUR 51,740 (2.02x) + 79% refund rate - PAUSE ALL CAMPAIGNS NOW
- DorianLebt: EUR 6.70 -> EUR 764.87 (114x ROI) - best creative ever

LIVE GMV MAX:
Campaign 1 (Oct 31 2025): EUR 16,214 spend -> EUR 137,697 revenue (7.52x) - NOT DELIVERING
Account ID to reconnect: 7517310666145285142 | EUR 1,000/day budget idle

ADS MANAGER FULL YEAR:
Total spend: EUR 296,913 | Revenue: EUR 1,934,499 | ROI: 6.52x | CPO: EUR 5.64
Orders: 52,624 | Ads drove ~95% of all orders
Acquisition stack: Ads 15.3% + Commission 8.3% + Discounts 27.8% = ~51% before COGS

2026 CAMPAIGNS:
Spring Sale (Mar 24-Apr 1): EUR 272,850 GMV | 9,289 orders | CTOR 1.34%
April Deals (Apr 25-May 7): EUR 258,171 GMV | 8,033 orders | CTOR 1.41%
Spring Escape (May 13-18): EUR 89,531 GMV | CTOR 1.10%
February Deals: EUR 59,641 | Winter Sale: EUR 45,826 | Valentine Day: EUR 45,517
Summer Sale: LIVE NOW (May 26 - Jul 2)

CREATOR LIST MAY 18-24:
misstestet: EUR 15,509 GMV | 386 orders | 9% refunds | #1 performer
danbor00: EUR 2,207 | 65 orders | 23% refunds WARNING
jonas.jamess: EUR 2,197 | 73 orders | 28% refunds WARNING
deal_detektivin: EUR 2,018 | 66 orders | 4% refunds GOOD | 112x sample ROI
reapez: EUR 1,811 | 38 orders | 79% refunds CRITICAL - pause all campaigns
emmasbeautyy1: EUR 1,768 | 9 orders | 0% refunds PERFECT | EUR 196 AOV
dorianlebt: EUR 1,432 | 47 orders | 6% refunds | 114x GMV Max ROI
beautytalkmitanna: EUR 1,392 | 213K followers | never received sample
Cumulative affiliate GMV (8,241 creators): EUR 5,472,781

TRANSACTION ANALYSIS AUG 2025 - MAY 2026:
Creator GMV: EUR 1,705,441 | Refunds: EUR 130,002 (7.6%)
Commission: EUR 149,060 (8.74%) | Videos: 21,317 | LIVE streams: 2,624
Daily selling creators: 42 of 8,241 (0.5% activation rate - CRITICAL)
Daily LIVE with revenue: 2 of 9.7 (79% generate EUR 0)
Samples shipped: 2,457

PRODUCT CATALOGUE (May 26):
OUT OF STOCK: OneBlade Intimate, Facial Hair Remover 5000, OneBlade Hair-Free Set,
Body and Balls (2 variants), OneBlade Duo Set, OneBlade Face 360
LOW STOCK: Lumea Series 8000 (CRITICAL - runs 15x ROI campaign)

AFFILIATE MAY 11-24:
GMV: EUR 58,757 | Refunds: EUR 14,616 (24.9% CRITICAL) | Commission: EUR 4,841

PROMO TOOLS MAY 19-25:
88.62% of shop GMV uses promotions | Discount given: EUR 13,795 | AOV: EUR 36.33

LIVE PERFORMANCE APR-MAY:
Best day: Apr 30 EUR 7,816 | Apr 28-30 = EUR 20,000 in 3 days (structured selling)
Rest of May: ~EUR 7,000 total

OUTREACH MAY 3-9:
544 contacted | 46 accepted (8.5%) | 401 no reply

PRODUCT CARD MAY 18-24:
636,244 views | EUR 4,433 GMV | Cart-to-paid declining: 12.45% to 8.53%

FORECASTS:
Jun 2026: EUR 185-210K | Jul: EUR 140-165K | Aug: EUR 120-145K
Sep: EUR 185-210K | Oct: EUR 210-260K
Black Friday Nov 28 2026: EUR 35-50K single day potential
Full year 2026 target: EUR 2.7-2.8M
3-year: 2026 EUR 2.7M | 2027 EUR 3-5M | 2028 EUR 6-10M

TOP PRIORITY ACTIONS:
1. Restock 7+ OOS SKUs today
2. Pause reapez from all 11 campaigns (79% refund rate)
3. Fix LIVE GMV Max Campaign 1 (reconnect account ID: 7517310666145285142)
4. Pause Beauty Set GMV Max (EUR 0 revenue)
5. Brief DorianLebt for 5+ new videos (114x ROI)
6. Scale Lumea 8000/9000 GMV Max (15.26x ROI)
7. Scale Starke Deals (142x ROI on EUR 278 spend)"""


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
        return f"Error: {str(e)}"
    return "Sorry, could not get an answer. Please try again."


seen = set()


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return jsonify({"status": "ok"})

    # Try to parse body
    try:
        body = request.get_json(force=True, silent=True) or {}
    except Exception:
        return jsonify({"challenge": ""})

    # Handle Feishu URL verification (both v1 and v2)
    if "challenge" in body:
        challenge = body.get("challenge", "")
        resp = make_response(json.dumps({"challenge": challenge}))
        resp.headers["Content-Type"] = "application/json"
        return resp

    if body.get("type") == "url_verification":
        challenge = body.get("challenge", "")
        resp = make_response(json.dumps({"challenge": challenge}))
        resp.headers["Content-Type"] = "application/json"
        return resp

    # Get event data
    header = body.get("header", {})
    event = body.get("event", {})

    # Only handle message events
    event_type = header.get("event_type", "") or body.get("event", {}).get("type", "")
    if "message" not in str(event_type).lower() and "receive" not in str(event_type).lower():
        # Try old format
        if body.get("event", {}).get("type") not in ["message", None]:
            return jsonify({"code": 0})

    msg = event.get("message", {})
    if not msg:
        msg = event

    msg_id = msg.get("message_id", "") or body.get("event", {}).get("message_id", "")

    # Deduplicate
    if msg_id and msg_id in seen:
        return jsonify({"code": 0})
    if msg_id:
        seen.add(msg_id)

    # Get message text
    try:
        content_raw = msg.get("content", "") or event.get("text", "")
        if isinstance(content_raw, str) and content_raw.startswith("{"):
            content = json.loads(content_raw)
            text = content.get("text", "").strip()
        else:
            text = str(content_raw).strip()
        # Remove @mentions
        text = text.replace("\uff20", "").strip()
        import re
        text = re.sub(r'@\S+', '', text).strip()
    except Exception:
        return jsonify({"code": 0})

    if not text:
        return jsonify({"code": 0})

    chat_id = msg.get("chat_id", "") or event.get("open_chat_id", "")
    if not chat_id:
        return jsonify({"code": 0})

    # Get answer and reply
    answer = ask_claude(text)
    send_reply(chat_id, answer)

    return jsonify({"code": 0})


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "Philips Analytics Bot running", "version": "2.0"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
