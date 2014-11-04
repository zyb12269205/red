__author__ = 'zhanyingbo'

from util.file_ops import *

CONTENT_MATCH_RATIO = 0.5
PRICE_MATCH_RATIO = 2

PARTERS = [
    'fairprice',
]

def get_products_partner(partner):
    def filter(products):
        results = []
        for product in products:
            content = product.get('name', '')
            content += ' '
            try:
                for value in json.loads(product.get('measure',{})).values():
                    content +=   str(value.replace(' ',''))
            except:
                try:
                    for value in product.get('measure',{}).values():
                        content +=  str(value.replace(' ',''))
                except:
                    pass
            content += ' '
            results.append({
                'content': content,
                'price': product['price']
            })
        print results
        return results

    products = read_file('../data/'+partner+'/products.json')
    return filter(products)


def init_master(trust):
    products_master = []
    for product in get_products_partner(trust):
        products_master.append(
            {
                'content': product['content'],
                'price': product['price'],
                'price_list':{
                    trust: float(product['price']),
                },
                'content_list':{
                     trust: product['content'],
                }
            }
        )
    return products_master

def best_match(sample, matched_list, partner):
    best_ratio = 0
    best_content = ''
    best_price = 0.0
    best_prod = None
    for prod in matched_list:
        [check, final_content, final_price] = compare(sample, prod)
        if check > best_ratio:
            best_prod = prod
            best_ratio = check
            best_price = final_price
            best_content = final_content

    if best_prod is None: return False
    best_prod['content'] = best_content
    best_prod['price'] = best_price
    best_prod['price_list'][partner] = float(sample['price'])
    best_prod['content_list'][partner] = sample['content']
    print 'match : '+ best_content
    return True


def match():
    trust = 'redmart'
    products_master = init_master(trust)
    add_into_product_masters = []
    for partner in PARTERS:
        total_products = get_products_partner(partner)
        for prod1 in total_products:
            if not best_match(prod1, products_master, partner):
                add_into_product_masters.append(
                    {
                        'content': prod1['content'],
                        'price': float(prod1['price']),
                        'price_list':{
                            partner: float(prod1['price']),
                        },
                        'content_list':{
                             partner: prod1['content'],
                        }
                    }
                )
        print partner + ' has total ' + str(len(total_products)) + ' with unmatched of ' + str(len(add_into_product_masters))

    save_file(products_master, '../data/master.json', True)





def compare(prod1, prod2):
    def join(list_strings):
        output = ''
        for x in list_strings:
            output += ' ' + x
        return output

    prod1_name = set(prod1['content'].split(' '))
    prod2_name = set(prod2['content'].split(' '))
    prod1_name.remove('')
    prod2_name.remove('')
    total = len(prod1_name.union(prod2_name))
    match_total = len(prod1_name.intersection(prod2_name))
    match_ratio = match_total*1.0/total
    #print 'matching ratio is ' + str(match_total*1.0/total)
    prod1_price = float(prod1['price'])
    prod2_price = float(prod2['price'])
    if prod1_price*prod2_price == 0: return (0, prod1['content'], prod1['price'])
    ratio = prod1_price/prod2_price if prod1_price > prod2_price else prod2_price/prod1_price
    if ratio > PRICE_MATCH_RATIO or match_ratio < CONTENT_MATCH_RATIO:
        return (0, prod1['content'], prod1['price'])
    else:
        return (match_ratio,  prod1['content'] + ' ' + prod2['content'], (prod1_price+prod2_price)/2)



match()