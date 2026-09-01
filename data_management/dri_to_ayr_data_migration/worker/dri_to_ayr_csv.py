"""Build AYR Metadata Store CSV files for one worker message.

This module is used by the worker Lambda. The coordinator decides the
ConsignmentReference and passes it through the worker message. If the worker
or coordinator does not supply a ConsignmentReference, CSV generation fails.
"""

from __future__ import annotations

import csv
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

LOGGER = logging.getLogger(__name__)


BODY_COLUMNS = ["BodyId", "Name", "Description"]

SERIES_COLUMNS = ["SeriesId", "BodyId", "Name", "Description"]

CONSIGNMENT_COLUMNS = [
    "ConsignmentId",
    "BodyId",
    "SeriesId",
    "ConsignmentReference",
    "ConsignmentType",
    "IncludeTopLevelFolder",
    "ContactName",
    "ContactEmail",
    "TransferStartDatetime",
    "TransferCompleteDatetime",
    "ExportDatetime",
    "CreatedDatetime",
]

FILE_COLUMNS = [
    "FileId",
    "ConsignmentId",
    "FileType",
    "FileName",
    "FilePath",
    "FileReference",
    "CiteableReference",
    "ParentReference",
    "OriginalFilePath",
    "Checksum",
    "CreatedDatetime",
]

FILE_METADATA_COLUMNS = [
    "MetadataId",
    "FileId",
    "PropertyName",
    "Value",
    "CreatedDatetime",
]

AV_METADATA_COLUMNS = [
    "FileId",
    "Filepath",
    "AV_Software",
]

# Source fields already represented by Body, Series, Consignment, File,
# or known FileMetadata mappings. These do not need duplicate dri_* entries.
MAPPED_RECORD_PATHS = {
    # Body / Consignment / File.
    "transferred_by",
    "tdr_consignment_id",
    "reference",
    # Existing FileMetadata mappings.
    "date_last_modified",
    "description",
    "public_description",
    "covering_date_end",
    "evidence_provider",
    "former_reference_department",
    "held_by",
    "language",
    "legal_status",
    "note",
    "copyright_holders",
    "sensitivity_foi_asserted_date",
    "sensitivity_foi_exemptions",
    "sensitivity_closure_period",
    "sensitivity_closure_start_date",
    "sensitivity_closure_review_date",
    "sensitivity_is_record_closed",
}

# These are preserved as source metadata because their final AYR mapping
# is not confirmed or they are useful DRI source identifiers.

# Digital-file fields represented directly by File/FileMetadata.
# Checksums are intentionally not listed because File.Checksum stores only
# one preferred checksum, so the full original checksum array is retained.
MAPPED_DIGITAL_FILE_PATHS = {
    "file_id",
    "file_name",
    "file_path",
    "size_bytes",
}


def utc_now_text() -> str:
    """Return UTC timestamp in DDT/Talend expected format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_state() -> dict[str, Any]:
    """Create the in-memory rows used while building one CSV package."""
    return {
        "created_datetime": utc_now_text(),
        "body_rows": [],
        "series_rows": [],
        "consignment_rows": [],
        "file_rows": [],
        "file_metadata_rows": [],
        "metadata_occurrences": {},
    }


def camel_to_snake(value: str) -> str:
    """Convert camelCase/PascalCase text to snake_case."""
    value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    return value.lower()


def stable_uuid(*parts: Any) -> str:
    """Create a deterministic UUID for repeatable CSV output."""
    key = "|".join("" if part is None else str(part) for part in parts)
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"ayr-dri-to-ayr-csv|{key}"))


def valid_uuid_or_none(value: Any) -> str | None:
    """Return a canonical UUID string if value is a valid UUID; otherwise None."""
    if not value:
        return None

    try:
        return str(uuid.UUID(str(value)))
    except (ValueError, AttributeError, TypeError):
        return None


def normalise_value(value: Any) -> str:
    """Convert a Python/JSON value to FileMetadata.Value text."""
    if isinstance(value, bool):
        return str(value).lower()

    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)

    return str(value)


def require_text(value: Any, field_name: str) -> str:
    """Return required text supplied by the worker/coordinator."""
    if not isinstance(value, str):
        raise ValueError(f"Missing required field: {field_name}")

    return value


def flatten_json(data: Any, prefix: str = "") -> Iterator[tuple[str, Any]]:
    """Yield flattened object leaves, retaining arrays as JSON values."""
    if isinstance(data, dict):
        for key, value in data.items():
            snake_key = camel_to_snake(key)
            new_prefix = f"{prefix}_{snake_key}" if prefix else snake_key
            yield from flatten_json(value, new_prefix)
        return

    if isinstance(data, list):
        yield prefix, data
        return

    if data is not None:
        yield prefix, data


def get_series_name(reference: str) -> str:
    """Return the segment before the first slash in a DRI reference."""
    return reference.split("/", 1)[0]


def derive_file_reference(reference: str) -> str:
    """
    Derive File.FileReference from the DRI reference.

    Example:
      LEV 2/2BD/Z -> 2BD/Z
    """
    if "/" not in reference:
        raise ValueError(
            f"Could not derive File.FileReference from reference: {reference!r}"
        )

    return reference.split("/", 1)[1]


def require_consignment_reference(consignment_reference: Any) -> str:
    """Return the required coordinator-supplied ConsignmentReference."""
    return require_text(consignment_reference, "consignment_reference")


def get_sha256_or_first_checksum(digital_file: dict[str, Any]) -> str | None:
    """Prefer SHA-256, then MD5, then the first checksum value available."""
    checksums = digital_file.get("checksums") or []

    if not isinstance(checksums, list):
        return None

    def find_by_hash(target_hash: str) -> str | None:
        for checksum in checksums:
            if not isinstance(checksum, dict):
                continue

            hash_name = str(checksum.get("hash", "")).upper().replace("-", "")

            if hash_name == target_hash and checksum.get("value"):
                return str(checksum["value"])

        return None

    return (
        find_by_hash("SHA256")
        or find_by_hash("MD5")
        or next(
            (
                str(checksum["value"])
                for checksum in checksums
                if isinstance(checksum, dict) and checksum.get("value")
            ),
            None,
        )
    )


def derive_file_path(digital_file: dict[str, Any]) -> str:
    """Use digitalFiles[].filePath when present, otherwise leave File.FilePath blank."""
    file_path = digital_file.get("filePath")
    return file_path if isinstance(file_path, str) else ""


def derive_closure_type(sensitivity: dict[str, Any]) -> str:
    """Derive AYR closure_type from DRI sensitivity.isRecordClosed."""
    if "isRecordClosed" not in sensitivity:
        raise ValueError(
            "Missing required field: sensitivity.isRecordClosed. "
            "This is required to derive closure_type."
        )

    return "Closed" if bool(sensitivity["isRecordClosed"]) else "Open"


def derive_closed_flag(original_value: Any, public_value: Any) -> bool | None:
    """Return whether a public/display value differs from its source value."""
    if original_value is None or public_value is None:
        return None

    return str(original_value) != str(public_value)


def join_foi_exemption_codes(sensitivity: dict[str, Any]) -> str | None:
    """Return FOI exemption codes as one semicolon-separated value."""
    exemptions = sensitivity.get("foiExemptions") or []

    if not isinstance(exemptions, list):
        return None

    codes = [
        str(exemption["reference"])
        for exemption in exemptions
        if isinstance(exemption, dict) and exemption.get("reference")
    ]

    if not codes:
        return None

    return ";".join(codes)


def build_known_metadata(
    record: dict[str, Any],
    digital_file: dict[str, Any],
) -> dict[str, Any]:
    """Return DRI values mapped to existing AYR FileMetadata keys."""
    sensitivity = record.get("sensitivity") or {}

    if not isinstance(sensitivity, dict):
        sensitivity = {}

    title = record.get("title")
    public_title = record.get("publicTitle")
    description = record.get("description")
    public_description = record.get("publicDescription")

    title_closed = derive_closed_flag(title, public_title)
    description_closed = derive_closed_flag(description, public_description)

    return {
        "date_last_modified": record.get("dateLastModified"),
        "description": public_description or description,
        "description_alternate": description
        if description_closed is True
        else None,
        "description_closed": description_closed,
        "title_alternate": title if title_closed is True else None,
        "title_closed": title_closed,
        "end_date": record.get("coveringDateEnd"),
        "evidence_provided_by": record.get("evidenceProvider"),
        "file_name": digital_file.get("fileName"),
        "file_size": digital_file.get("sizeBytes"),
        "foi_exemption_asserted": sensitivity.get("foiAssertedDate"),
        "foi_exemption_code": join_foi_exemption_codes(sensitivity),
        "former_reference_department": record.get("formerReferenceDepartment"),
        "held_by": record.get("heldBy"),
        "language": record.get("language"),
        "legal_status": record.get("legalStatus"),
        "note": record.get("note"),
        "rights_copyright": record.get("copyrightHolders"),
        "closure_period": sensitivity.get("closurePeriod"),
        "closure_start_date": sensitivity.get("closureStartDate"),
        "closure_type": derive_closure_type(sensitivity),
        "opening_date": sensitivity.get("closureReviewDate"),
    }


def create_body_row(state: dict[str, Any], body_name: str) -> None:
    """
    Add one Body CSV row.

    BodyId is intentionally blank because DDT resolves or creates Body at publication time.
    """
    state["body_rows"].append(
        {
            "BodyId": "",
            "Name": body_name,
            "Description": body_name,
        }
    )


def create_series_row(state: dict[str, Any], series_name: str) -> None:
    """
    Add one Series CSV row.

    SeriesId and BodyId are intentionally blank because DDT resolves or creates Series
    at publication time.
    """
    state["series_rows"].append(
        {
            "SeriesId": "",
            "BodyId": "",
            "Name": series_name,
            "Description": series_name,
        }
    )


def create_consignment_row(
    state: dict[str, Any],
    consignment_reference: str,
) -> str:
    """
    Add one Consignment CSV row and return ConsignmentId.

    ConsignmentId must be supplied by us.
    BodyId and SeriesId are intentionally blank because DDT resolves them later.
    """
    consignment_id = stable_uuid("Consignment", consignment_reference)

    state["consignment_rows"].append(
        {
            "ConsignmentId": consignment_id,
            "BodyId": "",
            "SeriesId": "",
            "ConsignmentReference": consignment_reference,
            "ConsignmentType": "Standard",
            "IncludeTopLevelFolder": "false",
            "ContactName": "",
            "ContactEmail": "",
            "TransferStartDatetime": "",
            "TransferCompleteDatetime": "",
            "ExportDatetime": "",
            "CreatedDatetime": state["created_datetime"],
        }
    )

    return consignment_id


def create_file_row(
    state: dict[str, Any],
    record: dict[str, Any],
    digital_file: dict[str, Any],
    consignment_id: str,
) -> str:
    """Create one File CSV row and return FileId."""
    reference = require_text(record.get("reference"), "reference")
    file_name = require_text(
        digital_file.get("fileName"), "digitalFiles[].fileName"
    )

    file_path = derive_file_path(digital_file)

    source_file_id = valid_uuid_or_none(digital_file.get("fileId"))

    file_id = source_file_id or stable_uuid(
        "File",
        record.get("recordId") or reference,
        file_path,
        file_name,
    )

    checksum = get_sha256_or_first_checksum(digital_file)

    state["file_rows"].append(
        {
            "FileId": file_id,
            "ConsignmentId": consignment_id,
            "FileType": "File",
            "FileName": file_name,
            "FilePath": file_path,
            "FileReference": derive_file_reference(reference),
            "CiteableReference": reference,
            "ParentReference": "",
            "OriginalFilePath": "",
            "Checksum": checksum or "",
            "CreatedDatetime": state["created_datetime"],
        }
    )

    return file_id


def insert_file_metadata(
    state: dict[str, Any],
    file_id: str,
    property_name: str,
    value: Any,
) -> None:
    """Add FileMetadata row(s). Simple arrays become multiple rows."""
    if value is None:
        return

    if isinstance(value, list):
        if not value:
            return

        if any(isinstance(item, (dict, list)) for item in value):
            insert_file_metadata(
                state,
                file_id,
                property_name,
                normalise_value(value),
            )
            return

        for item in value:
            insert_file_metadata(
                state,
                file_id,
                property_name,
                item,
            )
        return

    normalised = normalise_value(value)

    occurrence_key = (file_id, property_name, normalised)
    occurrence = state["metadata_occurrences"].get(occurrence_key, 0) + 1
    state["metadata_occurrences"][occurrence_key] = occurrence

    metadata_id = stable_uuid(
        "FileMetadata",
        file_id,
        property_name,
        normalised,
        occurrence,
    )

    state["file_metadata_rows"].append(
        {
            "MetadataId": metadata_id,
            "FileId": file_id,
            "PropertyName": property_name,
            "Value": normalised,
            "CreatedDatetime": state["created_datetime"],
        }
    )


def insert_unmapped_record_metadata(
    state: dict[str, Any],
    file_id: str,
    record: dict[str, Any],
) -> None:
    """Store record-level source values not represented by an AYR mapping."""
    record_without_digital_files = {
        key: value for key, value in record.items() if key != "digitalFiles"
    }

    for path, value in flatten_json(record_without_digital_files):
        if path in MAPPED_RECORD_PATHS:
            continue

        insert_file_metadata(
            state,
            file_id,
            f"dri_{path}",
            value,
        )


def insert_unmapped_digital_file_metadata(
    state: dict[str, Any],
    file_id: str,
    digital_file: dict[str, Any],
) -> None:
    """Store digital-file source fields not fully represented in AYR."""
    for path, value in flatten_json(digital_file):
        if path in MAPPED_DIGITAL_FILE_PATHS:
            continue

        insert_file_metadata(
            state,
            file_id,
            f"dri_digital_file_{path}",
            value,
        )


def migrate_record(
    state: dict[str, Any],
    record: dict[str, Any],
    digital_file: dict[str, Any],
    consignment_reference: str,
) -> None:
    """Convert one DRI record/file into CSV rows."""
    reference = require_text(record.get("reference"), "reference")
    transferred_by = require_text(record.get("transferredBy"), "transferredBy")
    series_name = get_series_name(reference)

    create_body_row(state, transferred_by)
    create_series_row(state, series_name)

    consignment_id = create_consignment_row(
        state,
        consignment_reference,
    )

    file_id = create_file_row(
        state,
        record,
        digital_file,
        consignment_id,
    )

    for property_name, value in build_known_metadata(
        record, digital_file
    ).items():
        insert_file_metadata(
            state,
            file_id,
            property_name,
            value,
        )

    insert_unmapped_record_metadata(
        state,
        file_id,
        record,
    )

    insert_unmapped_digital_file_metadata(
        state,
        file_id,
        digital_file,
    )


def write_csv(
    path: Path, columns: list[str], rows: list[dict[str, Any]]
) -> None:
    """Write rows to a CSV file with a fixed header."""
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=columns,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    LOGGER.info("Wrote %s row(s) to %s", len(rows), path)


def write_csvs(state: dict[str, Any], output_dir: Path) -> None:
    """Write all accumulated rows to CSV files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    write_csv(
        output_dir / "AYR-body-metadata.csv",
        BODY_COLUMNS,
        state["body_rows"],
    )

    write_csv(
        output_dir / "AYR-series-metadata.csv",
        SERIES_COLUMNS,
        state["series_rows"],
    )

    write_csv(
        output_dir / "AYR-consignment-metadata.csv",
        CONSIGNMENT_COLUMNS,
        state["consignment_rows"],
    )

    write_csv(
        output_dir / "AYR-file.csv",
        FILE_COLUMNS,
        state["file_rows"],
    )

    write_csv(
        output_dir / "AYR-file-metadata.csv",
        FILE_METADATA_COLUMNS,
        state["file_metadata_rows"],
    )

    write_csv(
        output_dir / "AYR-av-metadata.csv",
        AV_METADATA_COLUMNS,
        [],
    )


def convert_record_to_csv(
    record: dict[str, Any],
    digital_file: dict[str, Any],
    output_dir: str,
    consignment_reference: str,
) -> None:
    """Write AYR MDS CSV files for an already-loaded single DRI record/file."""
    state = new_state()
    final_consignment_reference = require_consignment_reference(
        consignment_reference
    )

    migrate_record(
        state=state,
        record=record,
        digital_file=digital_file,
        consignment_reference=final_consignment_reference,
    )

    write_csvs(state, Path(output_dir))

    LOGGER.info(
        "Completed CSV export for reference=%s, consignment_reference=%s.",
        record.get("reference"),
        final_consignment_reference,
    )
