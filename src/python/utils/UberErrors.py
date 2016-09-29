#!/home/grad3/harshal/py_env/my_env/python2.7

class ErrorDetails(object):
    """Class to standardize errors"""

    def __init__(self, status, code, title):
        self.status = status
        self.code = code
        self.title = title

    def __repr__(self):
        return "Error Details: {} {} {}".format(
            str(self.status),
            str(self.code),
            str(self.title)
        )

class APIError(Exception):
    """Parent class of all Uber API errors"""
    pass


class HTTPError(APIError):
    """Parent class of all HTTP errors"""

    def _adapt_response(self, response):
        """Convert error responses to standard ErrorDetails"""
        status = response[0]
        body = response[1]

        code = body.pop('code')
        title = body.pop('message')
        meta = body # save whatever is left in the response

        e = [ErrorDetails(status, code, title)]

        return e, meta
   
class ClientError(HTTPError):
    """Raise for 4XX Errors"""

    def __init__(self, response, message=None):
        """
        Parameters
            response
                The 4XX HTTP response
            message
                An error message string. If not provided,
                use default one.
        """
        if not message:
            message = (
                    'The request could not be fulfilled due to fault from '
                    'client sending the request.'
            )

        super(ClientError, self).__init__(message)
        errors, meta = super(ClientError, self)._adapt_response(response)
        self.errors = errors
        self.meta = meta

class ServerError(HTTPError):
    """Raise for 5XX Errors"""

    def __init__(self, response, message=None):
        """
        Parameters
            response
                The 5XX HTTP response
            message
                An error message string. If not provided,
                use default one.
        """
        if not message:
            message = (
                    'The server encountered an error or,
                    is unable to process request.'
            )

        super(ServerError, self).__init__(message)
        self.error, self.meta = self._adapt_response(response)

    def __adapt_response(self, response):
        """Convert error responses to standard ErrorDetails"""
        errors, meta = super(ServerError, self)._adapt_response(response)
        return errors[0], meta
