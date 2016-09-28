#!/home/grad3/harshal/py_env/my_env/bin/python2.7

class constants:

    # Logger constants. Choose between - 
    # INFO, DEBUG, WARN, ERROR, CRITICAL

    console_log_verbosity = 'INFO'
    file_log_verbosity = 'ERROR'
    log_file = "./log/log"

    # Proxy usage constants
    http_proxy_list = '/research/analytics/proxylist/http_proxylist/proxylist'
    socks_proxy_list = '/research/analytics/proxylist/socks5_proxylist/proxylist'

    proxy_authentication = True
    proxy_credentials = '/research/analytics/proxylist/proxy_credentials'

    if proxy_authentication:
        assert proxy_credentials is not None, "Provide proxy credentials file path"

    proxy_username = None
    proxy_password = None
    http_proxies = []
    socks_proxies = []
   
    if proxy_credentials: 
        f = open(proxy_credentials)
        rows = f.readlines()
        proxy_username = rows[0].strip().split(':')[1]
        proxy_password = rows[1].strip().split(':')[1]
        f.close()

    if http_proxy_list:
        with open(http_proxy_list) as f:
            proxies = f.readlines()
        http_proxies = [proxy.strip() for proxy in proxies]

    if socks_proxy_list:
        with open(socks_proxy_list) as f:
            proxies = f.readlines()
        socks_proxies = [proxy.strip() for proxy in proxies]


    # Database access constants for mysql database
    # To be done : Add support for mongoDB

    database_server = 'ist-www-mysql-prod.bu.edu'
    database_port = 3309
    database_name = 'amazon_appstore'
    database_username = 'amazon_appstore'
    database_password = 'sP7sw8chuchu'

