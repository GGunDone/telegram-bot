import requests
import json
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv("config.env")

# Конфигурация
TOKEN = os.getenv("BOT_TOKEN")
BONUS_URL = "https://vodka5.xyz?id=14245"
IMAGE_PATH = "bot.jpg.jpg"

# Файл для хранения данных пользователей
USERS_FILE = "users_data.json"

# Загружаем данные пользователей
def load_users_data():
    """Загружает данные пользователей из файла"""
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users_data(users_data):
    """Сохраняет данные пользователей в файл"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)

# Загружаем данные при запуске
users_data = load_users_data()

def send_message(chat_id, text, reply_markup=None):
    """Отправка сообщения в Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    
    response = requests.post(url, data=data)
    return response.json()

def send_photo(chat_id, photo_path, caption, reply_markup=None):
    """Отправка фото в Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    data = {
        "chat_id": chat_id,
        "caption": caption,
        "parse_mode": "HTML"
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    
    try:
        with open(photo_path, 'rb') as photo:
            files = {"photo": photo}
            response = requests.post(url, data=data, files=files)
            return response.json()
    except FileNotFoundError:
        return send_message(chat_id, caption, reply_markup)

def get_updates(offset=None):
    """Получение обновлений от Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    
    response = requests.get(url, params=params)
    return response.json()

def handle_message(message):
    """Обработка сообщения"""
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message.get("text", "")
    
    # Обновляем данные пользователя
    current_time = datetime.now().isoformat()
    users_data[str(user_id)] = {
        "chat_id": chat_id,
        "last_interaction": current_time,
        "username": message["from"].get("username", ""),
        "first_name": message["from"].get("first_name", "")
    }
    save_users_data(users_data)
    
    if text == "/start":
        # Создаем кнопку
        keyboard = {
            "inline_keyboard": [
                [{"text": "Забрать бонус", "url": BONUS_URL}]
            ]
        }
        
        # Текст сообщения
        caption = (
            "WELCOME-БОНУС на первый деп! 🎁\n\n"
            "1. Запускаешь бота\n"
            "2. Тапаешь по кнопке снизу\n"
            "3. Лутаешь +100% к пополнению и 100 FS в The Dog House\n\n"
            "Боровы, вы чё, реально ещё не забрали свой первый бонус? 🤔\n"
            "У вас ещё 3 валяются без дела — в сумме 300 FS\n\n"
            "Жми «Забрать бонус» и пошла возня 🚀🔥"
        )
        
        send_photo(chat_id, IMAGE_PATH, caption, keyboard)
        
    elif text == "/push_news":
        # Команда для отправки push-уведомления (только для админа)
        if str(user_id) == "YOUR_ADMIN_ID":  # Замените на ваш Telegram ID
            send_message(chat_id, "🚀 Отправляем push-уведомление всем пользователям...")
            sent, failed = send_news_update()
            send_message(chat_id, f"✅ Push-рассылка завершена!\nОтправлено: {sent}\nОшибок: {failed}")
        else:
            send_message(chat_id, "❌ У вас нет прав для выполнения этой команды")
            
    elif text == "/stats":
        # Статистика бота
        total_users = len(users_data)
        active_today = 0
        current_date = datetime.now().date()
        
        for user_data in users_data.values():
            last_interaction = datetime.fromisoformat(user_data["last_interaction"]).date()
            if last_interaction == current_date:
                active_today += 1
        
        stats_text = (
            f"📊 Статистика бота:\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"📅 Активных сегодня: {active_today}\n"
            f"🕐 Время: {datetime.now().strftime('%H:%M:%S')}"
        )
        send_message(chat_id, stats_text)
        
    else:
        response_text = "🤖 Привет! Используй команду /start для получения бонуса!"
        send_message(chat_id, response_text)

def check_and_send_reminders():
    """Проверяет пользователей и отправляет напоминания через 7 дней"""
    current_time = datetime.now()
    reminders_sent = 0
    
    for user_id, user_data in users_data.items():
        try:
            last_interaction = datetime.fromisoformat(user_data["last_interaction"])
            days_passed = (current_time - last_interaction).days
            
            # Если прошло 7 дней и пользователь не получал напоминание
            if days_passed >= 7 and not user_data.get("reminder_sent", False):
                chat_id = user_data["chat_id"]
                
                # Создаем кнопку для напоминания
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "Забрать бонус", "url": BONUS_URL}]
                    ]
                }
                
                # Текст напоминания
                reminder_text = (
                    "🎯 Напоминание о бонусе!\n\n"
                    "Привет! Прошла неделя, а ты так и не забрал свой бонус! 😏\n\n"
                    "🔥 +100% к пополнению\n"
                    "🎰 100 FS в The Dog House\n"
                    "💰 Дополнительные промокоды\n\n"
                    "Не упускай возможность! Жми кнопку ниже! 🚀"
                )
                
                # Отправляем напоминание
                send_message(chat_id, reminder_text, keyboard)
                
                # Отмечаем, что напоминание отправлено
                user_data["reminder_sent"] = True
                user_data["reminder_sent_date"] = current_time.isoformat()
                reminders_sent += 1
                
                print(f"Отправлено напоминание пользователю {user_id}")
                
        except Exception as e:
            print(f"Ошибка при отправке напоминания пользователю {user_id}: {e}")
    
    # Сохраняем обновленные данные
    if reminders_sent > 0:
        save_users_data(users_data)
        print(f"Отправлено {reminders_sent} напоминаний")

def send_push_notification(title, message, image_path=None, button_text="Узнать больше", button_url=None):
    """Отправляет push-уведомление всем пользователям"""
    sent_count = 0
    failed_count = 0
    
    print(f"Начинаем рассылку push-уведомления: {title}")
    
    for user_id, user_data in users_data.items():
        try:
            chat_id = user_data["chat_id"]
            
            # Создаем кнопку если указана
            keyboard = None
            if button_text and button_url:
                keyboard = {
                    "inline_keyboard": [
                        [{"text": button_text, "url": button_url}]
                    ]
                }
            
            # Отправляем сообщение с изображением или без
            if image_path and os.path.exists(image_path):
                send_photo(chat_id, image_path, message, keyboard)
            else:
                send_message(chat_id, message, keyboard)
            
            sent_count += 1
            print(f"Push отправлен пользователю {user_id}")
            
            # Небольшая задержка между отправками
            time.sleep(0.1)
            
        except Exception as e:
            failed_count += 1
            print(f"Ошибка при отправке push пользователю {user_id}: {e}")
    
    print(f"Push-рассылка завершена: отправлено {sent_count}, ошибок {failed_count}")
    return sent_count, failed_count

def send_news_update():
    """Отправляет обновление новостей всем пользователям"""
    title = "📢 НОВОСТИ И ОБНОВЛЕНИЯ!"
    
    message = (
        "🚀 У нас есть важные новости!\n\n"
        "✨ Новые бонусы и акции\n"
        "🎁 Дополнительные промокоды\n"
        "🔥 Увеличенные лимиты\n"
        "💎 Эксклюзивные предложения\n\n"
        "Не упусти возможность получить максимум! 💪\n"
        "Жми кнопку ниже и забирай свой бонус! 🎯"
    )
    
    button_text = "Забрать бонус"
    button_url = BONUS_URL
    
    return send_push_notification(title, message, IMAGE_PATH, button_text, button_url)

def main():
    """Основной цикл бота"""
    print("Бонус-бот запускается...")
    print("Бот готов к работе!")
    
    if not TOKEN:
        print("Ошибка: Не найден BOT_TOKEN в переменных окружения!")
        print("Создайте файл config.env с содержимым: BOT_TOKEN=ваш_токен")
        return
    
    offset = None
    last_reminder_check = datetime.now()
    
    while True:
        try:
            # Проверяем напоминания каждые 6 часов
            current_time = datetime.now()
            if (current_time - last_reminder_check).total_seconds() >= 6 * 3600:  # 6 часов
                check_and_send_reminders()
                last_reminder_check = current_time
            
            updates = get_updates(offset)
            
            if updates["ok"]:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    
                    if "message" in update:
                        handle_message(update["message"])
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\nБот остановлен пользователем")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
