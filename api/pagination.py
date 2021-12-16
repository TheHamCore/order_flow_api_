from rest_framework import pagination
from rest_framework.response import Response


class ContentRangeHeaderPagination(pagination.PageNumberPagination):
    page_query_param = 'offset'
    page_size_query_param = 'limit'

    def get_paginated_response(self, data):
        total_items = self.page.paginator.count
        item_starting_index = self.page.start_index()
        item_ending_index = self.page.end_index()

        content_range = f'items {item_starting_index}-{item_ending_index}/{total_items}'
        headers = {
            'Total objects': total_items,
            'Content-Range': content_range
        }

        return Response(data, headers=headers)
