import telebot
import requests
import json
import os

# 1. Insert your Telegram Bot Token here (From @BotFather)
BOT_TOKEN = "8061475536:AAFRbELE2GTbr2P9UgWZtDMCRPLebWWf6a8"
bot = telebot.TeleBot(BOT_TOKEN)

# 2. Stable Server configuration
API_URL = "https://xd-ps-api-txt.vercel.app/xdimpor_deceypt"
HEADERS = {
    "accept": "application/json",
    "user-agent": "Dalvik/2.1.0 (Linux; Android 10)",
    "content-type": "application/json; charset=utf-8",
    "accept-encoding": "gzip"
}

# Branding and support links
CHANNEL_URL = "https://t.me/+rZqVYMSTLPkxNmY0"
DEVELOPER_USERNAME = "@isFortan"

# List of ALL supported file extensions from the images
SUPPORTED_EXTENSIONS = ['.hc', '.hat', '.ziv', '.arm', '.slipnet', '.mludp', '.zoba', '.wyr', '.nm', '.apnalite', '.int', '.tik', '.v2', '.msy']

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    extensions_str = ", ".join([f"`{ext}`" for ext in SUPPORTED_EXTENSIONS])
    welcome_text = (
        "🎯 **Welcome to Ultimate Multi-Tunnel File Decrypter Bot!**\n\n"
        f"📁 Send me any configuration file with these extensions:\n{extensions_str}\n\n"
        "I will instantly extract the decrypted data for you.\n\n"
        f"📢 **Join our Channel:** [Click Here]({CHANNEL_URL})\n"
        f"👨‍💻 **Developer:** {DEVELOPER_USERNAME}"
    )
    
    markup = telebot.types.InlineKeyboardMarkup()
    btn_channel = telebot.types.InlineKeyboardButton(text="📢 Join Channel", url=CHANNEL_URL)
    btn_dev = telebot.types.InlineKeyboardButton(text="👨‍💻 Contact Dev", url=f"https://t.me/{DEVELOPER_USERNAME.replace('@', '')}")
    markup.add(btn_channel, btn_dev)
    
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)

# Document handler to process all incoming files from the images
@bot.message_handler(content_types=['document'])
def handle_tunnel_file(message):
    file_name = message.document.file_name
    
    # Extract the extension of the uploaded file
    _, file_extension = os.path.splitext(file_name.lower())
    
    # Check if the extension is in our comprehensive list
    if file_extension not in SUPPORTED_EXTENSIONS:
        bot.reply_to(message, f"⚠️ **Error:** Unsupported file format. Please send files with: {', '.join(SUPPORTED_EXTENSIONS)}")
        return

    try:
        status_msg = bot.reply_to(message, f"⏳ *Downloading {file_extension} file and extracting payload...*", parse_mode='Markdown')

        # 1. Download file from Telegram
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # 2. Decode the file content text
        try:
            encrypted_content = downloaded_file.decode('utf-8').strip()
        except UnicodeDecodeError:
            bot.edit_message_text("❌ **Error:** Failed to read file as text. Ensure it is not corrupted.", message.chat.id, status_msg.message_id)
            return

        bot.edit_message_text(f"🔄 *Sending {file_extension} payload to Stable Decryption Server...*", message.chat.id, status_msg.message_id, parse_mode='Markdown')

        # 3. Constructing the Dynamic Payload matching the stable server
        payload = {
            "file_type": file_extension, # Dynamically injects (.hc, .hat, .wyr, etc.)
            "source": "text",
            "content": encrypted_content
        }

        # 4. Requesting the stable API URL
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)
        
        if response.status_code == 200:
            response_data = response.json()
            
            # 5. Extraction logic
            if "decrypted" in response_data:
                decrypted_result = response_data["decrypted"]
                
                success_message = (
                    f"🎯 **{file_extension.upper()[1:]} File Decrypted Successfully!**\n\n"
                    f"```json\n{decrypted_result}\n```\n"
                    f"📢 **Channel:** [Join Here]({CHANNEL_URL})\n"
                    f"👨‍💻 **Developer:** {DEVELOPER_USERNAME}"
                )
                
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(
                    telebot.types.InlineKeyboardButton(text="📢 Channel", url=CHANNEL_URL),
                    telebot.types.InlineKeyboardButton(text="👨‍💻 Developer", url=f"https://t.me/{DEVELOPER_USERNAME.replace('@', '')}")
                )
                
                # Check for Telegram length limit (4096 chars)
                if len(success_message) > 4000:
                    output_filename = f"decrypted_{file_name}.txt"
                    with open(output_filename, "w", encoding="utf-8") as f:
                        f.write(decrypted_result)
                    
                    with open(output_filename, "rb") as f:
                        bot.send_document(
                            message.chat.id, 
                            f, 
                            caption=f"🎯 **Result is too long! Decrypted data saved as text file.**\n\n📢 {CHANNEL_URL}\n👨‍💻 Dev: {DEVELOPER_USERNAME}",
                            reply_markup=markup
                        )
                    
                    bot.delete_message(message.chat.id, status_msg.message_id)
                    os.remove(output_filename)
                else:
                    bot.edit_message_text(success_message, message.chat.id, status_msg.message_id, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)
            else:
                bot.edit_message_text("⚠️ **Server Error:** The `decrypted` block was missing from the response.", message.chat.id, status_msg.message_id)
        else:
            bot.edit_message_text(f"❌ **Connection Failed:** Server responded with code: {response.status_code}", message.chat.id, status_msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ **An unexpected error occurred:** {str(e)}")

# Infinite polling loop
print("[*] Ultimate Multi-Extension Bot is live and secure! Ready for all formats...")
bot.infinity_polling()
