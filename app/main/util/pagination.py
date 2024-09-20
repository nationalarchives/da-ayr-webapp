def get_pagination(current_page: int, total_pages: int) -> dict | None:
    """
    Generate pagination details for a given page within a total number of pages based on GDS rules.

    This function creates a pagination structure that includes page numbers, ellipses for skipped ranges,
    and information about previous and next pages, based on the current page and total page count.

    Parameters:
    current_page: int - The current active page.
    total_pages: int - The total number of pages available.

    Returns: dict | None
    """
    if total_pages <= 1 or current_page <= 0:
        return None  # if there is just one or 0 pages we won't show pagination

    pages = []

    if current_page > 1:
        pages.append(1)

    if current_page > 3:
        pages.append("ellipses")

    if current_page - 1 > 1:
        pages.append(current_page - 1)

    pages.append(current_page)

    if current_page < total_pages:
        pages.append(current_page + 1)

    if current_page < total_pages - 2:
        pages.append("ellipses")

    if current_page < total_pages - 1:
        pages.append(total_pages)

    previous_page = current_page - 1 if current_page > 1 else None
    next_page = current_page + 1 if current_page < total_pages else None

    return {
        "pages": pages,
        "previous": previous_page,
        "next": next_page,
    }


def calculate_total_pages(total_records: int, records_per_page: int) -> int:
    """
    Calculate the total number of pages required to display all records.

    This function determines the total number of pages needed by dividing the total number
    of records by the number of records per page.

    Parameters:
    ----------
    total_records: int - The total number of records.
    records_per_page: int - The number of records to be displayed per page.

    Returns: int
    """
    return (total_records + records_per_page - 1) // records_per_page


def paginate(items: list, current_page: int, page_size: int):
    """
    Paginate a list of items based on the current page and page size

    Parameters:
    items: list - The list of items
    current_page: int - Current page.
    page_size: int - Amount of items displayed per page,

    Returns: list
    """
    if current_page <= 0 or page_size <= 0:
        return []

    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size

    if current_page > total_pages:
        return []

    start_index = (current_page - 1) * page_size
    end_index = min(start_index + page_size, total_items)

    return items[start_index:end_index]
