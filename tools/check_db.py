import sqlite3
import sys

def main():
    db = 'db.sqlite3'
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        print('tables:', tables)
        cur.execute("SELECT sql FROM sqlite_master WHERE name='accounts_user';")
        row = cur.fetchone()
        print('accounts_user ddl:', row)
    except Exception as e:
        print('ERROR', e)
        sys.exit(1)
    finally:
        try:
            conn.close()
        except:
            pass

if __name__ == '__main__':
    main()
