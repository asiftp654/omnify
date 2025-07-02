from rest_framework.response import Response
from rest_framework import status
from typing import Any, Dict, List, Optional, Union


# This class is used to return a standardized response to the client.
class APIResponse:
    
    @staticmethod
    def success(
        data: Any = None, 
        message: str = "Success", 
        status_code: int = status.HTTP_200_OK
    ) -> Response:
        
        response_data = {
            "success": True,
            "message": message,
            "data": data
        }
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        errors: Optional[Union[Dict, List]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> Response:
        
        response_data = {
            "success": False,
            "message": message,
            "errors": errors
        }
        return Response(response_data, status=status_code)
    