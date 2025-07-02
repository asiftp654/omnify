from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page' 
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return {
            'total_items': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next_page': self.get_next_link(),
            'previous_page': self.get_previous_link(),
            'results': data
        }
