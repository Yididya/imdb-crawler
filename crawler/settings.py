
'''
Database configuration, Multiprocessing pool size and other settings.
'''

DATABASE = {
    'NAME': 'MovieDB',
    'USER': 'root',
    'PASSWORD': '0000',
    'HOST': 'localhost',
    'PORT': '3306',
}

ROOT_URL =  'http://www.imdb.com'
URL_TOP_250 = 'http://www.imdb.com/chart/top'
URL_BOTTOM_100 = 'http://www.imdb.com/chart/bottom'


NUMBER_OF_THREADS = 6