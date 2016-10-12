#!/home/grad3/harshal/py_env/my_env/python2.7

import json

class ErrorDetails(object):
    """Class to standardize errors"""

    def __init__(self, status, code, title):
        self.status = status
        self.code = code
        self.title = title

    def __repr__(self):
        return "Error Details: {} {}".format(
            str(self.code),
            str(self.title)
        )

class APIError(Exception):
    def __init__(self, response):
        """Convert error response to standard ErrorDetails"""
        status = response.response_code
        body = eval(response.response_body)

        code = body.pop('code')
        title = body.pop('message')
        meta = body # save whatever is left in the response

        self.e = ErrorDetails(status, code, title)

    def _get_adapted_response(self):
        return self.e
   
class UberError(APIError):
    """Raise for 4XX Errors"""

    def __init__(self, response):
        """
        Parameters
            response
                The HTTP response
        """

        super(ClientError, self).__init__(response)
        self.error = super(UberError, self)._get_adapted_response()

