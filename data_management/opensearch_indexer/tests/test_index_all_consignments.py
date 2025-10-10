"""
Tests for the index_all_consignments script.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from data_management.opensearch_indexer.opensearch_indexer.index_all_consignments import (
    build_database_url,
    get_all_consignment_references,
    main,
)


class TestBuildDatabaseUrl:
    """Tests for build_database_url function."""

    def test_build_database_url_success(self, monkeypatch):
        """Test building database URL with required environment variables."""
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_PORT", "5432")
        monkeypatch.setenv("DB_NAME", "testdb")
        monkeypatch.setenv("DB_USER", "testuser")
        monkeypatch.setenv(
            "DB_PASSWORD", "testpass"
        )  # pragma: allowlist secret

        result = build_database_url()

        assert (
            result
            == "postgresql+psycopg2://testuser:testpass@localhost:5432/testdb"  # pragma: allowlist secret
        )

    def test_build_database_url_with_ssl_cert(self, monkeypatch, tmp_path):
        """Test building database URL with SSL certificate."""
        cert_file = tmp_path / "cert.pem"
        cert_file.touch()

        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_PORT", "5432")
        monkeypatch.setenv("DB_NAME", "testdb")
        monkeypatch.setenv("DB_USER", "testuser")
        monkeypatch.setenv(
            "DB_PASSWORD", "testpass"
        )  # pragma: allowlist secret
        monkeypatch.setenv("DB_SSL_ROOT_CERTIFICATE", str(cert_file))

        result = build_database_url()

        assert (
            "postgresql+psycopg2://testuser:testpass@localhost:5432/testdb"  # pragma: allowlist secret
            in result
        )
        assert f"sslmode=verify-full&sslrootcert={cert_file}" in result

    def test_build_database_url_missing_required_vars(self, monkeypatch):
        """Test that missing required variables raises ValueError."""
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_PORT", "5432")

        with pytest.raises(
            ValueError, match="Missing required database environment variables"
        ):
            build_database_url()


class TestGetAllConsignmentReferences:
    """Tests for get_all_consignment_references function."""

    @patch(
        "data_management.opensearch_indexer.opensearch_indexer.index_all_consignments.create_engine"
    )
    @patch(
        "data_management.opensearch_indexer.opensearch_indexer.index_all_consignments.sessionmaker"
    )
    def test_get_all_consignment_references_success(
        self, mock_sessionmaker, mock_create_engine
    ):
        """Test successfully retrieving consignment references."""
        mock_session = MagicMock()
        mock_sessionmaker.return_value = Mock(return_value=mock_session)

        mock_result = [("CONS-001",), ("CONS-002",), ("CONS-003",)]
        mock_session.execute.return_value.fetchall.return_value = mock_result

        result = get_all_consignment_references("postgresql://test")

        assert result == ["CONS-001", "CONS-002", "CONS-003"]
        mock_session.close.assert_called_once()

    @patch(
        "data_management.opensearch_indexer.opensearch_indexer.index_all_consignments.create_engine"
    )
    @patch(
        "data_management.opensearch_indexer.opensearch_indexer.index_all_consignments.sessionmaker"
    )
    def test_get_all_consignment_references_closes_session_on_error(
        self, mock_sessionmaker, mock_create_engine
    ):
        """Test that session is closed even when an error occurs."""
        mock_session = MagicMock()
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        mock_session.execute.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(SQLAlchemyError):
            get_all_consignment_references("postgresql://test")

        mock_session.close.assert_called_once()


class TestMain:

    @pytest.fixture
    def mock_env_vars(self, monkeypatch):
        """Set up all required environment variables."""
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_PORT", "5432")
        monkeypatch.setenv("DB_NAME", "testdb")
        monkeypatch.setenv("DB_USER", "testuser")
        monkeypatch.setenv(
            "DB_PASSWORD", "testpass"
        )  # pragma: allowlist secret
        monkeypatch.setenv("RECORD_BUCKET_NAME", "test-bucket")
        monkeypatch.setenv("OPEN_SEARCH_HOST", "https://opensearch:9200")
        monkeypatch.setenv("OPEN_SEARCH_USERNAME", "admin")
        monkeypatch.setenv(
            "OPEN_SEARCH_PASSWORD", "admin"
        )  # pragma: allowlist secret

    @patch(
        "data_management.opensearch_indexer.opensearch_indexer.index_all_consignments.bulk_index_consignment"
    )
    @patch(
        "data_management.opensearch_indexer.opensearch_indexer.index_all_consignments.get_all_consignment_references"
    )
    def test_main_success(self, mock_get_refs, mock_bulk_index, mock_env_vars):
        """Test successful indexing of multiple consignments."""
        mock_get_refs.return_value = ["CONS-001", "CONS-002", "CONS-003"]

        main()

        assert mock_bulk_index.call_count == 3

    @patch(
        "data_management.opensearch_indexer.opensearch_indexer.index_all_consignments.bulk_index_consignment"
    )
    @patch(
        "data_management.opensearch_indexer.opensearch_indexer.index_all_consignments.get_all_consignment_references"
    )
    def test_main_no_consignments_found(
        self, mock_get_refs, mock_bulk_index, mock_env_vars
    ):
        """Test behavior when no consignments are found in database."""
        mock_get_refs.return_value = []

        main()

        mock_bulk_index.assert_not_called()

    @patch(
        "data_management.opensearch_indexer.opensearch_indexer.index_all_consignments.bulk_index_consignment"
    )
    @patch(
        "data_management.opensearch_indexer.opensearch_indexer.index_all_consignments.get_all_consignment_references"
    )
    def test_main_partial_failure_exits_with_error(
        self, mock_get_refs, mock_bulk_index, mock_env_vars
    ):
        """Test that partial failures result in exit code 1."""
        mock_get_refs.return_value = ["CONS-001", "CONS-002", "CONS-003"]

        def side_effect(consignment_ref, *args, **kwargs):
            if consignment_ref == "CONS-002":
                raise Exception("Indexing failed")

        mock_bulk_index.side_effect = side_effect

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        assert mock_bulk_index.call_count == 3  # All consignments attempted

    @patch(
        "data_management.opensearch_indexer.opensearch_indexer.index_all_consignments.get_all_consignment_references"
    )
    def test_main_missing_required_env_vars(self, mock_get_refs, monkeypatch):
        """Test that missing environment variables raises ValueError."""
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_PORT", "5432")
        monkeypatch.setenv("DB_NAME", "testdb")
        monkeypatch.setenv("DB_USER", "testuser")
        monkeypatch.setenv(
            "DB_PASSWORD", "testpass"
        )  # pragma: allowlist secret

        with pytest.raises(
            ValueError,
            match="Missing required OpenSearch environment variables",
        ):
            main()
