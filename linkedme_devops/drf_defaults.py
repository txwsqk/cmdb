"""
Django rest framework default pagination
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Update the structure of the response data.
    if response is not None:
        customized_response = {}
        customized_response['errors'] = []

        for key, value in response.data.items():
            error = {'field': key, 'message': value}
            customized_response['errors'].append(error)

        response.data = customized_response

    return response


class DefaultResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000