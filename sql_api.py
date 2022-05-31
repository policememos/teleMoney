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
                        "Time"	TEXTpip list
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
            cursor.execute(f'INSERT INTO prices_db VALUES ({item})')
    except Exception as err:
        print(f'Error occured:{err.__class__}, {err}')
        return None        
     
        
def find_data(name: str | int, type_='Articule') -> tuple:
    try:
        with sqlite3.connect(_DBNAME) as db:
            cursor = db.cursor()
            finded = cursor.execute(f'SELECT * FROM prices_db WHERE {type_}=={name}')
    except Exception as err:
        print(f'Error occured:{err.__class__}, {err}')
        return None        
    
