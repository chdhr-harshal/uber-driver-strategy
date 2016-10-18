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

class uber:

    # Uber API constants
    
    apps = [
    {
        'name' : 'HC_test_app_1',
        'client_id' : 'IcxHByeHX6iVv_7yxbzqLVkQ8Qq-bwE-',
        'client_secret' : 'eITxIs1Q41LzXq1FYJqNLvAV97Xg85hFHfhA27TY',
        'server_token' : 'b07-fP6i4IaLW_DuG5LXjVNtMdtupHJ_2FL_LQmM'
    },
    {
        'name' : 'HC_test_app_2',
        'client_id' : 'ot0B2PJc60TIgI4--vnWfWcK4Jyo1ef_',
        'client_secret' : '45xkaNszvMi2m9ZSic9gMZxXAAdKQZzMd9kT_NlJ',
        'server_token' : 'Bz2bdWuD5QBE2XhI5VM5QNMuzyJXpb6XrMFRw4NZ'
    },
    {
        'name' : 'HC_test_app_3',
        'client_id' : 'Cmo3979xbaSgfPDBm1t3JO9l8h8dHB__',
        'client_secret' : 'SYsNDC4zgi9IXX1q2c0RRf_Bk1ig4iFSTpvsuZsx',
        'server_token' : 'CPNCJjx4Rp2bR5E1M1K7Yx_C6ffP7-Brts5OpSKv'
    },
    {
        'name' : 'HC_test_app_4',
        'client_id' : 'MwGtKIrJK0Alqbo4imcHaAUmtqTbdzn4',
        'client_secret' : 'GWwMty1_Dt8tZtBlY8ZzRBwxYBfMTmbvViJ39NJn',
        'server_token' : 'jk0gKBMQYvQTfztyhI29yC2D8slgfqOPzw6ULq9X'
    },
    {
        'name' : 'HC_test_app_5',
        'client_id' : 'uJ0UpU4kuvp4E-4SWzXBy69H912qs3sA',
        'client_secret' : 'KehDOKxJR5h12Dvc19lSfINVc97T9TXQ942bqoSm',
        'server_token' : 'mHnEYjFBnQGL_TWJHrPcFJihrjI8U_0ybNkQuyLS'
    },
    {
        'name' : 'Marin_test_app_1',
        'client_id' : 'USBGrRmQJPaXpH3U6h23V3kzHXiPnB50',
        'client_secret' : 'QezjXpIkHMZAtWUjvEIfPLH1fY8TzelUTA9Ae4oL',
        'server_token' : '7HJFwwDuc-V8-FBCFe_jB4VwGZm_Rt_B4jwUVR59'
    },
    {
        'name' : 'Marin_test_app_2',
        'client_id' : 'qeoums6vj7sqM5e0KoXvsWw6TVEBtsDL',
        'client_secret' : 'FNPYffUbFgKUP4tRvsXDKzMgnTbEUOeTynDE8Dvp',
        'server_token' : 'AKrWTrPJhXDJciNb1FN818GK469p5Digxeh6PI7m'
    },
    {
        'name' : 'Marin_test_app_3',
        'client_id' : 'gkXsBPresGUPkatLSplQKX0FQjD3_eMX',
        'client_secret' : 'Ug5-FfUNMTB_aZFoS2xvPbAEsiQkw72vvU0kO3rw',
        'server_token' : 'Hbxc07HbsmicfCeLXHvvgQSdXzfcI3NobxYS03vS'
    },
    {
        'name' : 'Marin_test_app_4',
        'client_id' : 'cy2D1H9t_2qYviVO23F3WovHmPmboGt0',
        'client_secret' : 'qRupd9Mv78SqccvLYI3NdOOsDI0tvXTjjqM01AyW',
        'server_token' : 'KkMwx7s7NMSk4JnNDuRM5C0vqCDoGuS-zd2fU2EN'
    }
    ]

