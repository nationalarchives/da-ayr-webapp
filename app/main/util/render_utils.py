def get_file_mimetype(file_type):
    if file_type == "pdf":
        return "application/pdf"
    elif file_type in ["png", "jpg", "jpeg"]:
        return f"image/{file_type}"

