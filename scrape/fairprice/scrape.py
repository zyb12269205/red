__author__ = 'zhanyingbo'


import urllib2
import time

from util.file_ops import *
from lxml import etree

FAIRPRICE_DATA_DIR = '../../data/fairprice/'
CATEGORIES_URL = 'http://www.fairprice.com.sg/webapp/wcs/stores/servlet/en/fairprice'
CATEGORIES_FILE  = FAIRPRICE_DATA_DIR+'categories.json'
WAIT_TIME = 3



def query_save_result(url, file_path, process):
    if file_exist(file_path):
        return read_file(file_path)
    response = urllib2.urlopen(url).read()
    time.sleep(WAIT_TIME)
    result = process(response)
    save_file(result, file_path )
    return result

def process_category(response):
    result = {}
    for line in response.split('\r\n'):
        if 'TopCategoryLink_' in line:
            if 'href' in line and 'alt' in line:
                start_href = line.find('href="')
                start_alt = line.find('alt=')
                if 'alt="' in line: continue
                alt = line[start_alt+5: line.find("'", start_alt+5)]
                href = line[start_href+6: line.find('"', start_href+6)]
                result[alt] = href
    return result

            

def get_categories():
    return query_save_result(CATEGORIES_URL, CATEGORIES_FILE, process_category)


def get_product(response, cat):
    products = []
    tree = etree.HTML(response)
    for node in tree.xpath('.//div[@class="pr_nlst_wrp"]'):
        try:
            prod = {
                'name': node.xpath('.//h3/text()')[0].replace('\n','').replace('\t',''),
                'desc': node.xpath('.//h3/text()')[0].replace('\n','').replace('\t',''),
                'measure': '',
                'price': node.xpath('.//span[@class="pl_lst_rt"]/text()')[0],
                'category': cat,

            }
            products.append(prod)

        except:
            pass

    #print products
    return products




def query_result(cat, url):
    products = []
    index = 0
    while True:
        print url
        response = urllib2.urlopen(url).read()
        time.sleep(WAIT_TIME)
        new_products = get_product(response, cat)

        if len(new_products)==0: break

        products += (new_products)
        existing_beginIndex = 'beginIndex='+str(index)
        index += 24
        replaced_beginIndex = 'beginIndex='+str(index)
        url = url.replace(existing_beginIndex,replaced_beginIndex)

    save_file(products,FAIRPRICE_DATA_DIR+cat+'.json')

def scrape():
    cate = get_categories()
    for key in cate.keys():
        query_result(key, cate[key])


def product():
    cate = get_categories()
    products = []
    for key in cate.keys():
        file_path = FAIRPRICE_DATA_DIR+key+'.json'
        list_product = read_file(file_path)
        for prod in list_product:
            products.append(
                {
                    'price': prod.get('price').replace('\r\n','').replace('\t','').replace('$',''),
                    'name': prod.get('name').lower(),
                    'desc': prod.get('desc').lower(),
                    'measure': prod.get('measure'),
                    'category': key,
                }
            )
    save_file(products,FAIRPRICE_DATA_DIR+'products.json')



#scrape()
product()

