"""Database utility functions for building connection URLs."""

import os
from typing import Optional
from urllib.parse import quote_plus


def build_database_url(
    host: Optional[str] = None,
    port: Optional[str] = None,
    name: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    ssl_mode: Optional[str] = None,
    ssl_cert: Optional[str] = None,
) -> str:
    """
    Build PostgreSQL database URL.

    If parameters are not provided, they will be read from environment variables:
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_SSL_ROOT_CERTIFICATE

    Args:
        host: Database host
        port: Database port
        name: Database name
        user: Database user
        password: Database password
        ssl_mode: SSL mode (e.g., 'verify-full', 'disable'). If None, will check
                  if cert file exists and use verify-full if it does.
        ssl_cert: Path to SSL certificate file

    Returns:
        str: PostgreSQL connection URL

    Raises:
        ValueError: If required parameters are missing
    """
    db_host = host or os.getenv("DB_HOST")
    if not db_host:
        raise ValueError("Missing required database parameters: db_host")

    db_port = port or os.getenv("DB_PORT")
    if not db_port:
        raise ValueError("Missing required database parameters: db_port")

    db_name = name or os.getenv("DB_NAME")
    if not db_name:
        raise ValueError("Missing required database parameters: db_name")

    db_user = user or os.getenv("DB_USER")
    if not db_user:
        raise ValueError("Missing required database parameters: db_user")
    db_password = password or os.getenv("DB_PASSWORD")
    if not db_password:
        raise ValueError("Missing required database parameters: db_password")

    db_ssl_cert = ssl_cert or os.getenv("DB_SSL_ROOT_CERTIFICATE")

    encoded_password = quote_plus(db_password)
    base_url = (
        f"postgresql+psycopg2://{db_user}:{encoded_password}"
        f"@{db_host}:{db_port}/{db_name}"
    )

    # Handle SSL configuration
    if ssl_mode == "disable":
        return f"{base_url}?sslmode=disable"
    elif ssl_mode:
        # Explicit SSL mode provided
        if db_ssl_cert:
            return f"{base_url}?sslmode={ssl_mode}&sslrootcert={db_ssl_cert}"
        else:
            return f"{base_url}?sslmode={ssl_mode}"
    elif db_ssl_cert and os.path.exists(db_ssl_cert):
        # No explicit SSL mode, but cert file exists - use verify-full
        return f"{base_url}?sslmode=verify-full&sslrootcert={db_ssl_cert}"
    else:
        # No SSL configuration
        return base_url
