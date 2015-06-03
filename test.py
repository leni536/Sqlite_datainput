#! /usr/bin/python3
if __name__ == '__main__':
    import sqlite3 as db
    import sqlite_completer as sqc
    conn=db.connect(':memory:')
    conn.execute('CREATE TABLE test (test_id INTEGER PRIMARY KEY, name TEXT)')
    conn.execute('''INSERT INTO test (name) VALUES 
    ("jozsi"),
    ("pisti")
            ''')
    print(conn.execute('SELECT * FROM test').fetchall())
    myinput=sqc.sqlite_input()
    it=sqc.sqlite_input.input_type
    myinput.add_input(it(conn,table='test',source=['name'],target='test_id'))
    sqc.logger.setLevel(sqc.logging.DEBUG)
