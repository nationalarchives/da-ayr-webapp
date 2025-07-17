from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()


class Body(db.Model):
    __tablename__ = "Body"
    BodyId = db.Column(UUID(as_uuid=True), primary_key=True)
    Name = db.Column(Text)
    Description = db.Column(Text)


class Series(db.Model):
    __tablename__ = "Series"
    SeriesId = db.Column(UUID(as_uuid=True), primary_key=True)
    BodyId = db.Column(UUID(as_uuid=True), ForeignKey("Body.BodyId"))
    Name = db.Column(Text)
    Description = db.Column(Text)
    body = db.relationship("Body", foreign_keys="Series.BodyId")


class Consignment(db.Model):
    __tablename__ = "Consignment"
    ConsignmentId = db.Column(UUID(as_uuid=True), primary_key=True)
    SeriesId = db.Column(UUID(as_uuid=True), ForeignKey("Series.SeriesId"))
    BodyId = db.Column(UUID(as_uuid=True), ForeignKey("Body.BodyId"))
    ConsignmentReference = db.Column(Text)
    ConsignmentType = db.Column(String, nullable=False)
    IncludeTopLevelFolder = db.Column(Boolean)
    ContactName = db.Column(Text)
    ContactEmail = db.Column(Text)
    TransferStartDatetime = db.Column(DateTime)
    TransferCompleteDatetime = db.Column(DateTime)
    ExportDatetime = db.Column(DateTime)
    CreatedDatetime = db.Column(DateTime)
    series = db.relationship("Series", foreign_keys="Consignment.SeriesId")


class File(db.Model):
    __tablename__ = "File"
    FileId = db.Column(UUID(as_uuid=True), primary_key=True)
    ConsignmentId = db.Column(
        UUID(as_uuid=True), ForeignKey("Consignment.ConsignmentId")
    )
    FileReference = db.Column(Text, nullable=False)
    FileType = db.Column(Text, nullable=False)
    FileName = db.Column(Text, nullable=False)
    FilePath = db.Column(Text, nullable=False)
    CiteableReference = db.Column(Text)
    Checksum = db.Column(Text)
    CreatedDatetime = db.Column(DateTime)
    consignment = db.relationship(
        "Consignment", foreign_keys="File.ConsignmentId"
    )
    ffid_metadata = db.relationship(
        "FFIDMetadata",
        back_populates="file",
        uselist=False,
        foreign_keys="FFIDMetadata.FileId",
    )


class FileMetadata(db.Model):
    __tablename__ = "FileMetadata"
    MetadataId = db.Column(UUID(as_uuid=True), primary_key=True)
    FileId = db.Column(UUID(as_uuid=True), ForeignKey("File.FileId"))
    PropertyName = db.Column(Text, nullable=False)
    Value = db.Column(Text)
    CreatedDatetime = db.Column(DateTime)
    file = db.relationship("File", foreign_keys="FileMetadata.FileId")


class FFIDMetadata(db.Model):
    __tablename__ = "FFIDMetadata"

    FileId = db.Column(
        UUID(as_uuid=True), db.ForeignKey("File.FileId"), primary_key=True
    )
    Extension = db.Column(Text)
    PUID = db.Column(Text)
    FormatName = db.Column(Text)
    ExtensionMismatch = db.Column(Boolean)
    FFID_Software = db.Column("FFID-Software", Text)
    FFID_SoftwareVersion = db.Column("FFID-SoftwareVersion", Text)
    FFID_BinarySignatureFileVersion = db.Column(
        "FFID-BinarySignatureFileVersion", Text
    )
    FFID_ContainerSignatureFileVersion = db.Column(
        "FFID-ContainerSignatureFileVersion", Text
    )
    file = db.relationship(
        "File",
        back_populates="ffid_metadata",
        foreign_keys=[FileId],
        uselist=False,
    )
