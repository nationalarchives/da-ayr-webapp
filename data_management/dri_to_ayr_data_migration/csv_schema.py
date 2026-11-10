"""Shared CSV column contracts for DRI-to-AYR metadata packages."""

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
    "DateLastModified",
    "EndDate",
    "ClosureType",
    "OpeningDate",
    "ReconsiderDueInDate",
    "FormerFilePathDepartment",
    "CreatedDatetime",
]

FILE_METADATA_COLUMNS = [
    "MetadataId",
    "FileId",
    "PropertyName",
    "Value",
    "CreatedDatetime",
]

AV_METADATA_COLUMNS = ["FileId", "Filepath", "AV_Software"]
