# !/home/grad3/harshal/py_env/my_env/bin/python2.7

# Append root directory to system path
import sys
sys.path.append('..')

import random
import urllib
from fake_useragent import UserAgent
import pycurl
import cStringIO
from config.constants import constants

class request:
    """
    This class handles all requests using pyCurl
    Handles proxy usage if use_proxy is set True
    """

    def __init__(self, use_proxy=False):
        if use_proxy:
            self.proxy_authentication = constants.proxy_authentication
            self.username = constants.proxy_username
            self.password = constants.proxy_password
            self.http_proxy_list = constants.http_proxies
            self.socks_proxy_list = constants.socks_proxies

        self.ua = UserAgent()
        self.use_proxy = use_proxy
        self.last_sent_proxy_type = None
        self.last_sent_proxy = None


    def set_proxy(self, curl):
        """
        Selects randomly between all available HTTP and SOCKS proxies

        returns: curl object
        """

        self.last_sent_proxy = random.choice(self.http_proxy_list + self.socks_proxy_list)
        if self.last_sent_proxy in self.http_proxy_list:
            self.last_sent_proxy_type = 'HTTP'
            curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)
        else:
            self.last_sent_proxy_type = 'SOCKS'
            curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)

        curl.setopt(pycurl.PROXY, self.last_sent_proxy.split(':')[0])
        curl.setopt(pycurl.PROXYPORT, int(self.last_sent_proxy.split(':')[1]))

        return curl


    def remove_proxy(self):
        """
        Removes rogue proxies from the lists
        """

        if self.last_sent_proxy_type == 'HTTP':
            self.http_proxy_list.remove(self.last_sent_proxy)
        else:
            self.socks_proxy_list.remove(self.last_sent_proxy)


    def fetch(self, url, data=None):
        """
        Fetches html webpage for given url

        returns: tuple (http_status_code, page source of url)
        """

        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)

        buff = cStringIO.StringIO()
        hdr = cStringIO.StringIO()
        
        c.setopt(pycurl.HEADERFUNCTION, hdr.write)
        c.setopt(pycurl.WRITEFUNCTION, buff.write)
        c.setopt(pycurl.COOKIEJAR, '.cookiejar')
        c.setopt(pycurl.COOKIEFILE, '.cookiejar')

        c.setopt(pycurl.TIMEOUT, 10)
        c.setopt(pycurl.USERAGENT, self.ua.random)

        if data:
            c.setopt(pycurl.POSTFIELDS, urllib.urlencode(data))
        
        if self.use_proxy:
            if self.proxy_authentication:
                c.setopt(pycurl.PROXYUSERPWD, "{0}:{1}".format(self.username, self.password))
            c = self.set_proxy(c)

        while True:
            try:
                c.perform()
            except pycurl.error, e:
                self.remove_proxy()
                c = self.set_proxy(c)
            else:
                return (c.getinfo(pycurl.HTTP_CODE), buff.getvalue())
