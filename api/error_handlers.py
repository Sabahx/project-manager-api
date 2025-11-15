"""
Custom error handlers for better API responses
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides more detailed error responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the response data
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'message': None,
            'details': None
        }

        # Extract error message
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response_data['message'] = response.data['detail']
            else:
                custom_response_data['message'] = 'An error occurred'
                custom_response_data['details'] = response.data
        else:
            custom_response_data['message'] = str(response.data)

        response.data = custom_response_data

    return response


def success_response(data=None, message='Success', status_code=status.HTTP_200_OK):
    """
    Standardized success response format
    """
    return Response({
        'error': False,
        'status_code': status_code,
        'message': message,
        'data': data
    }, status=status_code)


def error_response(message='An error occurred', details=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Standardized error response format
    """
    return Response({
        'error': True,
        'status_code': status_code,
        'message': message,
        'details': details
    }, status=status_code)
