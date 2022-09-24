from dotenv import load_dotenv
import os

load_dotenv()

CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
API_ID = int(os.getenv('API_ID', "0"))
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')

PRINT_INTERVAL = 1
MB = 1048576


VIDEO_DIRECTORY = "videos"
SEARCH_TEXT = "#HPC_AH"