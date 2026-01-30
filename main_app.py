import os
import traceback

from app import create_app
from configs.env_config import EnvConfig

if os.getenv("CONFIG_SOURCE") == "AWS_SECRETS_MANAGER":
    from configs.aws_secrets_manager_config import AWSSecretsManagerConfig

    config_class = AWSSecretsManagerConfig
    local_env = False
elif os.getenv("CONFIG_SOURCE") == "ENVIRONMENT_VARIABLES":
    config_class = EnvConfig
    local_env = True
else:
    config_class = EnvConfig
    local_env = True
try:
    app = create_app(config_class, local_env)
except Exception as e:
    print(e)
    print(traceback.format_exc())
