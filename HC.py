import telebot
import requests
import json
import os

# 1. Insert your Telegram Bot Token here (From @BotFather)
BOT_TOKEN = "7885551891:AAFpZlQrjW11n8MYRuLduTuMx9p_41-tRlQ"
bot = telebot.TeleBot(BOT_TOKEN)

# 2. Server configurations extracted from HttpCanary
API_URL = "https://xd-ps-api-txt.vercel.app/xdimpor_deceypt"
HEADERS = {
    "accept": "application/json",
    "user-agent": "Dalvik/2.1.0 (Linux; Android 10)",
    "content-type": "application/json; charset=utf-8",
    "accept-encoding": "gzip"
}

# Links for branding and support
CHANNEL_URL = "https://t.me/+rZqVYMSTLPkxNmY0"
DEVELOPER_USERNAME = "@isFortan"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🎯 **Welcome to .hc File Decrypter Bot!**\n\n"
        "📁 Just send me any `.hc` configuration file, and I will instantly extract the decrypted data for you.\n\n"
        f"📢 **Join our Channel:** [Click Here]({CHANNEL_URL})\n"
        f"👨‍💻 **Developer:** {DEVELOPER_USERNAME}"
    )
    
    # Adding interactive buttons under the welcome message
    markup = telebot.types.InlineKeyboardMarkup()
    btn_channel = telebot.types.InlineKeyboardButton(text="📢 Join Channel", url=CHANNEL_URL)
    btn_dev = telebot.types.InlineKeyboardButton(text="👨‍💻 Contact Dev", url=f"https://t.me/{DEVELOPER_USERNAME.replace('@', '')}")
    markup.add(btn_channel, btn_dev)
    
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)

# Document handler to receive and process files
@bot.message_handler(content_types=['document'])
def handle_hc_file(message):
    file_name = message.document.file_name
    
    # Check if the file has the correct extension (.hc)
    if not file_name.lower().endswith('.hc'):
        bot.reply_to(message, "⚠️ **Error:** Please send a valid file ending with `.hc` extension.")
        return

    try:
        # Notify the user that processing has started
        status_msg = bot.reply_to(message, "⏳ *Downloading the file and reading encrypted payload...*", parse_mode='Markdown')

        # 1. Download file from Telegram servers
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # 2. Decode file content into string text
        try:
            hc_content = downloaded_file.decode('utf-8').strip()
        except UnicodeDecodeError:
            bot.edit_message_text("❌ **Error:** Failed to read file content as plain text. Ensure the file is not corrupted.", message.chat.id, status_msg.message_id)
            return

        bot.edit_message_text("🔄 *Sending payload data to the decryption server...*", message.chat.id, status_msg.message_id, parse_mode='Markdown')

        # 3. Construct the payload matching request_body.json exactly
        payload = {
            "file_type": ".hc",
            "source": "text",
            "content": hc_content  # Dynamic file content sent by the user
        }

        # 4. Sending the POST request to Vercel API
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)
        
        if response.status_code == 200:
            response_data = response.json()
            
            # 5. Extract decrypted data from response
            if "decrypted" in response_data:
                decrypted_result = response_data["decrypted"]
                
                # Format the success output text
                success_message = (
                    "🎯 **File Decrypted Successfully!**\n\n"
                    f"```json\n{decrypted_result}\n```\n"
                    f"📢 **Channel:** [Join Here]({CHANNEL_URL})\n"
                    f"👨‍💻 **Developer:** {DEVELOPER_USERNAME}"
                )
                
                # Create buttons for the decrypted message results
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(
                    telebot.types.InlineKeyboardButton(text="📢 Channel", url=CHANNEL_URL),
                    telebot.types.InlineKeyboardButton(text="👨‍💻 Developer", url=f"https://t.me/{DEVELOPER_USERNAME.replace('@', '')}")
                )
                
                # Handling Telegram's 4096 character limit per message
                if len(success_message) > 4000:
                    output_filename = f"decrypted_{file_name}.txt"
                    with open(output_filename, "w", encoding="utf-8") as f:
                        f.write(decrypted_result)
                    
                    with open(output_filename, "rb") as f:
                        bot.send_document(
                            message.chat.id, 
                            f, 
                            caption=f"🎯 **Result is too long! Decrypted data saved into a text file.**\n\n📢 {CHANNEL_URL}\n👨‍💻 Dev: {DEVELOPER_USERNAME}",
                            reply_markup=markup
                        )
                    
                    bot.delete_message(message.chat.id, status_msg.message_id)
                    os.remove(output_filename)  # Delete the temporary file
                else:
                    bot.edit_message_text(success_message, message.chat.id, status_msg.message_id, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)
            else:
                bot.edit_message_text("⚠️ **Server Error:** Server responded but the `decrypted` data field was missing.", message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text(f"❌ **Connection Failed:** Server returned status code: {response.status_code}", message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ **An unexpected error occurred:** {str(e)}")

# Keep the bot running continuously
print("[*] The Telegram Bot is now running perfectly... Send a .hc file to test!")
bot.infinity_polling()
