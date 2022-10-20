import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from time import sleep
import telebot
import sql_api as db
from lxml import etree
import os

TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot(TOKEN, parse_mode='MarkdownV2')

Uzver = ''
CSV = 'prices.csv'
URLS = ['https://goldapple.ru/19760311280-the-wet-detangler-mini-pink-sherbet', # Список ссылок на товары
        'https://goldapple.ru/11663-35161700002-menthol',
        'https://goldapple.ru/65970100004-hydrating-cream'
        ]

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'
}

last_chat_id = ''
connection_time = ''
diff_in_milliseconds = ''


def get_html(url, params=''):
    '''
    Получаем страницу, замеряем время на получение ответа от сервера
    Если ответ отличный от 200 пишем в консоль об ошибке
    Если запрос успешен пишем "time ping" ответа
    '''
    global connection_time
    global diff_in_milliseconds
    now1 = datetime.now()
    current_time1 = str(now1.strftime("%b %d %Y %H:%M:%S"))
    print(f'\n{current_time1} Trying connect to site...')
    html = requests.get(url, headers=HEADERS, params=params)
    now2 = datetime.now()
    current_time2 = str(now2.strftime("%b %d %Y %H:%M:%S"))
    connection_time = now2 - now1
    diff_in_milliseconds = connection_time.total_seconds() * 1000
    if html.status_code == 200:
        print(f"{current_time2} Site status... OK")
    else:
        print(f">>> {current_time2} CONNECTION ERROR")
        return False
    print(f'                     Connection ping {round(diff_in_milliseconds)}ms')
    return html


def get_content(html) -> tuple:
    '''
    Парсим soup обьект, возвращает dict 
    {'articule':    int,
    'name':         str,
    'price':        int, 
    'special_price':str,
    'month':        str,
    'day':          int, 
    'year':         int, 
    'current_time': XX:XX}
    '''
    global diff_in_milliseconds
    now1 = datetime.now()
    current_time1 = str(now1.strftime("%b %d %Y %H:%M:%S"))
    print(f'{current_time1} Parsing elements...')
    soup = BeautifulSoup(html, 'lxml')
    dom = etree.HTML(str(soup))
    articule = dom.xpath('/html/body/div[1]/main/div/div/section/section[1]/section[3]/div/form/p[1]/span[2]')[0].text
    price = dom.xpath('/html/body/div[1]/main/div/div/section/section[1]/section[3]/div/form/div[3]/div/div/span[1]/span/span/span')[0].text.replace(u'\xa0', '').replace('₽', '').strip()
    name = ', '.join((dom.xpath('/html/body/div[1]/main/div/div/section/section[1]/section[3]/div/header/h1/a')[0].text.strip(), dom.xpath('/html/body/div[1]/main/div/div/section/section[1]/section[3]/div/header/h1/span')[0].text.strip()))
    try:
        special_price = int(dom.xpath('/html/body/div[1]/main/div/div/section/section[1]/section[3]/div/form/div[3]/div/span/span/span/span')[0].text.replace(u'\xa0', '').replace('₽', '').strip())
        if special_price == 0:
            special_price = None
    except:
        special_price = None
    
    now2 = datetime.now()
    current_time2 = str(now2.strftime("%b %d %Y %H:%M")).split()
    info = ({'articule': int(articule), 'name': name, 'price': int(price), 'special_price': special_price, 'month': current_time2[0], 'day': int(current_time2[1]), 'year': int(current_time2[2]), 'current_time': current_time2[3]})
    now3 = datetime.now()
    current_time3 = str(now3.strftime("%b %d %Y %H:%M:%S"))
    connection_time = now3 - now1
    diff_in_milliseconds = connection_time.total_seconds() * 1000
    print(f'{current_time3} Done.')
    print(f'                     Parsing time {round(diff_in_milliseconds)}ms')
    return info

    
def save_info_db(item):
    result = db.insert_data(item)
    match result:
        case None:
            print('write to db error\n\n')
        case True:
            print(f'new info was added in db\n\n')


def alert_to_user(oldprice, newprice, item):
    try:
        print(f'Alert to user sended')
        bot.send_message(last_chat_id, f"💵 Новый прайс 💵 \nТовар: *{item[1]}* \n~{oldprice}~ ₽    {newprice} ₽")
    except:
        print(f'Alert to user filed')
        pass


def parse():
    goods_amount = len(URLS)
    goods_amount_counter = 1
    global updated_price
    updated_price = 0
    if not goods_amount:  # если нет товаров - сообщение юзеру
        bot.send_message(
            last_chat_id, f'У тебя пока нет отслеживаемых товаров, отправь мне ссылку на товар с сайта Золотое Яблоко')
    else:
        for url in URLS:
            print(f'\t\tGood {goods_amount_counter}/{len(URLS)}')
            html = get_html(url)
            if not html:
                continue  # ! добавь месседж юзеру что товар непрочекан
            # ({'articule':articule,'name':name, 'price':int(price),'special_price':int(special_price), 'month':current_time[0], 'day':int(current_time[1]), 'year':int(current_time[2]), 'current_time':current_time[3]})
            info = get_content(html.text)
            new_thing = (info['articule'], info['name'], info['price'], info['special_price'])
            try:
                # find('name', type_='?') -> returns header = ['Articule', 'Good', 'Price', 'Special_price', 'Month',' Day','Year','Time']
                finded_last_info = db.find_data(new_thing[0])[-1]
                best_price, best_sp_pr = new_thing[2], new_thing[3]
                last_price, last_spesial_price = finded_last_info[2], finded_last_info[3]
                new_thebest = best_price if best_sp_pr is None or best_price < best_sp_pr else best_sp_pr
                old_thebest = last_price if last_spesial_price is None or last_price < last_spesial_price else last_spesial_price
                      
                if new_thebest < old_thebest:
                    # items += (info),
                    goods_amount_counter += 1
                    updated_price += 1
                    print(f'\n💵 Новый прайс 💵 \nТовар: *{new_thing[1]}* \n~{last_price}~ ₽,{last_spesial_price}    {best_price=}, {best_sp_pr=} ₽\n\n')
                    save_info_db(tuple(info.values())) 
                    alert_to_user(old_thebest, new_thebest, new_thing)
                elif new_thebest > old_thebest:
                    # items += (info),
                    goods_amount_counter += 1
                    updated_price += 1
                    print(f'💵 Новый прайс 💵 \nТовар: *{new_thing[1]}* \n~{last_price}~ ₽,{last_spesial_price}    {best_price=}, {best_sp_pr=} ₽\n\n')
                    save_info_db(tuple(info.values())) 
                else:    
                    print('Same price')
                    goods_amount_counter += 1
            except:
                print('Try to find old price FAILED, skip this step')
                goods_amount_counter += 1
                save_info_db(tuple(info.values()))

    
# BOT WRAPPER
@bot.message_handler(commands=['start', 'help', 'h'])
def start_message(message):
    global last_chat_id
    bot.send_message(
        message.chat.id, "🤖: Привет, оповещу тебя о\nсмене цены на товары из 🍎\nЦены обновляю каждые 3 часа")
    last_chat_id = message.from_user.id
    db.create_db()
    while True:
        parse()
        sleep(30)
    
@bot.message_handler(commands=['mylist'])
def mylist_db(message):
    items = db.read_db()
    for art, good, pr, sp_pr, mo, day, year, time in items:
        bot.send_message(message.chat.id, f'Артикул: {art}\nНаименование: {good}\nЦена: {pr}\nСпец\.цена: {sp_pr}\nДата добавления: {year} {mo} {day} {time}')
    
if __name__ == '__main__':
    print('_____________________________________________________\n_______________ Bot status: Online __________________\n\n')
    bot.infinity_polling()
    print('\n\n_____________________________________________________\n_______________ Bot status: offline _________________')
