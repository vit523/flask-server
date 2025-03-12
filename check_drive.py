from googleapiclient.discovery import build
from google.oauth2 import service_account

# Подключаем Google API
SERVICE_ACCOUNT_FILE = "credentials.json"
FOLDER_ID = "1YjA4gSFCULp6azLBHEKhLlXTVblqtljD"  # Замени на ID папки Google Диска

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

# Функция для получения списка файлов в папке
def list_files():
    results = drive_service.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed=false",
        fields="files(id, name)"
    ).execute()
    files = results.get("files", [])
    if not files:
        print("❌ Файлы не найдены.")
    else:
        print("✅ Найденные файлы:")
        for file in files:
            print(f"{file['name']} (ID: {file['id']})")

# Запускаем проверку
list_files() 
