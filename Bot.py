import os
import requests
import time
from datetime import datetime

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8493334113:AAG0xhH5SEZ72APG4WrUjRrBAj1ilUWyZPo")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@Prostokirilllll")
ADMIN_USERNAME = "prostokiril"

print("=" * 50)
print("🤖 TELEGRAM BOT - RENDER.COM")
print("=" * 50)
print(f"Бот запущен: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
print(f"Канал: {CHANNEL_ID}")
print(f"Админ: @{ADMIN_USERNAME}")
print("=" * 50)

def send_message(chat_id, text, buttons=None):
    """Отправляет сообщение"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    if buttons:
        data["reply_markup"] = {"inline_keyboard": buttons}
    
    try:
        requests.post(url, json=data, timeout=5)
        return True
    except:
        return False

def check_subscription(user_id):
    """Проверяет подписку на канал"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
    data = {"chat_id": CHANNEL_ID, "user_id": user_id}
    
    try:
        r = requests.post(url, json=data, timeout=5).json()
        if r.get("ok"):
            status = r["result"]["status"]
            return status in ["member", "administrator", "creator"]
    except:
        pass
    return False

def is_admin(username):
    """Проверяет, админ ли пользователь"""
    return username and username.lower() == ADMIN_USERNAME.lower()

# ========== ОСНОВНОЙ ЦИКЛ ==========
def main():
    offset = 0
    
    while True:
        try:
            # Получаем обновления от Telegram
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {
                "offset": offset,
                "timeout": 25,
                "allowed_updates": ["message", "callback_query"]
            }
            
            response = requests.get(url, params=params, timeout=30).json()
            
            if response.get("ok") and response.get("result"):
                for update in response["result"]:
                    offset = update["update_id"] + 1
                    
                    # Обработка сообщений
                    if "message" in update and "text" in update["message"]:
                        msg = update["message"]
                        user_id = msg["from"]["id"]
                        chat_id = msg["chat"]["id"]
                        text = msg["text"]
                        name = msg["from"].get("first_name", "Пользователь")
                        username = msg["from"].get("username", "")
                        
                        # Команда /start
                        if text == "/start":
                            if is_admin(username):
                                send_message(
                                    chat_id,
                                    f"👑 <b>ПАНЕЛЬ ВЛАДЕЛЬЦА</b>\n\n"
                                    f"Привет, {name}!\n"
                                    f"Бот работает 24/7 на Render.com\n\n"
                                    f"📢 Канал: {CHANNEL_ID}\n"
                                    f"💰 Баланс: 999,999 монет\n"
                                    f"⚡ Статус: Активен"
                                )
                            else:
                                if check_subscription(user_id):
                                    send_message(
                                        chat_id,
                                        f"✅ <b>ДОБРО ПОЖАЛОВАТЬ, {name}!</b>\n\n"
                                        f"Ты подписан на канал!\n"
                                        f"Доступ открыт!\n\n"
                                        f"Напиши что-нибудь..."
                                    )
                                else:
                                    buttons = [
                                        [{"text": "📢 ПОДПИСАТЬСЯ НА КАНАЛ", "url": f"https://t.me/Prostokirilllll"}],
                                        [{"text": "✅ Я ПОДПИСАЛСЯ", "callback_data": "check_sub"}]
                                    ]
                                    send_message(
                                        chat_id,
                                        f"🔒 <b>ДОСТУП ЗАКРЫТ, {name}!</b>\n\n"
                                        f"Для использования бота нужно подписаться:\n"
                                        f"<b>{CHANNEL_ID}</b>\n\n"
                                        f"1. Нажми 'ПОДПИСАТЬСЯ НА КАНАЛ'\n"
                                        f"2. Подпишись\n"
                                        f"3. Нажми 'Я ПОДПИСАЛСЯ'",
                                        buttons
                                    )
                        
                        # Команда /status
                        elif text == "/status":
                            send_message(
                                chat_id,
                                f"📊 <b>СТАТУС БОТА</b>\n\n"
                                f"✅ Работает на Render.com\n"
                                f"⏰ Запущен: {datetime.now().strftime('%H:%M')}\n"
                                f"📢 Канал: {CHANNEL_ID}\n"
                                f"👑 Админ: @{ADMIN_USERNAME}"
                            )
                    
                    # Обработка нажатий кнопок
                    elif "callback_query" in update:
                        call = update["callback_query"]
                        call_id = call["id"]
                        user_id = call["from"]["id"]
                        message_id = call["message"]["message_id"]
                        chat_id = call["message"]["chat"]["id"]
                        
                        if call["data"] == "check_sub":
                            if check_subscription(user_id):
                                # Подписался
                                requests.post(
                                    f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                                    json={"callback_query_id": call_id}
                                )
                                
                                requests.post(
                                    f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                                    json={
                                        "chat_id": chat_id,
                                        "message_id": message_id,
                                        "text": "✅ <b>ОТЛИЧНО! ПОДПИСКА ПОДТВЕРЖДЕНА!</b>\n\n"
                                               "Теперь тебе доступны все функции бота!\n"
                                               "Напиши /start",
                                        "parse_mode": "HTML"
                                    }
                                )
                            else:
                                # Еще не подписался
                                requests.post(
                                    f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                                    json={
                                        "callback_query_id": call_id,
                                        "text": "❌ Вы еще не подписались на канал!",
                                        "show_alert": True
                                    }
                                )
            
            # Небольшая пауза
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            print(f"📡 Ошибка сети: {e}")
            time.sleep(5)
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            time.sleep(3)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    main()