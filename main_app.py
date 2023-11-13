import os

from app import create_app
from configs.aws_parameter_store_config import AWSParameterStoreConfig
from configs.env_config import EnvConfig

if os.getenv("CONFIG_SOURCE") == "AWS_PARAMETER_STORE":
    config_class = AWSParameterStoreConfig
elif os.getenv("CONFIG_SOURCE") == "ENVIRONMENT_VARIABLES":
    config_class = EnvConfig

app = create_app(config_class)
