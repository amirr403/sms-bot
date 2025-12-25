import telebot
import requests
from bs4 import BeautifulSoup
import time
import threading
from telebot import types

# --- CONFIGURATION ---
BOT_TOKEN = '8404464902:AAEijTyNj5mU9RX4Rn0HtVS9ukZvvEd5pcY'
bot = telebot.TeleBot(BOT_TOKEN)

# APKI NEW COOKIES (Fresh)
COOKIES = {
    "cf_clearance": "wLd.kppdjuf0owY3_h5oT8c65MQUWemGMz0iYmXToEg-1766659431-1.2.1.1-.x.Og9d.hcJ.MayELjC971YcakAqgEfqV1RSKYGIKVVELendw3fI9fuw8Qln088Ik9Nptui7mAu1VZ8p4MC1z6CViK0NM5bmr4PjUdVrJaa56p9zK6Lh_7nZlfasHkqg_rGTh2OEJhV7.l7dx3C.7K9f1H5jdmbb1f0_KJ4EfwHOKlhkeYYankG_klQyHIw3gVrXoDjWpHSW2FV20feYJpHttxkZSnhEaabochpBsPM",
    "mnitnetworkcom_mhitauth": "gAAAAABpTO7uFN8mX9Q2Lt5fTPTJOYZByA8TAKkKInzVOcBHMhnK_igMsCmSPohOyQZjbP8A2yWEVdjXWDIMFcayiu-hHf-zGVEK65MgHoWiLlc86D3x3n4Yy1I1g5dbZ0F9JKpr5W1pX-F0V6UnDkApVDCeCajx-2BF1JuT3-_k_JwxP-cvCJVQS9DTbxIXiV8_aywtUY--aTIRxWTQ54TZcDU6_BN3FettkfC7LFw7WrsZL_9F_dUQI4i0u0uIA6YbecNNed8D0ET53U1zJzIs0CZVLYwngTFfyN9GDyfHWiWYpmFelbXHPTm_foiyjj6tBxkTJCg_Ke-kHqs6f62UG5Tjcfpxtmv3xtnSji2Abs0RM4724RxQPq66CbMIRVxRz-8NxGQKOUfI0TYYl9JYstVNYTUDL8-fycllm_YDM_xi7HbpHfRXeuN9DZo0qLj8dfitE6mldr2uZsP_Zykuq7tA5_ek2qF5-0WFHpqzOcc1mo2L1K4m9ugolBF022i3x3bPr8BA7MWAzTCvIE7vMoePunFJx6dpJnFhs05J3F0FVHSWDdmFGMkcI4tetbQmf_wSSaAjIwZdcmzsW90sWynbmHs3F7LbrxC6Kel5oD-L_tn_8gGGDUFyuPcA0U5ipxC8CXijtRTxUR01JRK7AYLdxEmqF7iiQHIPWfRTSA4DhYSlTqXwPeb7CCp2egbTJCFZW4TZROwkF7vX2sHVs1Ovppawc4b0LXS4Ea17zqjfYxtYd7E=",
    "mnitnetworkcom_session": "M_SESSION_3H2N0W6M8",
    "mnitnetworkcom_accountType": "user"
}

TARGET_URL = "https://v2.minitnetwork.com/dashboard/getnum?range=2290193469XXX"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://v2.minitnetwork.com/dashboard/index"
}

def monitor_otp(chat_id):
    bot.send_message(chat_id, "🔍 OTP Monitoring Started (Every 12s)...")
    last_otp = ""
    start_time = time.time()
    
    # 20 Minute tak check karega
    while time.time() - start_time < 1200:
        try:
            resp = requests.get(TARGET_URL, cookies=COOKIES, headers=headers, timeout=20)
            
            if "login" in resp.url.lower():
                bot.send_message(chat_id, "⚠️ Cookies Expired! Please get new ones.")
                break

            soup = BeautifulSoup(resp.text, 'html.parser')
            # Success badge dhoondna
            success_badge = soup.find('span', string=lambda x: x and 'success' in x.lower())
            
            if success_badge:
                parent = success_badge.find_parent()
                otp_element = parent.find_next_sibling() if parent else None
                if otp_element:
                    raw_text = otp_element.get_text().strip()
                    otp_found = "".join(filter(str.isdigit, raw_text))
                    
                    if otp_found and len(otp_found) >= 4 and otp_found != last_otp:
                        bot.send_message(chat_id, f"✅ *NEW OTP:* `{otp_found}`", parse_mode="Markdown")
                        last_otp = otp_found
            
        except Exception as e:
            print(f"Monitoring Error: {e}")
            
        time.sleep(12)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("➕ Get New Number", callback_data="get_num")
    markup.add(btn)
    bot.send_message(message.chat.id, "🤖 SMS Bot with Fresh Cookies is Online!\n\nPress the button below:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "get_num")
def callback_get_number(call):
    bot.answer_callback_query(call.id, "Requesting Number...")
    try:
        # Trigger number refresh
        requests.get(TARGET_URL, cookies=COOKIES, headers=headers, timeout=20)
        bot.send_message(call.message.chat.id, "✅ Request sent! Waiting for OTP...")
        threading.Thread(target=monitor_otp, args=(call.message.chat.id,)).start()
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Network Error: {e}")

# Simple test command to check if bot is alive
@bot.message_handler(func=lambda m: True)
def echo_all(m):
    bot.reply_to(m, "I am alive! Use /start to see the button.")

if __name__ == "__main__":
    print("🚀 Bot is starting on Termux...")
    bot.infinity_polling()
