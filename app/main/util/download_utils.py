def get_download_endpoint_filename(file):
    """
    Generates the download filename based on the file's properties.
    """
    download_filename = file.FileName
    if file.CiteableReference:
        if len(file.FileName.rsplit(".", 1)) > 1:
            download_filename = (
                file.CiteableReference + "." + file.FileName.rsplit(".", 1)[1]
            )
    return download_filename
