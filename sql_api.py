import sqlite3

_DBNAME = 'pricedb.db'

def create_db():
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


def read_db():
    with sqlite3.connect(_DBNAME) as db:
        cursor = db.cursor()
        items = cursor.execute('SELECT rowid,* FROM prices_db')
        return items


def insert_data(item):
    with sqlite3.connect(_DBNAME) as db:
        cursor = db.cursor()
        cursor.execute(f'INSERT INTO prices_db VALUES ({item})')
        
        
def find_data(name: str | int, type_='Articule') -> tuple:
    with sqlite3.connect(_DBNAME) as db:
        cursor = db.cursor()
        finded = cursor.execute(f'SELECT * FROM prices_db WHERE {type_}=={name}')
        