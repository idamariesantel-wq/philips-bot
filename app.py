import os
import json
import re
import requests
from flask import Flask, request, make_response

app = Flask(__name__)

FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

SYSTEM_PROMPT = """You are a specialized analytics assistant for the Philips TikTok Shop Germany.
Answer questions precisely based on this data. Be concise and actionable.
Respond in the same language as the question (German if asked in German, English if asked in English).
Do not use markdown formatting like **bold** or *italic* — use plain text only.

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

CREATOR LIST FEB 28 - MAY 27 2026 (3 months, 36,394 creators total):
Top 20 by GMV with refund rates:
1. misstestet: EUR 94,201 GMV | 2,921 orders | 7.3% refunds | 13,637 followers
2. jonas.jamess: EUR 67,803 GMV | 2,393 orders | 5.7% refunds | 24,548 followers
3. reapez: EUR 54,728 GMV | 1,393 orders | 9.2% refunds 3-month (79% was 1-week spike) | 17,922 followers
4. fundkugel: EUR 38,634 GMV | 1,441 orders | 4.3% refunds | 3,210 followers
5. netterhase: EUR 37,886 GMV | 1,266 orders | 6.4% refunds | 23,366 followers
6. diegotestet: EUR 36,722 GMV | 1,190 orders | 5.7% refunds | 15,976 followers
7. produktguru: EUR 30,046 GMV | 1,095 orders | 7.6% refunds | 93,413 followers
8. beautytalkmitanna: EUR 27,429 GMV | 1,055 orders | 11.0% refunds | 213,190 followers
9. danbor00: EUR 26,590 GMV | 818 orders | 8.2% refunds | 326,103 followers
10. nr.1_trendvault: EUR 21,778 GMV | 743 orders | 9.2% refunds | 19,894 followers
11. ttbestedeals: EUR 21,265 GMV | 697 orders | 5.9% refunds | 9,978 followers
12. marinus.bestfinds: EUR 20,586 GMV | 753 orders | 4.6% refunds | 31,605 followers
13. deal_detektivin: EUR 14,571 GMV | 496 orders | 2.4% refunds | 7,003 followers - BEST refund rate
14. hinatasdiary: EUR 14,464 GMV | 524 orders | 4.2% refunds | 15,953 followers
15. nextlivinghub: EUR 14,051 GMV | 566 orders | 5.6% refunds | 16,160 followers
16. hamburg.411: EUR 12,918 GMV | 440 orders | 6.7% refunds | 35,169 followers
17. vani_de_paris_: EUR 12,585 GMV | 627 orders | 5.0% refunds | 10,609 followers
18. adrian.ptrc: EUR 12,368 GMV | 441 orders | 4.3% refunds | 10,285 followers
19. gigi_skinvia: EUR 11,686 GMV | 459 orders | 6.8% refunds | 2,942 followers
20. vinzenz.mp4: EUR 11,313 GMV | 417 orders | 7.5% refunds | 18,780 followers

Key insight: reapez 79% refund rate was a 1-week anomaly. 3-month rate is 9.2% which is above average but not critical.
Best quality creator: deal_detektivin with only 2.4% refunds over 3 months.
Highest follower count in top 20: danbor00 with 326,103 followers.
beautytalkmitanna has 213,190 followers with 11% refunds - worth monitoring.

AFFILIATE CORE STATS FEB 28 - MAY 27 2026:
Total Affiliate GMV: EUR 991,010 | LIVE GMV: EUR 8,523 | Video GMV: EUR 975,766
Items sold: 32,677 | Est. commission: EUR 87,022
Refunded GMV: EUR 87,791 (8.9% overall refund rate)
Items refunded: 2,233 | Collaborations: 14,416
LIVE streams: 1,350 | Shoppable videos: 13,406lade Intimate, Facial Hair Remover 5000, OneBlade Face 360, Body and Balls, OneBlade Duo Set
LOW STOCK: Lumea 8000 CRITICAL

FORECASTS:
Jun: EUR 185-210K | Jul: EUR 140-165K | Aug: EUR 120-145K | Sep: EUR 185-210K | Oct: EUR 210-260K
Black Friday 2026: EUR 35-50K | Full year 2026: EUR 2.7-2.8M


PRODUCT CARD LIST MAY 21-27 2026 (per SKU performance):
Ranked by GMV:
1. OneBlade Intimate QP1924/22+30: GMV EUR 1,787 | Conversion 0.14% | 39,836 viewers - BEST OVERALL
2. OneBlade 360 Face+Body QP4631/65: GMV EUR 498 | Conversion 0.01% | 86,372 viewers - most traffic
3. Lumea Series 8000 BRI945/00: GMV EUR 315 | Conversion 0.01% | 23,326 viewers
4. OneBlade SkinProtect Klinge QP219/52: GMV EUR 144 | Conversion 0.06% | 6,784 viewers
5. Sonicare 3100 HX4031/21: GMV EUR 144 | Conversion 0.01% | 8,294 viewers
6. Facial Hair Remover 5000 BRR454/00: GMV EUR 80 | Conversion 0.02% | 15,288 viewers
7. Nose & Ear Trimmer NT3650/16: GMV EUR 55 | Conversion 0.04% | 11,057 viewers
8. Avent Natural Response Bottle SCY670/02: GMV EUR 38 | Conversion 0.05% | 5,646 viewers
9. OneBlade 360 Blade QP410/50: GMV EUR 31 | Conversion 0.02% | 11,121 viewers

Zero GMV products (traffic but no sales):
- Skin LED Beauty Set BRE738/00: 25,505 viewers, 0% conversion
- Lumea 9000 BRI955/00: 11,696 viewers, 0.01% conversion, EUR 0
- OneBlade Face 360 QP2734/31: 6,601 viewers, 0% conversion - OOS
- Body & Balls BG3485/15: 1,461 viewers, 0% - OOS
- Sonicare S2 Ultra Soft HX6052/10: 1,425 viewers, 0.21% conversion but EUR 0 (too low traffic)

Key insight: OneBlade Intimate is #1 product by GMV AND conversion rate (0.14%) among revenue-generating products.
Facial Hair Remover has low GMV this week (EUR 80) because it is out of stock.

LIVE PERFORMANCE Feb 27 - May 27 2026 (3 months daily data):
Monthly LIVE GMV:
- Feb 2026: EUR 1,024 (programme just starting)
- Mar 2026: EUR 36,757 (strong ramp up)
- Apr 2026: EUR 34,752 (peak month)
- May 2026: EUR 8,842 (sharp decline)
Total 3-month LIVE GMV: EUR 81,375
Peak day: Apr 30 2026 EUR 7,816
Key insight: LIVE peaked in March-April during campaign periods then collapsed in May. 
Only 2 of ~9.7 daily LIVE streams generate any revenue.

VIDEO PERFORMANCE Feb 27 - May 27 2026 (3 months daily data):
Monthly Video GMV:
- Feb 2026: EUR 25,743 (early stage)
- Mar 2026: EUR 399,278 (Spring Sale ramp - massive growth)
- Apr 2026: EUR 299,267 (April Deals campaign)
- May 2026: EUR 278,829 (Spring Escape + Summer Sale start)
Total 3-month Video GMV: EUR 1,003,116
Peak day: Apr 28 2026 EUR 31,083
Key insight: Video GMV grew 15x from Feb to March driven by Spring Sale campaign.
Video is the dominant revenue channel at 98% of content GMV vs 2% LIVE.

TOP PRIORITIES:
1. Restock OOS SKUs today
2. Pause reapez from all campaigns
3. Fix LIVE GMV Max Campaign 1
4. Brief DorianLebt for new videos
5. Scale Lumea and Starke Deals"""


def clean_response(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'^#{1,3} (.+)$', r'\1:', text, flags=re.MULTILINE)
    return text.strip()


def get_token():
    r = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
        timeout=10
    )
    return r.json().get("tenant_access_token", "")


def send_reply(chat_id, text):
    try:
        token = get_token()
        requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"receive_id": chat_id, "msg_type": "text", "content": json.dumps({"text": text})},
            timeout=10
        )
    except Exception as e:
        print(f"SEND ERROR: {e}")


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
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 600,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": question}]
            },
            timeout=25
        )
        data = r.json()
        if data.get("content"):
            return clean_response(data["content"][0]["text"])
        if data.get("error"):
            return "Error: " + data["error"].get("message", "unknown")
    except Exception as e:
        return f"Error: {str(e)}"
    return "Sorry, could not get an answer."


import threading
seen = set()


def handle_event(body):
    event = body.get("event", {})
    msg = event.get("message", {})
    chat_id = msg.get("chat_id", "") or event.get("open_chat_id", "")
    msg_id = msg.get("message_id", "") or event.get("message_id", "")
    content_raw = msg.get("content", "") or event.get("text", "")

    if not chat_id:
        return make_response(json.dumps({"code": 0}), 200, {"Content-Type": "application/json"})

    if msg_id in seen:
        return make_response(json.dumps({"code": 0}), 200, {"Content-Type": "application/json"})
    if msg_id:
        seen.add(msg_id)

    try:
        if isinstance(content_raw, str) and content_raw.strip().startswith("{"):
            text = json.loads(content_raw).get("text", "").strip()
        else:
            text = str(content_raw).strip()
        text = re.sub(r'@[^\s]+', '', text).strip()
    except Exception:
        text = ""

    if not text:
        return make_response(json.dumps({"code": 0}), 200, {"Content-Type": "application/json"})

    def reply():
        answer = ask_claude(text)
        send_reply(chat_id, answer)

    t = threading.Thread(target=reply)
    t.daemon = True
    t.start()

    return make_response(json.dumps({"code": 0}), 200, {"Content-Type": "application/json"})


@app.route("/", methods=["GET", "POST"])
def root():
    if request.method == "POST":
        raw = request.get_data(as_text=True)
        try:
            body = json.loads(raw) if raw else {}
        except Exception:
            return make_response(json.dumps({"code": 0}), 200, {"Content-Type": "application/json"})
        if body.get("type") == "url_verification" or "challenge" in body:
            return make_response(json.dumps({"challenge": body.get("challenge", "")}), 200, {"Content-Type": "application/json"})
        return handle_event(body)
    return make_response(json.dumps({"status": "ok"}), 200, {"Content-Type": "application/json"})


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return make_response(json.dumps({"code": 0}), 200, {"Content-Type": "application/json"})
    raw = request.get_data(as_text=True)
    try:
        body = json.loads(raw) if raw else {}
    except Exception:
        return make_response(json.dumps({"code": 0}), 200, {"Content-Type": "application/json"})
    if body.get("type") == "url_verification" or "challenge" in body:
        return make_response(json.dumps({"challenge": body.get("challenge", "")}), 200, {"Content-Type": "application/json"})
    return handle_event(body)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
