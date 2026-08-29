from django.core.paginator import (Paginator,
                                   EmptyPage)
import django.http

RECORDS_PER_PAGE: int = 5
DEFAULT_PAGE_NUMBER: int = 1

def get_page_number_from(
        request: django.http.HttpRequest, default_page_number: int = DEFAULT_PAGE_NUMBER
    ):
    try:
        page_number: int = int(request.GET.get("page", default_page_number))
    
    except ValueError:
        page_number = default_page_number

    return page_number

def get_page_and_page_range_of(
        object_list, page_number: int, per_page: int = RECORDS_PER_PAGE,
        default_page_number: int = DEFAULT_PAGE_NUMBER
    ):
    paginator = Paginator(object_list, per_page)

    try:
        page = paginator.page(page_number)
    
    except EmptyPage:
        page = paginator.page(default_page_number)

    return (page, paginator.page_range)

def get_pagination_page_range(page_number: int, page_range: range):
    left = max(1, page_number - 1)
    right = min(page_number + 1, page_range.stop - 1)

    return range(left, right + 1, 1)