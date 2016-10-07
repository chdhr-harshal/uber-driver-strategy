#!/home/grad3/harshal/py_env/my_env/bin/python2.7

"""Python Client for Uber API. """

from collections import OrderedDict
from utils.CurlReq import request
from urllib import urlencode
from requests import codes
from utils.UberErrors import *


API_HOST = "https://api.uber.com"

class UberSession(object):
    """Class to store credentials. """
    def __init__(self, server_token):
        """Initialize UberSession.
        
        Parameters
            server_token (str)
                Application's server token
        """
        self.server_token = server_token
    

class UberRidesClient(object):
    """Class to make calls to Uber API. """

    def __init__(self, session):
        """Initialize UberRidesClient.

        Parameters
            session(Session)
                The session object containing access credentials
        """
        self.session = session

    def _build_url(self, target, args=None):
        """Build API query url
    
        Parameters
            target (str)
                The API target (e.g. '/v1/products')
            args (dict)
                Dictionary of arguments required for the request.

        Returns
            url (str)
                The API query url
        """
        return "{0}{1}?{2}".format(API_HOST, target, urlencode(args))
        

    def _api_call(self, method, target, args=None):
        """Create Request object and execute the call to API server.

        Parameters
            method (str)
                HTTP request (e.g. 'GET')
            target (str)
                The API target (e.g. '/v1/products')
            args (dict)
                Dictionary of arguments required for the request

        Returns
            (Response)
                API server's response to the query.
        """
        req = request(use_proxy=True)
        url = self._build_url(target, args)
        response = req.fetch(url, header=['Authorization: Token {0}'.format(self.session.server_token)])

        if response.response_code != codes.ok:
            try:
                raise UberError(response)
            except UberError, e:
                print e.error
        else:
            return response.response_body
        


    def get_products(self, latitude, longitude):
        """Get information about Uber products offered at particular location

        Parameters
            latitude (float)
                The latitude of the location.
            longitude (float)
                The longitude of the location.

        Returns
            (Response)
                A response object containing available products information
        """
        args = OrderedDict([
            ('latitude', latitude),
            ('longitude', longitude)
        ])

        return self._api_call('GET', '/v1/products', args=args)


    def get_product(self, product_id):
        """Get information about particular Uber product.

        Parameters
            product_id (str)
                Unique identifier of the Uber product

        Returns
            (Response)
                A response object containing particular product information
        """
        endpoint = '/v1/products/{0}'.format(product_id)
        return self._api_call('GET', endpoint)

    def get_price_estimates(
        self, 
        start_latitude,
        start_longitude,
        end_latitude,
        end_longitude,
        seat_count=2,
        ):
        """Get price estimates for products at a particular location.

        Parameters
            start_latitude (float)
                The latitude of start location
            start_longitude (float)
                The longitude of start location
            end_latitude (float)
                The latitude of end location
            end_longitude (float)
                The longitude of end location
            seat_count (int)
                The number of seats for UberPOOL. Default and max. value is 2
        
        Returns
            (Response)
                A response object containing each products price estimate
        """
        args = OrderedDict([
            ('start_latitude', start_latitude),
            ('start_longitude', start_longitude),
            ('end_latitude', end_latitude),
            ('end_longitude', end_longitude),
            ('seat_count', seat_count)
        ])

        return self._api_call('GET', '/v1/estimates/price', args=args)
       
    def get_pickup_time_estimates(
        self,
        start_latitude,
        start_longitude,
        ):
        """Get pickup time estimates for products at given location.

        Parameters
            start_latitude (float)
            start_longitude (float)

        Returns
            (Response)
                A response object containing pickup time estimates for each product
        """
        args = OrderedDict([
            ('start_latitude', start_latitude),
            ('start_longitude', start_longitude)
        ])

        return self._api_call('GET', '/v1/estimates/time', args=args)         
