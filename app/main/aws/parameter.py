import boto3


def get_aws_environment_prefix() -> str:
    environment_name = get_parameter_store_key_value("ENVIRONMENT_NAME")
    return "/" + environment_name + "/"


def get_parameter_store_key_value(key: str) -> str:
    """
    Get string value of `key` in Parameter Store.
    :param key: Name of key whose value will be returned.
    :return: String value of requested Parameter Store key.
    """
    ssm_client = boto3.client("ssm")
    parameter_value = ssm_client.get_parameter(Name=key)["Parameter"]["Value"]
    return parameter_value
