__author__ = 'zhanyingbo'

import json
import zlib
import urllib2
import time

from util.file_ops import *

CATEGORIES_URL = 'https://api.redmart.com/v1.4.1/catalog/categories?extent=13'
REDMART_DATA_DIR = '../../data/redmart/'

headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip,deflate',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'api.redmart.com'
}
CATEGORIES_FILE  = REDMART_DATA_DIR+'categories.json'
DETAIL_CATEGORY = 'https://api.redmart.com/v1.4.1/products/bycategory/?uri=%s&page=null&pageSize=%s&instock=false&sort=null'
WAIT_TIME = 3


def query_save_result(url, file_path):
    if file_exist(file_path):
        return read_file(file_path)
    response = urllib2.urlopen(url)
    time.sleep(WAIT_TIME)
    result = json.loads(response.read())
    save_file(result, file_path )
    return result


def get_categories():
    return query_save_result(CATEGORIES_URL, CATEGORIES_FILE)

def scrape():
    categories = get_categories()

    ## TODO: code could be improved by using pool
    ##query_category_urls = []
    for ctg in categories.get('categories',[]):
        uri = ctg.get('uri','')
        count = ctg.get('count', 0)*2
        query_save_result(DETAIL_CATEGORY%(uri, count), REDMART_DATA_DIR+uri+'.json')

def product():
    categories = get_categories()
    products = []
    ## TODO: code could be improved by using pool
    ##query_category_urls = []
    for ctg in categories.get('categories',[]):
        uri = ctg.get('uri','')
        count = ctg.get('count', 0)*2
        content = query_save_result(DETAIL_CATEGORY%(uri, count), REDMART_DATA_DIR+uri+'.json')
        for prod in content.get('products',[]):
            products.append(
                {
                    'name': prod['title'].lower(),
                    'measure': json.dumps(prod['measure']),
                    'desc': prod['desc'].lower(),
                    'price': prod['pricing']['price'] if prod['pricing']['price'] < prod['pricing']['promo_price'] or prod['pricing']['promo_price'] < 0.001 else prod['pricing']['promo_price'],
                    'category': uri
                }
            )
    save_file(products, REDMART_DATA_DIR+'products.json', True)

        
product()

