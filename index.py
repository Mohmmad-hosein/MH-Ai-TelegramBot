import requests
import telebot
from telebot import types
import time
import logging

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# توکن بات تلگرام
TOKEN = '8262023316:AAFkgi6whXDh01Hk3NCWh-K5BT4Nd_yhIgY'

# ذخیره توکن‌های JWT برای هر کاربر
user_tokens = {}
user_states = {}
user_emails = {}  # برای ذخیره ایمیل کاربران

# زمان شروع ربات
start_time = time.time()

bot = telebot.TeleBot(TOKEN)

def make_keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('📝 رجیستر', '🔐 لاگین')
    markup.add('📊 پروفایل', '🚪 خروج')
    markup.add('❓ کمک')
    return markup

@bot.message_handler(commands=['start', 'cancel'])
def start(message):
    markup = make_keyboard()
    bot.send_message(
        message.chat.id, 
        '🤖 **به ربات MH-AI خوش آمدید!**\n\n'
        'لطفاً یکی از گزینه‌های زیر رو انتخاب کن:',
        reply_markup=markup,
        parse_mode='Markdown'
    )
    user_states[message.chat.id] = 'choose_action'

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🤖 **راهنما ربات MH-AI**

📋 **دستورات اصلی:**
/start - شروع ربات
/help - نمایش راهنما  
/profile - اطلاعات پروفایل
/logout - خروج از حساب
/cancel - لغو عملیات جاری

📝 **نحوه استفاده:**
1. اول با گزینه 📝 رجیستر ثبت نام کن
2. یا با گزینه 🔐 لاگین وارد شو
3. سپس هر سوالی داری بپرس

🔑 **فرمت لاگین:**
email:password

💡 **مثال:**
user@example.com:password123

📞 **پشتیبانی:**
اگر مشکل داشتید پیام بدید!
"""
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['profile'])
def profile_command(message):
    if message.chat.id in user_tokens:
        email = user_emails.get(message.chat.id, 'نامشخص')
        profile_text = f"""
📊 **پروفایل کاربری**

✅ **وضعیت:** لاگین شده
📧 **ایمیل:** {email}
🔑 **توکن:** فعال

💬 **امکانات:**
- می‌تونی سوالاتت رو بپرسی
- از هوش مصنوعی کمک بگیری
"""
        bot.send_message(message.chat.id, profile_text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "❌ **شما لاگین نیستید!**\nلطفاً اول لاگین کنید.", parse_mode='Markdown')

@bot.message_handler(commands=['logout'])
def logout_command(message):
    if message.chat.id in user_tokens:
        del user_tokens[message.chat.id]
    if message.chat.id in user_emails:
        del user_emails[message.chat.id]
    user_states[message.chat.id] = 'choose_action'
    
    bot.send_message(message.chat.id, "✅ **با موفقیت خارج شدید!**", parse_mode='Markdown')
    start(message)

@bot.message_handler(commands=['status'])
def status_command(message):
    uptime = time.time() - start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    
    users_count = len(user_tokens)
    
    status_text = f"""
📈 **وضعیت ربات**

⏰ **آپتایم:** {hours} ساعت, {minutes} دقیقه, {seconds} ثانیه
👥 **کاربران آنلاین:** {users_count} نفر
🟢 **وضعیت:** فعال

🤖 **ربات MH-AI**
"""
    bot.send_message(message.chat.id, status_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == '❓ کمک')
def help_button(message):
    help_command(message)

@bot.message_handler(func=lambda message: message.text == '📊 پروفایل')
def profile_button(message):
    profile_command(message)

@bot.message_handler(func=lambda message: message.text == '🚪 خروج')
def logout_button(message):
    logout_command(message)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'choose_action')
def choose_action(message):
    if message.text == '📝 رجیستر':
        bot.send_message(message.chat.id, '📝 **لطفاً ایمیل و پسوردت رو به فرمت زیر بفرست:**\n\nemail:password\n\n💡 مثال:\nuser@example.com:password123', parse_mode='Markdown')
        user_states[message.chat.id] = 'register'
    elif message.text == '🔐 لاگین':
        bot.send_message(message.chat.id, '🔐 **لطفاً ایمیل و پسوردت رو به فرمت زیر بفرست:**\n\nemail:password\n\n💡 مثال:\nuser@example.com:password123', parse_mode='Markdown')
        user_states[message.chat.id] = 'login'
    else:
        bot.send_message(message.chat.id, 'لطفاً فقط از گزینه‌های منو استفاده کن!')

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'register')
def register(message):
    try:
        email, password = message.text.split(':')
        email = email.strip()
        password = password.strip()
        
        response = requests.post(
            'https://mh-ai.liara.run/api/auth/register',
            json={"email": email, "password": password, "turnstileToken": "test"},
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            bot.send_message(message.chat.id, '✅ **ثبت نام موفق!**\n\nحالا می‌تونی با گزینه 🔐 لاگین وارد شی.', parse_mode='Markdown')
        else:
            error_msg = response.json().get("message", "مشکل ناشناخته")
            bot.send_message(message.chat.id, f'❌ **خطا در ثبت نام:**\n{error_msg}', parse_mode='Markdown')
            
    except ValueError:
        bot.send_message(message.chat.id, '❌ **فرمت اشتباه!**\nلطفاً به شکل زیر بفرست:\nemail:password', parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Register error: {e}")
        bot.send_message(message.chat.id, '❌ **خطای سیستمی!**\nلطفاً بعداً تلاش کن.', parse_mode='Markdown')
    
    finally:
        user_states[message.chat.id] = 'choose_action'
        start(message)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'login')
def login(message):
    try:
        email, password = message.text.split(':')
        email = email.strip()
        password = password.strip()
        
        response = requests.post(
            'https://mh-ai.liara.run/api/auth/login',
            json={"email": email, "password": password, "turnstileToken": "test"},
            timeout=30
        )
        
        if response.status_code == 200:
            token = response.json().get('token')
            if token:
                user_tokens[message.chat.id] = token
                user_emails[message.chat.id] = email
                bot.send_message(
                    message.chat.id, 
                    '✅ **لاگین موفق!**\n\nحالا می‌تونی هر سوالی داری از من بپرسی!',
                    parse_mode='Markdown'
                )
                user_states[message.chat.id] = 'ask_question'
            else:
                bot.send_message(message.chat.id, '❌ **توکن دریافت نشد!**', parse_mode='Markdown')
                user_states[message.chat.id] = 'choose_action'
                start(message)
        else:
            error_msg = response.json().get("message", "مشکل ناشناخته")
            bot.send_message(message.chat.id, f'❌ **خطا در لاگین:**\n{error_msg}', parse_mode='Markdown')
            user_states[message.chat.id] = 'choose_action'
            start(message)
            
    except ValueError:
        bot.send_message(message.chat.id, '❌ **فرمت اشتباه!**\nلطفاً به شکل زیر بفرست:\nemail:password', parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Login error: {e}")
        bot.send_message(message.chat.id, '❌ **خطای سیستمی!**\nلطفاً بعداً تلاش کن.', parse_mode='Markdown')
        user_states[message.chat.id] = 'choose_action'
        start(message)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'ask_question')
def ask_question(message):
    if message.text in ['/start', '/cancel', '/logout']:
        return
    
    if message.text == '🚪 خروج':
        logout_command(message)
        return
        
    if message.chat.id not in user_tokens:
        bot.send_message(message.chat.id, '❌ **لطفاً اول لاگین کن!**', parse_mode='Markdown')
        user_states[message.chat.id] = 'choose_action'
        start(message)
        return

    try:
        # نشان دادن تایپ کردن
        bot.send_chat_action(message.chat.id, 'typing')
        
        headers = {'Authorization': f'Bearer {user_tokens[message.chat.id]}'}
        response = requests.post(
            'https://mh-ai.liara.run/api/ask',
            json={"question": message.text},
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            answer = response.json().get('response', 'پاسخ دریافت نشد!')
            bot.send_message(message.chat.id, f'🤖 **پاسخ:**\n\n{answer}', parse_mode='Markdown')
        else:
            error_msg = response.json().get("message", "مشکل ناشناخته")
            bot.send_message(message.chat.id, f'❌ **خطا در دریافت پاسخ:**\n{error_msg}', parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Ask error: {e}")
        bot.send_message(message.chat.id, '❌ **خطا در پردازش سوال!**\nلطفاً دوباره تلاش کن.', parse_mode='Markdown')

# هندلر برای تمام پیام‌ها
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.chat.id not in user_states:
        user_states[message.chat.id] = 'choose_action'
    
    if user_states[message.chat.id] != 'ask_question':
        start(message)

if __name__ == '__main__':
    logger.info("🤖 ربات MH-AI در حال راه اندازی...")
    print("🤖 ربات در حال اجراست...")
    print("🟢 برای توقف: Ctrl+C")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"خطا در اجرای ربات: {e}")
        print(f"❌ خطا: {e}")