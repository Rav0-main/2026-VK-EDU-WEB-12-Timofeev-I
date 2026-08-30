from django.core.paginator import (Paginator,
                                   EmptyPage)
from django.http import HttpRequest

DEFAULT_RECORDS_PER_PAGE: int = 5
DEFAULT_PAGE_NUMBER: int = 1

class PaginationManager:
    __slots__ = ["__page_number", "__paginator"]

    def __init__(self, request: HttpRequest, objs,
                 default_page_number: int = DEFAULT_PAGE_NUMBER, objs_per_page: int = DEFAULT_RECORDS_PER_PAGE):
        try:
            self.__page_number: int = int(request.GET.get("page", default_page_number))
            
        except ValueError:
            self.__page_number = default_page_number

        self.__paginator = Paginator(objs, objs_per_page)

        try:
            self.__paginator.page(self.__page_number)
            
        except EmptyPage:
            self.__page_number = DEFAULT_PAGE_NUMBER

    @property
    def page(self):
        return self.__paginator.page(self.__page_number)

    @property
    def page_range(self):
        return self.__paginator.page_range

    @property
    def range(self):
        left = max(self.__paginator.page_range.start, self.__page_number - 1)
        right = min(self.__page_number + 1, self.__paginator.page_range.stop - 1)
        
        return range(left, right + 1, 1)

    @property
    def first_page(self):
        return self.page_range.start if self.page_range.start != self.range.start else None

    @property
    def last_page(self):
        return self.page_range.stop - 1 if self.range.stop != self.page_range.stop else None