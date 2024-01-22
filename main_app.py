import os
import traceback

from app import create_app
from configs.aws_secrets_manager_config import AWSSecretsManagerConfig
from configs.env_config import EnvConfig

if os.getenv("CONFIG_SOURCE") == "AWS_SECRETS_MANAGER":
    config_class = AWSSecretsManagerConfig
elif os.getenv("CONFIG_SOURCE") == "ENVIRONMENT_VARIABLES":
    config_class = EnvConfig

try:
    app = create_app(config_class)
except Exception as e:
    print(e)
    print(traceback.format_exc())
