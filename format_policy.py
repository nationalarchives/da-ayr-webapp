"""Shared viewer, conversion and text extraction format policies."""

UNIVERSAL_VIEWER_SUPPORTED_IMAGE_PUIDS = {
    "fmt/3": "gif",
    "fmt/4": "gif",
    "fmt/43": "jpg",
    "fmt/44": "jpg",
    "x-fmt/391": "jpg",
    "fmt/11": "png",
    "fmt/12": "png",
    "fmt/13": "png",
    "fmt/353": "tif",
    "fmt/567": "webp",
}

UNIVERSAL_VIEWER_SUPPORTED_APPLICATION_PUIDS = {
    "fmt/16": "pdf",
    "fmt/17": "pdf",
    "fmt/18": "pdf",
    "fmt/19": "pdf",
    "fmt/20": "pdf",
    "fmt/276": "pdf",
}

CONVERTIBLE_PUIDS = {
    "fmt/39": "doc",
    "fmt/40": "doc",
    "x-fmt/44": "doc",
    "x-fmt/45": "doc",
    "fmt/50": "rtf",
    "fmt/59": "xls",
    "fmt/61": "xls",
    "x-fmt/111": "txt",
    "x-fmt/116": "wk4",
    "fmt/126": "ppt",
    "fmt/214": "xlsx",
    "fmt/215": "pptx",
    "fmt/355": "rtf",
    "x-fmt/394": "wp",
    "fmt/412": "docx",
    "x-fmt/115": "wk3",
    "fmt/116": "bmp",
    "x-fmt/258": "vsd",
    "fmt/443": "vsd",
    "fmt/1510": "vsd",
    "x-fmt/255": "pub",
    "x-fmt/332": "fm3",
    "x-fmt/18": "csv",
}

TEXTRACT_FILE_PUIDS_CONVERT_TO_SUPPORTED_MAP = {
    "x-fmt/44": "fmt/412",  # .wpd to .docx
    "x-fmt/45": "fmt/412",  # .dot to .docx
    "x-fmt/394": "fmt/412",  # .wpd to .docx
    "fmt/126": "fmt/215",  # .ppt to .pptx
    "x-fmt/115": "fmt/214",  # .wk3 to .xlsx
    "x-fmt/116": "fmt/214",  # .wk4 to .xlsx
    "fmt/116": "fmt/20",  # .bmp to .pdf
    "x-fmt/258": "fmt/20",  # .vsd to .pdf
    "fmt/1510": "fmt/20",  # .vsd to .pdf
    "fmt/443": "fmt/20",  # .vsd to .pdf
    "x-fmt/255": "fmt/20",  # .pub to .pdf
    "x-fmt/332": "fmt/20",  # .fm3 to .pdf
}

TEXTRACT_FILE_PUIDS_FALLBACK_CONVERSION_MAP = {
    "fmt/59": "fmt/214",  # .xls to .xlsx
    "fmt/61": "fmt/214",  # .xls to .xlsx
    "fmt/39": "fmt/412",  # .doc to .docx
    "fmt/40": "fmt/412",  # .doc to .docx
    "fmt/609": "fmt/412",  # .doc to .docx
}

SUPPORTED_TEXTRACT_PUIDS = {
    "x-fmt/111": "txt",
    "x-fmt/18": "csv",
    "fmt/39": "doc",
    "fmt/40": "doc",
    "fmt/609": "doc",
    "fmt/412": "docx",
    "fmt/45": "rtf",
    "fmt/50": "rtf",
    "fmt/52": "rtf",
    "fmt/53": "rtf",
    "fmt/355": "rtf",
    "fmt/136": "odt",
    "fmt/290": "odt",
    "fmt/291": "odt",
    "fmt/14": "pdf",
    "fmt/15": "pdf",
    "fmt/16": "pdf",
    "fmt/17": "pdf",
    "fmt/18": "pdf",
    "fmt/19": "pdf",
    "fmt/20": "pdf",
    "fmt/276": "pdf",
    "fmt/95": "pdf",
    "fmt/354": "pdf",
    "fmt/476": "pdf",
    "fmt/477": "pdf",
    "fmt/478": "pdf",
    "fmt/479": "pdf",
    "fmt/480": "pdf",
    "fmt/481": "pdf",
    "fmt/488": "pdf",
    "fmt/489": "pdf",
    "fmt/490": "pdf",
    "fmt/491": "pdf",
    "fmt/492": "pdf",
    "fmt/493": "pdf",
    "fmt/144": "pdf",
    "fmt/145": "pdf",
    "fmt/146": "pdf",
    "fmt/147": "pdf",
    "fmt/148": "pdf",
    "fmt/157": "pdf",
    "fmt/158": "pdf",
    "fmt/278": "eml",
    "x-fmt/430": "msg",
    "fmt/3": "gif",
    "fmt/4": "gif",
    "fmt/42": "jpg",
    "fmt/43": "jpg",
    "fmt/44": "jpg",
    "x-fmt/391": "jpg",
    "fmt/11": "png",
    "fmt/12": "png",
    "fmt/13": "png",
    "fmt/353": "tif",
    "fmt/59": "xls",
    "fmt/61": "xls",
    "fmt/214": "xlsx",
    "fmt/215": "pptx",
}
