import os
from datetime import datetime

import psycopg2


def get_db_connection():
    """Get a secure connection to the webapp database using environment variables."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="verify-full",
        sslrootcert=os.getenv("DB_SSL_ROOTCERT"),
    )


def insert_metadata(conn, document_id, metadata):
    with conn.cursor() as cur:
        # Insert basic metadata
        cur.execute(
            """
            INSERT INTO document_metadata (document_id, key, value, created_at)
            VALUES (%s, %s, %s, %s)
        """,
            (
                document_id,
                metadata["key"],
                metadata["value"],
                datetime.utcnow(),
            ),
        )

        # Insert additional metadata fields
        for key, value in metadata.items():
            if key not in ["key", "value"]:
                cur.execute(
                    """
                    INSERT INTO document_metadata (document_id, key, value, created_at)
                    VALUES (%s, %s, %s, %s)
                """,
                    (
                        document_id,
                        key,
                        str(value),
                        datetime.now(datetime.timezone.utc),
                    ),
                )

        conn.commit()
