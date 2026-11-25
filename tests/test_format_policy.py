import configs.base_config as viewer
import format_policy as policy


def test_viewer_reuses_shared_policy():
    assert viewer.CONVERTIBLE_PUIDS is policy.CONVERTIBLE_PUIDS
    assert (
        viewer.UNIVERSAL_VIEWER_SUPPORTED_IMAGE_PUIDS
        is policy.UNIVERSAL_VIEWER_SUPPORTED_IMAGE_PUIDS
    )
    assert (
        viewer.UNIVERSAL_VIEWER_SUPPORTED_APPLICATION_PUIDS
        is policy.UNIVERSAL_VIEWER_SUPPORTED_APPLICATION_PUIDS
    )


def test_representative_format_policy():
    assert policy.UNIVERSAL_VIEWER_SUPPORTED_IMAGE_PUIDS["fmt/353"] == "tif"
    assert policy.CONVERTIBLE_PUIDS["fmt/412"] == "docx"
    assert policy.SUPPORTED_TEXTRACT_PUIDS["fmt/20"] == "pdf"
    assert (
        policy.TEXTRACT_FILE_PUIDS_CONVERT_TO_SUPPORTED_MAP["fmt/116"]
        == "fmt/20"
    )
    assert (
        policy.TEXTRACT_FILE_PUIDS_FALLBACK_CONVERSION_MAP["fmt/59"]
        == "fmt/214"
    )
