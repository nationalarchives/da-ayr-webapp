from app import create_app
from configs.local_config import LocalConfig

app = create_app(LocalConfig)
