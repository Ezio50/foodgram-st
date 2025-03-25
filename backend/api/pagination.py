from rest_framework import pagination

from foodgram import constants


class Standard_Pagination(pagination.PageNumberPagination):
    page_size = constants.PAGE_SIZE
    page_size_query_param = 'limit'
