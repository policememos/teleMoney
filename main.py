import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
from time import sleep
import telebot
import sql_api as db

TOKEN = '5178356349:AAE5mk8NT13nsChnvTMJ9NVSXUCsp8kRnTM'

bot = telebot.TeleBot(TOKEN, parse_mode='MarkdownV2')


Uzver = ''
CSV = 'prices.csv'
URLS = ['https://goldapple.ru/19760311280-the-wet-detangler-mini-pink-sherbet',
        'https://goldapple.ru/11663-35161700002-menthol',
        "https://goldapple.ru/65970100004-hydrating-cream"
        ]

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0'
}

FLAG = 0
ITEMS = ()
last_chat_id = ''
connection_time = ''
diff_in_milliseconds = ''


def get_html(url, params=''):
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
    parsing soup object and returns dict 
    {'articule':    str,
    'name':         str,
    'price':        int, 
    'special_price':int,
    'month':        str,
    'day':          int, 
    'year':         int, 
    'current_time': XX:XX}
    '''
    global diff_in_milliseconds
    now1 = datetime.now()
    current_time1 = str(now1.strftime("%b %d %Y %H:%M:%S"))
    print(f'{current_time1} Parsing elements...')
    soup = BeautifulSoup(html, 'html.parser')
    item = soup.find('div', class_='pdp__form-inner-wrapper')
    articule = item.find('p', class_="paragraph-2 pdp-form__sku").find('span', attrs={'itemprop': 'sku'}).text
    paran = ["old-price", "best-loyalty-price"]
    item_price = soup.find('div', class_='price-box price-final_price')
    special_price = item_price.find('span', class_=paran[1]).find('span', attrs={'data-price-type': 'bestLoyaltyPrice'}).text.replace(u'\xa0', '').replace('₽', '').strip()
    price = item_price.find('span', class_='price').text.replace(u'\xa0', '').replace('₽', '').strip()
    name = item.find('a', class_='link-alt pdp-title__brand').text.strip() + ', ' + item.find('span', class_='pdp-title__name').text.strip()
    now2 = datetime.now()
    current_time2 = str(now2.strftime("%b %d %Y %H:%M")).split()
    info = ({'articule': articule, 'name': name, 'price': int(price), 'special_price': int(special_price),'month': current_time2[0], 'day': int(current_time2[1]), 'year': int(current_time2[2]), 'current_time': current_time2[3]})
    now3 = datetime.now()
    current_time3 = str(now3.strftime("%b %d %Y %H:%M:%S"))
    connection_time = now3 - now1
    diff_in_milliseconds = connection_time.total_seconds() * 1000
    print(f'{current_time3} Done.')
    print(f'                     Parsing time {round(diff_in_milliseconds)}ms')
    return info


def check_csv(path):
    '''
    Creating file with heder row 'Articule', 'Good', 'Price', 'Special_price', 'Month',' Day','Year','Time' , or skip
    change FLAG to 1 if create
    '''
    global FLAG
    try:
        with open(path, 'r') as file:
            reader = tuple(csv.reader(file, delimiter=';'))
            text = ['Articule', 'Good', 'Price',
                    'Special_price', 'Month', ' Day', 'Year', 'Time']
            if reader[0] == text:
                FLAG = 1

    except:
        pass


def create_csv(path):
    if not FLAG:
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Articule', 'Good', 'Price',
                            'Special_price', 'Month', ' Day', 'Year', 'Time'])
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
                writer.writerow([item['articule'], item['name'], item['price'], item['special_price'],
                                item['month'], item['day'], item['year'], item['current_time']])
    except PermissionError:
        print('Can\'t write file, perhaps it\'s opened?')
    print(f'Job was finished\n' if not updated_price else f'-> Updated: {updated_price} goods price')


def alert_to_user(oldprice, newprice, item):
    print(f'ALERT {oldprice=}, {newprice=}, {item}')
    if newprice < oldprice:
        try:
            print(f'ALERT try')
            bot.send_message(last_chat_id, f"💵 Новый прайс 💵 \nТовар: *{item[1]}* \n~{oldprice}~ ₽    {newprice} ₽")
        except:
            print(f'ALERT fall')
            pass


def parse(ITEMS, CSV):
    goods_amount = len(URLS)
    goods_amount_counter = 1
    global updated_price
    updated_price = 0
    if not goods_amount:  # если нет товаров - сообщение юзеру
        bot.send_message(
            last_chat_id, f'У тебя пока нет отслеживаемых товаров, отправь мне ссылку на товар с сайта Золотое Яблоко')
    else:
        for url in URLS:
            print(f'\tGood {goods_amount_counter}/{len(URLS)}')
            html = get_html(url)
            if not html:
                continue  # ! добавь месседж юзеру что товар непрочекан
            # ({'articule':articule,'name':name, 'price':int(price),'special_price':int(special_price), 'month':current_time[0], 'day':int(current_time[1]), 'year':int(current_time[2]), 'current_time':current_time[3]})
            info = get_content(html.text)
            new_thing = (info['articule'], info['name'],
                         info['price'], info['special_price'])

            try:
                # find('name', type_='?') -> returns header = ['Articule', 'Good', 'Price', 'Special_price', 'Month',' Day','Year','Time']
                _, finded_info = find(new_thing[0], type_='Articule')
                #                             returns finded = tuple((search obj),(search obj))
                last_price, last_spesial_price = int(
                    finded_info[-1][2]), int(finded_info[-1][3])
            except (FileNotFoundError, IndexError):
                last_price, last_spesial_price = 9999999, 9999999

            best_price, best_sp_pr = new_thing[2], new_thing[3]
            try:
                new_thebest = best_price if best_price < best_sp_pr else best_sp_pr
                old_thebest = last_price if last_price < last_spesial_price else last_spesial_price

            except:
                pass
            match new_thing:
                case [art, nam, pr, sp_pr] if pr != last_price:
                    ITEMS += (info),
                    goods_amount_counter += 1
                    updated_price += 1
                    print(
                        f'💵 Price Новый прайс 💵 \nТовар: *{nam}* \n~{last_price}~ ₽,{last_spesial_price}    {pr=}, {sp_pr=} ₽\n\n')
                    if old_thebest:
                        alert_to_user(old_thebest, new_thebest, new_thing)

                case [art, nam, pr, sp_pr] if sp_pr != last_spesial_price:
                    ITEMS += (info),
                    goods_amount_counter += 1
                    updated_price += 1
                    print(
                        f'💵 Special_price Новый прайс 💵 \nТовар: *{nam}* \n~{last_price}~ ₽,{last_spesial_price}~ ₽    {sp_pr=}, {sp_pr=} ₽\n\n')
                    if old_thebest:
                        alert_to_user(old_thebest, new_thebest, new_thing)
                    else:
                        print(f'alert_to_user not called! {old_thebest=} ')

                case _:
                    print('Same price\n')
                    goods_amount_counter += 1
                    pass

    save_csv(ITEMS, CSV)


def read_database(path):
    with open(path, 'r') as file:
        reader = list(csv.reader(file, delimiter=';'))
        reader.pop(0)
        print(f'>>>Reading database')
        for art, good, pr, sp_pr, mo, day, year, time in reader:
            yield art, good, pr, sp_pr, mo, day, year, time


def find(name: str | int, type_='Articule', csv_=CSV) -> tuple:
    '''
    name: name of search, 
    type_= 'Articule'|'Good'|'Price'|'Special_price'|'Month'|'Day'|'Year'|'Time',
    csv_= filename

    returns header = ['Articule', 'Good', 'Price', 'Special_price', 'Month',' Day','Year','Time']
    returns finded = tuple((search obj),(search obj))
    '''
    with open(csv_, 'r') as file:
        reader = list(csv.reader(file, delimiter=';'))
        header = reader.pop(0)
        finded = []
        _type = ''

        match type_:
            case 'Articule': _type = 0
            case 'Good': _type = 1
            case 'Price': _type = 2
            case 'Special_price': _type = 3
            case 'Month': _type = 4
            case' Day': _type = 5
            case'Year': _type = 6
            case'Time': _type = 7

        for line in reader:
            if line[_type] == name:
                finded.append(tuple(line))
        return header, finded

    
# BOT WRAPPER
@bot.message_handler(commands=['start', 'help', 'h'])
def start_message(message):
    global last_chat_id
    bot.send_message(
        message.chat.id, "Привет, оповещу тебя о смене цены на товары из 🍎\nСписок товаров: mylist")
    last_chat_id = message.from_user.id
    while True:
        parse(ITEMS, CSV)
        sleep(30)
    

@bot.message_handler(regexp='MyList')
def command_help(message):
    items = read_database(CSV)
    for art, good, pr, sp_pr, mo, day, year, time in items:
        bot.send_message(message.chat.id, f'Артикул: {art}\nНаименование: {good}\nЦена: {pr}\nСпец\.цена: {sp_pr}\nДата добавления: {year} {mo} {day} {time}')
    



if __name__ == '__main__':
    bot.infinity_polling()
    
# parse(ITEMS,CSV)
# read_database(CSV)
# header, finded = find('1980', type_='Price')