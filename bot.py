import os
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from googleapiclient.discovery import build
from google.oauth2 import service_account

# === НАСТРОЙКИ ===
BOT_TOKEN = "7940210585:AAGS1-DLKzezCHHXD2DpQcjn0eYx_oMwrAs"  # Замените на токен из BotFather
SERVICE_ACCOUNT_FILE = "credentials.json"  # JSON-ключ Google API
FOLDER_ID = "1YjA4gSFCULp6azLBHEKhLlXTVblqtljD"  # ID папки Google Диска
WEBHOOK_URL = "http://127.0.0.1:8080/upload_link"  # Адрес Webhook-сервера (замените на ngrok/VPS)

# === НАСТРОЙКА ЛОГИРОВАНИЯ ===
logging.basicConfig(level=logging.INFO)

# === ИНИЦИАЛИЗАЦИЯ БОТА ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# === НАСТРОЙКА GOOGLE DRIVE API ===
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

# === ФУНКЦИЯ ЗАГРУЗКИ ФАЙЛА В GOOGLE ДИСК ===
def upload_to_drive(file_path, file_name):
    try:
        file_metadata = {"name": file_name, "parents": [FOLDER_ID]}
        media = drive_service.files().create(
            body=file_metadata,
            media_body=file_path,
            fields="id"
        ).execute()

        file_id = media.get("id")
        file_link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"

        logging.info(f"✅ Файл загружен: {file_link}")

        # 🔹 Отправляем ссылку в Webhook
        payload = {"file_link": file_link}
        response = requests.post(WEBHOOK_URL, json=payload)

        if response.status_code == 200:
            logging.info("✅ Ссылка успешно отправлена в Webhook")
        else:
            logging.error(f"❌ Ошибка при отправке Webhook: {response.text}")

        return file_link
    except Exception as e:
        logging.error(f"❌ Ошибка загрузки файла: {e}")
        return None

# === ОБРАБОТКА КОМАНДЫ /загрузить_документ ===
@dp.message_handler(commands=["загрузить_документ"])
async def request_file(message: types.Message):
    await message.reply("📂 Отправьте файл, который хотите загрузить в Google Диск.")

# === ОБРАБОТКА ФАЙЛОВ ===
@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    document = message.document
    file_name = document.file_name
    file_path = f"temp/{file_name}"

    os.makedirs("temp", exist_ok=True)

    # Скачиваем файл
    file = await bot.get_file(document.file_id)
    await bot.download_file(file.file_path, file_path)

    # Загружаем в Google Диск
    file_link = upload_to_drive(file_path, file_name)

    if file_link:
        await message.reply(f"✅ Файл загружен в Google Диск: [Ссылка]({file_link})", parse_mode="Markdown")
    else:
        await message.reply("❌ Ошибка загрузки файла.")

    os.remove(file_path)  # Удаляем временный файл

# === ЗАПУСК БОТА ===
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)