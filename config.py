import os
DB_URL = os.getenv("MONGODB_URL", 'mongodb://localhost:27017/docstore')
MAX_FILE_SIZE = 8 * 1024 * 1024
MAX_FILENUM_ALLOWED = 256
PID_LENGTH = 32
HMAC_KEY = os.getenv("HMAC_KEY", "eca47a50d2a16ead448805b452ccaea7")
ACCESS_KEY = os.getenv("ACCESS_KEY", "b86925de7s05dc7a2b56533s1a009843")