import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from time import sleep
import telebot

TOKEN = '5178356349:AAE5mk8NT13nsChnvTMJ9NVSXUCsp8kRnTM'

bot = telebot.TeleBot(TOKEN)



CSV = 'prices.csv'
URLS = ['https://goldapple.ru/117072-3260800012-the-3in1-foundation',
        'https://goldapple.ru/91104-lotion-tonique-reveil',
        'https://goldapple.ru/19760311151-dry-hair-nourishing-shampoo',
        'https://goldapple.ru/19760311149-dry-hair-nourishing-conditioner',
        'https://goldapple.ru/10016-7001900003-healthy-mix-serum',
        'https://goldapple.ru/65970100004-hydrating-cream',
        'https://goldapple.ru/3205400004-cabaret',
        'https://goldapple.ru/19000034449-marilyn',
        'https://goldapple.ru/30150400002-cleansing-gel',
        'https://goldapple.ru/15780600003-hy-ol',
        'https://goldapple.ru/19000004951-the-scalp-exfoliator-and-massager-pretty-pink',
        ]

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'
}

FLAG = 0
ITEMS = ()
last_chat_id = ''



def get_html(url, params=''):
    print('\nTrying connect to site...')
    html = requests.get(url, headers=HEADERS, params=params)
    print(f'{"Site status... OK" if html.status_code==200 else "Connection Error"}')
    return html

def get_content(html) -> tuple:
    '''
    parsing soup object and returns dict 
    {'name': str,
    'price': int, 
    'month': str,
    'day': int, 
    'year': int, 
    'current_time': XX:XX}
    '''
    
    print(f'Parsing elements...')
    soup = BeautifulSoup(html, 'html.parser')
    item = soup.find('div', class_='pdp__form-inner-wrapper')
    price = item.find('div', class_='price-box price-final_price').find('span', class_='price').text.replace(u'\xa0', '').replace('₽', '').strip()
    name = item.find('a', class_='link-alt pdp-title__brand').text.strip() +', '+ item.find('span', class_='pdp-title__name').text.strip()
    now = datetime.now()
    current_time = str(now.strftime("%b %d %Y %H:%M")).split()
    info = ({'name':name, 'price':int(price), 'month':current_time[0], 'day':int(current_time[1]), 'year':int(current_time[2]), 'current_time':current_time[3]})
    print(f'Done.')
    return info


def check_csv(path):
    '''
    Creating file with heder row 'Товар', 'Цена', 'Месяц',' День','Год','Время' , or skip
    change FLAG to 1 if create
    '''
    global FLAG
    try:
        with open(path, 'r') as file:    
            reader = tuple(csv.reader(file, delimiter=';'))
            text = ['Товар', 'Цена', 'Месяц',' День','Год','Время']
            if reader[0] == text: FLAG = 1

    except:
        print('except checker')
        pass
        
def create_csv(path):
    if not FLAG:
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Товар', 'Цена', 'Месяц',' День','Год','Время'])
            print('File prices.csv created')
    else:
        pass


  
def save_csv(items, path):
    check_csv(path)
    create_csv(path)
    try:
        with open(path, 'a', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            for item in items:
                writer.writerow([item['name'], item['price'], item['month'], item['day'], item['year'], item['current_time']])
    except PermissionError:
        print('Не могу записать файл, возможно он уже открыт')
    print('Job was finished')
              

def parse(ITEMS, CSV):
    st = 1
    for url in URLS:
        print(f'\tТовар {st}/{len(URLS)} ')
        html = get_html(url)
        info = get_content(html.text)
        new_thing = (info['name'],info['price'])
        try:
            _, finded_info = find(new_thing[0] ,type_='Товар')
            last_price = int(finded_info[-1][1])
        except (FileNotFoundError, IndexError):
            last_price = None
        if new_thing[1] != last_price:
            ITEMS += (info),
            st += 1
            try:
                bot.send_message(last_chat_id, f"💵 Новый прайс 💵 \n Товар: {new_thing[0]} \n~{last_price}~₽\n{new_thing[1]}₽", parse_mode='MarkdownV2')
            except:
                pass
        else:
            print('Цена не изменилась\n')
            st += 1
            pass

    save_csv(ITEMS, CSV)


def read_database(path):
    with open(path, 'r') as file:    
        reader = list(csv.reader(file, delimiter=';'))    
        reader.pop(0)
        for nam, pr, mo, day, year, time  in reader:
            print(f'{nam=}, {pr=}, {mo=}, {day=}, {year=}, {time=} ')
            
def find(name: str|int , type_ = 'Товар', csv_=CSV) -> tuple:
    '''
    name: name of search, 
    type_= 'Товар'|'Цена'|'Месяц'|'День'|'Год'|'Время',
    csv_= filename
    
    returns header = ['Товар', 'Цена', 'Месяц',' День','Год','Время']
    returns finded = tuple((search obj),(search obj))
    '''
    with open(csv_, 'r') as file:
        reader = list(csv.reader(file, delimiter=';'))
        header = reader.pop(0)
        finded = []
        _type=''
        
        match type_:
            case 'Товар': _type = 0
            case 'Цена': _type = 1
            case 'Месяц': _type = 2
            case' День': _type = 3
            case'Год': _type = 4
            case'Время': _type = 5
            
        for line in reader:
            if line[_type]==name:
                finded.append(tuple(line))
        return header, finded

# BOT WRAPPER
@bot.message_handler(commands=['start'])
def start_message(message):
    global last_chat_id
    bot.send_message(message.chat.id, "Привет, оповещу тебя о смене цены на товары из 🍎")
    last_chat_id = message.from_user.id
    while True:    
        parse(ITEMS, CSV)
        sleep(60)

bot.infinity_polling()



# parse(ITEMS,CSV)
# read_database(CSV)
# header, finded = find('1980', type_='Цена')
