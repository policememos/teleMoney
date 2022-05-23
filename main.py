import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from progress.bar import FillingCirclesBar
from progress.spinner import Spinner




CSV = 'prices.csv'
URLS = ['https://goldapple.ru/19000014167-hair-oil', 'https://goldapple.ru/41100300002-pink-breeze','https://goldapple.ru/19000025384-salt-scalp-scrub',
        'https://goldapple.ru/19000001800-soapy-flower-fine-fragrance-hair-body-mist','https://goldapple.ru/99494000003-biotin-damage-care-oil',
        'https://goldapple.ru/19000049656-tricho-expert','https://goldapple.ru/41100300001-stockholm-rose','https://goldapple.ru/19000022739-leave-in-molecular-repair-hair-mask',
        'https://goldapple.ru/19760300021-scalp-scaling-spa'
        ]
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'
}






def get_html(url, params=''):
    html = requests.get(url, headers=HEADERS, params=params)
    print(f'{"Site connected... OK" if html.status_code==200 else "Connection Error"}')
    return html

def get_content(html):
    
    print(f'Parsing elements...')
    soup = BeautifulSoup(html, 'html.parser')
    spinner.next()
    item = soup.find('div', class_='pdp__form-inner-wrapper')
    spinner.next()
    price = item.find('div', class_='price-box price-final_price').find('span', class_='price').text.replace(u'\xa0', '').replace('₽', '').strip()
    spinner.next()
    name = item.find('a', class_='link-alt pdp-title__brand').text.strip() +','+ item.find('span', class_='pdp-title__name').text.strip()
    spinner.next()
    now = datetime.now()
    spinner.next()
    current_time = now.strftime("%b %d %Y")
    spinner.next()
    info = ({'name':name, 'price':price, 'current_time':current_time})
        
    
    
    return info
  
  
def save_csv(items, path):
    
    with open(path, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        spinner.next()
        writer.writerow(['Товар','Цена','Дата'])
        spinner.next()
        
        for item in items:
            spinner.next()
            writer.writerow([item['name'], item['price'], item['current_time']])
              
  
            


ITEMS = ()


bar = FillingCirclesBar('Parsing data...', max=len(URLS))
spinner = Spinner('Loading ')
state = 'run'
while state != 'FINISHED':
    spinner.next()
    for url in URLS:
        spinner.next()
        html = get_html(url)
        spinner.next()
        info = get_content(html.text)
        spinner.next()
        ITEMS += (info),
    state = 'FINISHED'

save_csv(ITEMS, CSV)

    


