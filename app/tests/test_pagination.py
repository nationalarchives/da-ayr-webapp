import pytest

from app.main.util.pagination import (
    calculate_total_pages,
    get_pagination,
    paginate,
)


class TestPaginationUtilities:
    @pytest.mark.parametrize(
        "items, current_page, page_size, expected_result",
        [
            ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 2, 3, [4, 5, 6]),
            ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 4, 3, [10]),
            ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], -2, 3, []),
            ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], -2, -3, []),
            ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 2, -3, []),
            ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 2, 5, [6, 7, 8, 9, 10]),
            ([1], 10, 1, []),
            ([1], 1, 1000, [1]),
            ([1, 2], 1, 1, [1]),
            ([1, 2], 1, 2, [1, 2]),
            ([], 10, 2, []),
        ],
    )
    def test_paginate_scenarios(
        self, items, current_page, page_size, expected_result
    ):
        """
        Test the calculation of total pages based on total records and records per page in different scenarios.
        """
        result = paginate(items, current_page, page_size)
        assert result == expected_result

    @pytest.mark.parametrize(
        "total_records, records_per_page, expected_result",
        [
            (100, 5, 20),
            (10, 3, 4),
            (12, 5, 3),
            (5, 5, 1),
            (3, 5, 1),
            (14, 7, 2),
            (0, 7, 0),
        ],
    )
    def test_total_pages_calculation_scenarios(
        self, total_records, records_per_page, expected_result
    ):
        """
        Test the calculation of total pages based on total records and records per page in different scenarios.
        """
        result = calculate_total_pages(total_records, records_per_page)
        assert result == expected_result

    def test_returns_none_when_0_or_1_pages(self):
        """
        Test that the pagination function returns None when there are 0 or only 1 page.
        """
        result_0 = get_pagination(0, 0)
        result_1 = get_pagination(0, 1)

        assert result_0 is None
        assert result_1 is None

    def test_no_previous_when_first_page(self):
        """
        Test that when current page is the first previous is None while next is correct
        """
        result = get_pagination(1, 100)
        assert result["previous"] is None
        assert result["next"] == 2

    def test_no_next_when_last_page(self):
        """
        Test that when current page is the last previous is correct while next is None
        """
        result = get_pagination(100, 100)
        assert result["previous"] == 99
        assert result["next"] is None

    @pytest.mark.parametrize(
        "current_page, total_pages, expected_result",
        [
            # if current page is 1 out of 100 outcome is 1 2 ... 100
            (
                1,
                100,
                {"previous": None, "next": 2, "pages": [1, 2, "ellipses", 100]},
            ),
            # if current page is 2 out of 100 outcome is 1 2 3 ... 100
            (
                2,
                100,
                {"previous": 1, "next": 3, "pages": [1, 2, 3, "ellipses", 100]},
            ),
            # if current page is 3 out of 100 outcome is 1 2 3 4 ... 100
            (
                3,
                100,
                {
                    "previous": 2,
                    "next": 4,
                    "pages": [1, 2, 3, 4, "ellipses", 100],
                },
            ),
            # if current page is 4 out of 100 outcome is 1 ... 3 4 5 ... 100
            (
                4,
                100,
                {
                    "previous": 3,
                    "next": 5,
                    "pages": [1, "ellipses", 3, 4, 5, "ellipses", 100],
                },
            ),
            # if current page is 100 out of 100 outcome is 1 ... 99 100
            (
                100,
                100,
                {
                    "previous": 99,
                    "next": None,
                    "pages": [1, "ellipses", 99, 100],
                },
            ),
            # if current page is 99 out of 100 outcome is 1 ... 98 99 100
            (
                99,
                100,
                {
                    "previous": 98,
                    "next": 100,
                    "pages": [1, "ellipses", 98, 99, 100],
                },
            ),
            # if current page is 98 out of 100 outcome is 1 ... 97 98 99 100
            (
                98,
                100,
                {
                    "previous": 97,
                    "next": 99,
                    "pages": [1, "ellipses", 97, 98, 99, 100],
                },
            ),
            # if current page is 97 out of 100 outcome is 1 ... 96 97 98 ... 100
            (
                97,
                100,
                {
                    "previous": 96,
                    "next": 98,
                    "pages": [1, "ellipses", 96, 97, 98, "ellipses", 100],
                },
            ),
            # edge case where there are 5 pages and current is 3, all pages should be visible
            (
                3,
                5,
                {
                    "previous": 2,
                    "next": 4,
                    "pages": [1, 2, 3, 4, 5],
                },
            ),
            # if the number of pages is 1 then pages is None and pagination wont be shown
            (
                1,
                1,
                None,
            ),
            # if the number of pages is 0 then pages is None and pagination wont be shown
            (
                0,
                0,
                None,
            ),
            # edge case where current page is bigger than total number of pages should return None for pages
            (
                1000,
                0,
                None,
            ),
            # edge case where current_page is negative
            (
                -10,
                10,
                None,
            ),
            # edge case where total_pages is negative
            (
                10,
                -10,
                None,
            ),
            # edge case where current_page and total_pages are negative
            (
                -10,
                -10,
                None,
            ),
            # edge case where current_page and total_pages are 0
            (
                0,
                0,
                None,
            ),
        ],
    )
    def test_pagination_return_scenario(
        self, current_page, total_pages, expected_result
    ):
        """
        Test different pagination scenarios based on the current page and total pages.
        """
        result = get_pagination(current_page, total_pages)
        assert result == expected_result
