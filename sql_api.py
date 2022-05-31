import sqlite3

_DBNAME = 'pricedb.db'

def create_db():
    try:
        with sqlite3.connect(_DBNAME) as db:
            cursor = db.cursor()
            cursor.execute('''
                        CREATE TABLE IF NOT EXISTS "Prices_db" (
                        "Articule"	INTEGER,
                        "Good"	TEXT,
                        "Price"	INTEGER,
                        "Special_price"	INTEGER,
                        "Month"	TEXT,
                        "Day"	NUMERIC,
                        "Year"	INTEGER,
                        "Time"	TEXT
                    )''')
    except Exception as err:
        print(f'Error occured:{err.__class__}, {err}')
        return None


def read_db():
    try:
        with sqlite3.connect(_DBNAME) as db:
            cursor = db.cursor()
            items = cursor.execute('SELECT * FROM prices_db')
            return items
    except Exception as err:
        print(f'Error occured:{err.__class__}, {err}')
        return None        


def insert_data(item):
    try:
        with sqlite3.connect(_DBNAME) as db:
            cursor = db.cursor()
            cursor.execute(f'INSERT INTO prices_db VALUES ({item[0]},"{item[1]}",{item[2]},{item[3]},"{item[4]}",{item[5]},{item[6]},"{item[7]}")')
            return True
    except Exception as err:
        print(f'Error occured:{err.__class__}, {err}')
        return None        
     
        
def find_data(name: int, type_='Articule') -> tuple:
    try:
        with sqlite3.connect(_DBNAME) as db:
            cursor = db.cursor()
            finded = tuple(cursor.execute(f'SELECT * FROM prices_db WHERE {type_}=={name}'))
            return finded
    except Exception as err:
        print(f'Error occured:{err.__class__}, {err}')
        return None        
    
