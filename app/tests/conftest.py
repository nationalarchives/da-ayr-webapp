from unittest.mock import patch

import pytest
from flask.testing import FlaskClient
from testing.postgresql import PostgresqlFactory

from app import create_app
from app.main.authorize.ayr_user import AYRUser
from app.main.db.models import Body, db
from app.tests.factories import (
    BodyFactory,
    ConsignmentFactory,
    FileFactory,
    FileMetadataFactory,
    SeriesFactory,
)
from configs.testing_config import TestingConfig


@pytest.fixture(scope="function")
def mock_standard_user():
    ayr_user_patcher = patch("app.main.authorize.permissions_helpers.AYRUser")
    patcher = patch(
        "app.main.authorize.access_token_sign_in_required.get_keycloak_instance_from_flask_config"
    )

    def _mock_standard_user(client: FlaskClient, body: str = "test_body"):
        groups = ["/ayr_user_type/view_dept", f"/transferring_body_user/{body}"]
        with client.session_transaction() as session:
            session["access_token"] = "valid_access_token"
            session["refresh_token"] = "valid_refresh_token"
            session["user_groups"] = groups
            session["user_type"] = "standard_user"
            session["user_id"] = "test_standard_user"

        mock_ayr_user = ayr_user_patcher.start()
        mock_keycloak = patcher.start()

        mock_ayr_user.return_value = AYRUser(groups)
        mock_keycloak.return_value.introspect.return_value = {
            "active": True,
            "groups": groups,
        }

        if Body.query.filter(Body.Name == body).count() == 0:
            BodyFactory(Name=body)

    yield _mock_standard_user

    ayr_user_patcher.stop()
    patcher.stop()


@pytest.fixture(scope="function")
def mock_all_access_user():
    ayr_user_patcher = patch("app.main.authorize.permissions_helpers.AYRUser")
    patcher = patch(
        "app.main.authorize.access_token_sign_in_required.get_keycloak_instance_from_flask_config"
    )

    def _mock_all_access_user(client: FlaskClient):
        groups = ["/ayr_user_type/view_all"]

        with client.session_transaction() as session:
            session["access_token"] = "valid_access_token"
            session["refresh_token"] = "valid_refresh_token"
            session["user_groups"] = groups
            session["user_type"] = "all_access_user"
            session["user_id"] = "test_aau_user"

        mock_ayr_user = ayr_user_patcher.start()
        mock_keycloak = patcher.start()

        mock_ayr_user.return_value = AYRUser(groups)
        mock_keycloak.return_value.introspect.return_value = {
            "active": True,
            "groups": groups,
        }

    yield _mock_all_access_user

    ayr_user_patcher.stop()
    patcher.stop()


@pytest.fixture
def app(database):
    app = create_app(TestingConfig, database.url())
    yield app


@pytest.fixture(scope="function")
def client(app):
    db.session.remove()
    db.drop_all()
    db.create_all()
    yield app.test_client()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "ignore_https_errors": True}


@pytest.fixture(scope="session")
def database(request):
    # Launch new PostgreSQL server
    postgresql = PostgresqlFactory(cache_initialized_db=True)()
    yield postgresql

    # PostgreSQL server is terminated here
    @request.addfinalizer
    def drop_database():
        postgresql.stop()


@pytest.fixture(scope="function")
def browse_files():
    """

    purpose of this function to return file objects to perform testing on
      combination of single and multiple filters
      and single sorting

    returns 28 file objects associated with consignments

    there are 6 bodies defined as Transferring bodies,

    there are 6 series defined as Series (linked directly to one transferring body)

    there are 12 consignment objects (1 to 12) associated with transferring body and series
      consignment_1 and consignment_2 associated to body_1 and series_1
      consignment_3 and consignment_4 associated to body_2 and series_2
      consignment_5 and consignment_6 associated to body_3 and series_3
      consignment_7 and consignment_8 associated to body_4 and series_4
      consignment_9 and consignment_10 associated to body_5 and series_5
      consignment_11 associated to body_6 and series_6

      each consignment has a unique ConsignmentReference to support filter
      each consignment has a unique TransferCompleteDatetime to support date filters

    there are 28 file objects (1 to 28) associated with consignments
      file_1 associated to consignment_1
      file_2 and file_3 associated to consignment_2
      file_4 , file_5 and file_6 associated to consignment_3
      file_7 , file_8, file_9 and file_10 associated to consignment_4
      file_11 associated to consignment_5
      file_12 and file_3 associated to consignment_6
      file_14 , file_15 and file_16 associated to consignment_7
      file_17 , file_18 and file_19 associated to consignment_8
      file_20 and file_21 associated to consignment_9
      file_22 , file_23, file_24 and file_25 associated to consignment_10
      file_26 and file_27 associated to consignment_11
    """

    body_1 = BodyFactory(Name="first_body", Description="first_body")
    body_2 = BodyFactory(Name="second_body", Description="second_body")
    body_3 = BodyFactory(Name="third_body", Description="third_body")
    body_4 = BodyFactory(Name="fourth_body", Description="fourth_body")
    body_5 = BodyFactory(Name="fifth_body", Description="fifth_body")
    body_6 = BodyFactory(Name="sixth_body", Description="sixth_body")

    series_1 = SeriesFactory(
        Name="first_series", Description="first_series", body=body_1
    )
    series_2 = SeriesFactory(
        Name="second_series", Description="second_series", body=body_2
    )
    series_3 = SeriesFactory(
        Name="third_series", Description="third_series", body=body_3
    )
    series_4 = SeriesFactory(
        Name="fourth_series", Description="fourth_series", body=body_4
    )
    series_5 = SeriesFactory(
        Name="fifth_series", Description="fifth_series", body=body_5
    )

    series_6 = SeriesFactory(
        Name="sixth_series", Description="sixth_series", body=body_6
    )

    consignment_1 = ConsignmentFactory(
        series=series_1,
        ConsignmentReference="TDR-2023-FI1",
        TransferCompleteDatetime="2023-01-13",
    )
    consignment_2 = ConsignmentFactory(
        series=series_1,
        ConsignmentReference="TDR-2023-SE2",
        TransferCompleteDatetime="2023-02-7",
    )

    consignment_3 = ConsignmentFactory(
        series=series_2,
        ConsignmentReference="TDR-2023-TH3",
        TransferCompleteDatetime="2023-03-15",
    )
    consignment_4 = ConsignmentFactory(
        series=series_2,
        ConsignmentReference="TDR-2023-FO4",
        TransferCompleteDatetime="2023-04-26",
    )

    consignment_5 = ConsignmentFactory(
        series=series_3,
        ConsignmentReference="TDR-2023-FI5",
        TransferCompleteDatetime="2023-05-10",
    )
    consignment_6 = ConsignmentFactory(
        series=series_3,
        ConsignmentReference="TDR-2023-SI6",
        TransferCompleteDatetime="2023-06-17",
    )

    consignment_7 = ConsignmentFactory(
        series=series_4,
        ConsignmentReference="TDR-2023-SE7",
        TransferCompleteDatetime="2023-07-21",
    )
    consignment_8 = ConsignmentFactory(
        series=series_4,
        ConsignmentReference="TDR-2023-EI8",
        TransferCompleteDatetime="2023-08-3",
    )

    consignment_9 = ConsignmentFactory(
        series=series_5,
        ConsignmentReference="TDR-2023-NI9",
        TransferCompleteDatetime="2023-09-21",
    )
    consignment_10 = ConsignmentFactory(
        series=series_5,
        ConsignmentReference="TDR-2023-TE10",
        TransferCompleteDatetime="2023-09-21",
    )

    consignment_11 = ConsignmentFactory(
        series=series_6,
        ConsignmentReference="TDR-2023-EL11",
        TransferCompleteDatetime="2023-10-14",
    )

    file_1 = FileFactory(
        consignment=consignment_1,
        FileType="File",
        FileName="first_file.txt",
        FilePath="/data/first_file.txt",
    )

    file_2 = FileFactory(
        consignment=consignment_2,
        FileType="File",
        FileName="second_file.pdf",
        FilePath="/data/second_file.pdf",
    )

    file_3 = FileFactory(
        consignment=consignment_2,
        FileType="File",
        FileName="third_file.doc",
        FilePath="/data/third_file.doc",
    )

    file_4 = FileFactory(
        consignment=consignment_3,
        FileType="File",
        FileName="fourth_file.docx",
        FilePath="/data/fourth_file.docx",
    )

    file_5 = FileFactory(
        consignment=consignment_3,
        FileType="File",
        FileName="fifth_file.docx",
        FilePath="/data/fifth_file.docx",
    )

    file_6 = FileFactory(
        consignment=consignment_3,
        FileType="File",
        FileName="sixth_file.ppt",
        FilePath="/data/sixth_file.ppt",
    )

    file_7 = FileFactory(
        consignment=consignment_4,
        FileType="File",
        FileName="seventh_file.xls",
        FilePath="/data/seventh_file.xls",
    )

    file_8 = FileFactory(
        consignment=consignment_4,
        FileType="File",
        FileName="eighth_file.pdf",
        FilePath="/data/seventh_file.pdf",
    )

    file_9 = FileFactory(
        consignment=consignment_4,
        FileType="File",
        FileName="ninth_file.txt",
        FilePath="/data/ninth_file.txt",
    )

    file_10 = FileFactory(
        consignment=consignment_4,
        FileType="File",
        FileName="tenth_file.ppt",
        FilePath="/data/tenth_file.ppt",
    )

    file_11 = FileFactory(
        consignment=consignment_5,
        FileType="File",
        FileName="eleventh_file.zip",
        FilePath="/data/eleventh_file.zip",
    )

    file_12 = FileFactory(
        consignment=consignment_6,
        FileType="File",
        FileName="twelfth_file.ppt",
        FilePath="/data/twelfth_file.ppt",
    )

    file_13 = FileFactory(
        consignment=consignment_6,
        FileType="File",
        FileName="thirteenth_file.docx",
        FilePath="/data/thirteenth_file.docx",
    )

    file_14 = FileFactory(
        consignment=consignment_7,
        FileType="File",
        FileName="fourteenth_file.ppt",
        FilePath="/data/fourteenth_file.ppt",
    )

    file_15 = FileFactory(
        consignment=consignment_7,
        FileType="File",
        FileName="fifteenth_file.png",
        FilePath="/data/fifteenth_file.png",
    )

    file_16 = FileFactory(
        consignment=consignment_7,
        FileType="File",
        FileName="sixteenth_file.gif",
        FilePath="/data/sixteenth_file.gif",
    )

    file_17 = FileFactory(
        consignment=consignment_8,
        FileType="File",
        FileName="seventeenth_file.pdf",
        FilePath="/data/seventeenth_file.pdf",
    )

    file_18 = FileFactory(
        consignment=consignment_8,
        FileType="File",
        FileName="eighteenth_file.xls",
        FilePath="/data/eighteenth_file.xls",
    )

    file_19 = FileFactory(
        consignment=consignment_8,
        FileType="File",
        FileName="nineteenth_file.ppt",
        FilePath="/data/nineteenth_file.ppt",
    )

    file_20 = FileFactory(
        consignment=consignment_9,
        FileType="File",
        FileName="twentieth_file.tiff",
        FilePath="/data/twentieth_file.tiff",
    )

    file_21 = FileFactory(
        consignment=consignment_9,
        FileType="File",
        FileName="twenty-first.ppt",
        FilePath="/data/twenty-first.ppt",
    )

    file_22 = FileFactory(
        consignment=consignment_10,
        FileType="File",
        FileName="twenty-second.doc",
        FilePath="/data/twenty-second.doc",
    )

    file_23 = FileFactory(
        consignment=consignment_10,
        FileType="File",
        FileName="twenty-third.docx",
        FilePath="/data/twenty-third.docx",
    )

    file_24 = FileFactory(
        consignment=consignment_10,
        FileType="File",
        FileName="twenty-fourth.docx",
        FilePath="/data/twenty-fourth.docx",
    )

    file_25 = FileFactory(
        consignment=consignment_10,
        FileType="File",
        FileName="twenty-fifth.xls",
        FilePath="/data/twenty-fifth.xls",
    )

    file_26 = FileFactory(
        consignment=consignment_11,
        FileType="File",
        FileName="twenty-sixth.docx",
        FilePath="/data/twenty-sixth.docx",
    )

    file_27 = FileFactory(
        consignment=consignment_11,
        FileType="File",
        FileName="twenty-seventh.xls",
        FilePath="/data/twenty-seventh.xls",
    )

    return [
        file_1,
        file_2,
        file_3,
        file_4,
        file_5,
        file_6,
        file_7,
        file_8,
        file_9,
        file_10,
        file_11,
        file_12,
        file_13,
        file_14,
        file_15,
        file_16,
        file_17,
        file_18,
        file_19,
        file_20,
        file_21,
        file_22,
        file_23,
        file_24,
        file_25,
        file_26,
        file_27,
    ]


@pytest.fixture(scope="function")
def browse_transferring_body_files():
    """

    purpose of this function to return file objects to perform testing on
      combination of single and multiple filters
      and single sorting

    returns 5 file objects associated with consignments

    there is 1 body defined as Transferring bodies,

    there are 3 series defined as Series in one body

    there are 3 consignment objects (1 to 3) associated with transferring body and series
      consignment_1 associated to body_1 and series_1
      consignment_2 associated to body_1 and series_2
      consignment_3 associated to body_1 and series_3

      each consignment has a unique TransferCompleteDatetime to support date filters

    there are 5 file objects (1 to 5) associated with consignments

      file_1 and file_2 associated to consignment_1
      file_3 and file_4 associated to consignment_2
      file_5 associated to consignment_3
    """

    body_1 = BodyFactory(Name="first_body", Description="first_body")

    series_1 = SeriesFactory(
        Name="first_series", Description="first_series", body=body_1
    )

    series_2 = SeriesFactory(
        Name="second_series", Description="second_series", body=body_1
    )

    series_3 = SeriesFactory(
        Name="third_series", Description="third_series", body=body_1
    )

    consignment_1 = ConsignmentFactory(
        series=series_1,
        ConsignmentReference="TDR-2023-FI1",
        TransferCompleteDatetime="2023-10-14",
    )

    consignment_2 = ConsignmentFactory(
        series=series_2,
        ConsignmentReference="TDR-2023-SE2",
        TransferCompleteDatetime="2023-03-30",
    )

    consignment_3 = ConsignmentFactory(
        series=series_3,
        ConsignmentReference="TDR-2023-TH3",
        TransferCompleteDatetime="2023-07-07",
    )

    file_1 = FileFactory(
        consignment=consignment_1,
        FileType="File",
        FileName="first_file.docx",
        FilePath="/data/first_file.docx",
    )

    file_2 = FileFactory(
        consignment=consignment_2,
        FileType="File",
        FileName="second_file.xls",
        FilePath="/data/second_file.xls",
    )

    file_3 = FileFactory(
        consignment=consignment_2,
        FileType="File",
        FileName="third_file.docx",
        FilePath="/data/third_file.docx",
    )

    file_4 = FileFactory(
        consignment=consignment_3,
        FileType="File",
        FileName="fourth-file.pdf",
        FilePath="/data/fourth-file.pdf",
    )

    file_5 = FileFactory(
        consignment=consignment_3,
        FileType="File",
        FileName="fifth-file.xls",
        FilePath="/data/fifth-file.xls",
    )

    file_6 = FileFactory(
        consignment=consignment_3,
        FileType="File",
        FileName="sixth-file.xls",
        FilePath="/data/sixth-file.xls",
    )

    return [
        file_1,
        file_2,
        file_3,
        file_4,
        file_5,
        file_6,
    ]


@pytest.fixture(scope="function")
def browse_consignment_files():
    """

    purpose of this function to return file objects to perform testing on
      combination of single and multiple filters
      and single sorting

    returns 5 file objects associated with consignments

    there is 1 body defined as Transferring bodies,

    there is 1 series defined as Series in one body

    there is a 1 consignment object associated with transferring body and series
      consignment_1 associated to body_1 and series_1

    there are 5 file objects (1 to 5) associated with consignment

    file_1, file_2, file_3, file_4 and file_5 associated to consignment_1
    """

    body_1 = BodyFactory(Name="first_body", Description="first_body")

    series_1 = SeriesFactory(
        Name="first_series", Description="first_series", body=body_1
    )

    consignment_1 = ConsignmentFactory(
        series=series_1,
        ConsignmentReference="TDR-2023-FI1",
        TransferCompleteDatetime="2023-10-14",
    )

    file_1 = FileFactory(
        consignment=consignment_1,
        FileName="first_file.docx",
        FileType="file",
    )

    FileMetadataFactory(
        file=file_1,
        PropertyName="date_last_modified",
        Value="2023-02-25T10:12:47",
    )

    FileMetadataFactory(
        file=file_1, PropertyName="closure_type", Value="Closed"
    )
    FileMetadataFactory(
        file=file_1,
        PropertyName="opening_date",
        Value="2023-02-25T11:14:34",
    )

    file_2 = FileFactory(
        consignment=consignment_1,
        FileName="second_file.ppt",
        FileType="file",
    )
    FileMetadataFactory(
        file=file_2,
        PropertyName="date_last_modified",
        Value="2023-01-15T12:28:08",
    )
    FileMetadataFactory(file=file_2, PropertyName="closure_type", Value="Open")
    FileMetadataFactory(file=file_2, PropertyName="opening_date", Value=None)

    file_3 = FileFactory(
        consignment=consignment_1,
        FileName="third_file.docx",
        FileType="file",
    )

    FileMetadataFactory(
        file=file_3,
        PropertyName="date_last_modified",
        Value="2023-03-10T10:12:47",
    )

    FileMetadataFactory(
        file=file_3, PropertyName="closure_type", Value="Closed"
    )
    FileMetadataFactory(
        file=file_3,
        PropertyName="opening_date",
        Value="2090-03-10T10:12:47",
    )

    file_4 = FileFactory(
        consignment=consignment_1,
        FileName="fourth_file.xls",
        FileType="file",
    )

    FileMetadataFactory(
        file=file_4,
        PropertyName="date_last_modified",
        Value="2023-04-12T10:12:47",
    )

    FileMetadataFactory(
        file=file_4, PropertyName="closure_type", Value="Closed"
    )
    FileMetadataFactory(
        file=file_4,
        PropertyName="opening_date",
        Value="2070-03-25T10:12:47",
    )

    file_5 = FileFactory(
        consignment=consignment_1,
        FileName="fifth_file.doc",
        FileType="file",
    )

    FileMetadataFactory(
        file=file_5,
        PropertyName="date_last_modified",
        Value="2023-05-20T10:12:47",
    )

    FileMetadataFactory(file=file_5, PropertyName="closure_type", Value="Open")
    FileMetadataFactory(
        file=file_5,
        PropertyName="opening_date",
        Value=None,
    )

    return [
        file_1,
        file_2,
        file_3,
        file_4,
        file_5,
    ]


@pytest.fixture(scope="function")
def record_files():
    """

    purpose of this function to return file objects to perform testing on
      displaying record metadata based on the closure type status

    returns 3 file objects associated with consignments

    there is 1 body defined as Transferring bodies,

    there is 1 series defined as Series in one body

    there is a 1 consignment object associated with transferring body and series
      consignment_1 associated to body_1 and series_1

    there are 5 file objects (1 to 5) associated with consignment

    file_1, file_2, file_3 associated to consignment_1
    """

    body_1 = BodyFactory(Name="first_body", Description="first_body")

    series_1 = SeriesFactory(
        Name="first_series", Description="first_series", body=body_1
    )

    consignment_1 = ConsignmentFactory(
        series=series_1,
        ConsignmentReference="TDR-2023-FI1",
        TransferCompleteDatetime="2023-10-14",
    )

    # file with closure type - Open
    file_1 = FileFactory(
        consignment=consignment_1,
        FileName="open_file.docx",
        FileType="file",
        FileReference="ABCDE",
        FilePath="data/content/test_folder/open_file.docx",
        CiteableReference="first_body/ABCDE",
    )
    file_1_metadata = {
        "file_object": file_1,
        "description": FileMetadataFactory(
            file=file_1, PropertyName="description", Value="open document file"
        ),
        "closure_type": FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Open"
        ),
        "date_last_modified": FileMetadataFactory(
            file=file_1, PropertyName="date_last_modified", Value="2023-01-15"
        ),
        "former_reference": FileMetadataFactory(
            file=file_1, PropertyName="former_reference_department", Value="-"
        ),
        "translated_title": FileMetadataFactory(
            file=file_1, PropertyName="file_name_translation", Value="-"
        ),
        "held_by": FileMetadataFactory(
            file=file_1,
            PropertyName="held_by",
            Value="The National Archives, Kew",
        ),
        "legal_status": FileMetadataFactory(
            file=file_1, PropertyName="legal_status", Value="Public record(s)"
        ),
        "rights_copyright": FileMetadataFactory(
            file=file_1,
            PropertyName="rights_copyright",
            Value="Crown copyright",
        ),
        "language": FileMetadataFactory(
            file=file_1, PropertyName="language", Value="English"
        ),
    }

    # file with closure type - Open , but has closure start date and closure period - as it was once closed
    file_2 = FileFactory(
        consignment=consignment_1,
        FileName="open_file_once_closed.pdf",
        FileType="file",
        FileReference="ABCDE",
        FilePath="data/content/test_folder/open_file_once_closed.pdf",
        CiteableReference="first_body/ABCDE",
    )
    file_2_metadata = {
        "file_object": file_2,
        "alternative_title": FileMetadataFactory(
            file=file_2, PropertyName="title_alternate", Value="alternate title"
        ),
        "description": FileMetadataFactory(
            file=file_2,
            PropertyName="description",
            Value="open once closed document file",
        ),
        "alternative_description": FileMetadataFactory(
            file=file_2, PropertyName="description_alternate", Value="-"
        ),
        "closure_type": FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        ),
        "date_last_modified": FileMetadataFactory(
            file=file_2, PropertyName="date_last_modified", Value="2023-01-15"
        ),
        "opening_date": FileMetadataFactory(
            file=file_2, PropertyName="opening_date", Value="2023-02-25"
        ),
        "closure_start_date": FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value="2023-01-15"
        ),
        "closure_period": FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value="10"
        ),
        "foi_exemption_code": FileMetadataFactory(
            file=file_2, PropertyName="foi_exemption_code", Value="14(2)(b)"
        ),
        "former_reference": FileMetadataFactory(
            file=file_2,
            PropertyName="former_reference_department",
            Value="former reference",
        ),
        "translated_title": FileMetadataFactory(
            file=file_2, PropertyName="file_name_translation", Value="-"
        ),
        "held_by": FileMetadataFactory(
            file=file_2,
            PropertyName="held_by",
            Value="The National Archives, Kew",
        ),
        "legal_status": FileMetadataFactory(
            file=file_2, PropertyName="legal_status", Value="Public record(s)"
        ),
        "rights_copyright": FileMetadataFactory(
            file=file_2,
            PropertyName="rights_copyright",
            Value="Crown copyright",
        ),
        "language": FileMetadataFactory(
            file=file_2, PropertyName="language", Value="English"
        ),
    }

    # file with closure type - Closed
    file_3 = FileFactory(
        consignment=consignment_1,
        FileName="closed_file.pdf",
        FileType="file",
        FileReference="ABCDE",
        FilePath="data/content/test_folder/closed_file.pdf",
        CiteableReference="first_body/ABCDE",
    )
    file_3_metadata = {
        "file_object": file_3,
        "alternative_title": FileMetadataFactory(
            file=file_3, PropertyName="title_alternate", Value="alternate title"
        ),
        "description": FileMetadataFactory(
            file=file_3,
            PropertyName="description",
            Value="closed document file",
        ),
        "alternative_description": FileMetadataFactory(
            file=file_3, PropertyName="description_alternate", Value="-"
        ),
        "closure_type": FileMetadataFactory(
            file=file_3, PropertyName="closure_type", Value="Closed"
        ),
        "date_last_modified": FileMetadataFactory(
            file=file_3, PropertyName="date_last_modified", Value="2023-01-15"
        ),
        "opening_date": FileMetadataFactory(
            file=file_3, PropertyName="opening_date", Value="2023-02-25"
        ),
        "closure_start_date": FileMetadataFactory(
            file=file_3, PropertyName="closure_start_date", Value="2023-01-15"
        ),
        "closure_period": FileMetadataFactory(
            file=file_3, PropertyName="closure_period", Value="10"
        ),
        "foi_exemption_code": FileMetadataFactory(
            file=file_3, PropertyName="foi_exemption_code", Value="14(2)(b)"
        ),
        "former_reference": FileMetadataFactory(
            file=file_3,
            PropertyName="former_reference_department",
            Value="former reference",
        ),
        "translated_title": FileMetadataFactory(
            file=file_3, PropertyName="file_name_translation", Value="-"
        ),
        "held_by": FileMetadataFactory(
            file=file_3,
            PropertyName="held_by",
            Value="The National Archives, Kew",
        ),
        "legal_status": FileMetadataFactory(
            file=file_3, PropertyName="legal_status", Value="Public record(s)"
        ),
        "rights_copyright": FileMetadataFactory(
            file=file_3,
            PropertyName="rights_copyright",
            Value="Crown copyright",
        ),
        "language": FileMetadataFactory(
            file=file_3, PropertyName="language", Value="English"
        ),
    }

    # file with no metadata
    file_4 = FileFactory(
        consignment=consignment_1,
        FileName="file_no_metadata.docx",
        FileType="file",
        FileReference="ABCDE",
        FilePath="data/content/test_folder/file_no_metadata.docx",
        CiteableReference="first_body/ABCDE",
    )
    file_4_metadata = {
        "file_object": file_4,
        "alternative_title": FileMetadataFactory(
            file=file_3, PropertyName="title_alternate", Value=None
        ),
        "description": FileMetadataFactory(
            file=file_3, PropertyName="description", Value=None
        ),
        "alternative_description": FileMetadataFactory(
            file=file_3, PropertyName="description_alternate", Value=None
        ),
        "closure_type": FileMetadataFactory(
            file=file_3, PropertyName="closure_type", Value=None
        ),
        "date_last_modified": FileMetadataFactory(
            file=file_3, PropertyName="date_last_modified", Value=None
        ),
        "opening_date": FileMetadataFactory(
            file=file_3, PropertyName="opening_date", Value=None
        ),
        "closure_start_date": FileMetadataFactory(
            file=file_3, PropertyName="closure_start_date", Value=None
        ),
        "closure_period": FileMetadataFactory(
            file=file_3, PropertyName="closure_period", Value=None
        ),
        "foi_exemption_code": FileMetadataFactory(
            file=file_3, PropertyName="foi_exemption_code", Value=None
        ),
        "former_reference": FileMetadataFactory(
            file=file_3, PropertyName="former_reference_department", Value=None
        ),
        "translated_title": FileMetadataFactory(
            file=file_3, PropertyName="file_name_translation", Value=None
        ),
        "held_by": FileMetadataFactory(
            file=file_3, PropertyName="held_by", Value=None
        ),
        "legal_status": FileMetadataFactory(
            file=file_3, PropertyName="legal_status", Value=None
        ),
        "rights_copyright": FileMetadataFactory(
            file=file_3, PropertyName="rights_copyright", Value=None
        ),
        "language": FileMetadataFactory(
            file=file_3, PropertyName="language", Value=None
        ),
    }

    # file without citeable reference
    file_5 = FileFactory(
        consignment=consignment_1,
        FileName="file_no_metadata.docx",
        FileType="file",
        FileReference="ABCDE",
        FilePath="data/content/test_folder/file_without_citeable_reference.docx",
        CiteableReference=None,
    )
    file_5_metadata = {
        "file_object": file_5,
        "description": FileMetadataFactory(
            file=file_5,
            PropertyName="description",
            Value="file without citeable reference",
        ),
        "closure_type": FileMetadataFactory(
            file=file_5, PropertyName="closure_type", Value="Open"
        ),
        "date_last_modified": FileMetadataFactory(
            file=file_5, PropertyName="date_last_modified", Value="2023-01-15"
        ),
        "former_reference": FileMetadataFactory(
            file=file_5, PropertyName="former_reference_department", Value="-"
        ),
        "translated_title": FileMetadataFactory(
            file=file_5, PropertyName="file_name_translation", Value="-"
        ),
        "held_by": FileMetadataFactory(
            file=file_5,
            PropertyName="held_by",
            Value="The National Archives, Kew",
        ),
        "legal_status": FileMetadataFactory(
            file=file_5, PropertyName="legal_status", Value="Public record(s)"
        ),
        "rights_copyright": FileMetadataFactory(
            file=file_5,
            PropertyName="rights_copyright",
            Value="Crown copyright",
        ),
        "language": FileMetadataFactory(
            file=file_5, PropertyName="language", Value="English"
        ),
    }

    return [
        file_1_metadata,
        file_2_metadata,
        file_3_metadata,
        file_4_metadata,
        file_5_metadata,
    ]
