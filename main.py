#!/usr/bin/python3
import optparse as op
import readline as rl
import sqlite3 as db
import logging
import sys
import codecs
import sqlite_completer as sc

#### shameless StackOverflow paste for safe (?) sqlite identifier sanitizing
## http://stackoverflow.com/questions/6514274/how-do-you-escape-strings-for-sqlite-table-column-names-in-python#answer-6701665
#def quote_identifier(s, errors="strict"):
#    encodable = s.encode("utf-8", errors).decode("utf-8")
#
#    nul_index = encodable.find("\x00")
#
#    if nul_index >= 0:
#        error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
#                                   nul_index, nul_index + 1, "NUL not allowed")
#        error_handler = codecs.lookup_error(errors)
#        replacement, _ = error_handler(error)
#        encodable = encodable.replace("\x00", replacement)
#
#    return "\"" + encodable.replace("\"", "\"\"") + "\""
#### /StackOverflow
#
#class completer:
#    def __init__(self,conn,table,colnum=0):
#        self.conn=conn
#        self.c=conn.cursor()
#
#        self.tab=table
#
#        self.colnum=colnum
#        self.cols=[x[1] for x in self.c.execute('PRAGMA table_info('+quote_identifier(options.table)+')').fetchall()]
#        self.col=self.cols[self.colnum]
#        self.fields=[]
#
#    def completer(self,text, state):
#        if len(text)<0 :
#            return None
#        if state==0 :
#            if self.colnum==0 :
#                where2=' 1 '
#            else:
#                # ! Not safe !
#                where2=' AND '.join(
#                    map(lambda x: x[0]+'='+x[1],zip(self.cols[:self.colnum],self.fields[:self.colnum])))
#
#            where=' WHERE ( CAST ('+quote_identifier(self.col)+' AS TEXT) LIKE ? AND ' + where2 + ')' 
#            sql=('SELECT DISTINCT '+quote_identifier(self.col)+ 
#                 ' FROM '+quote_identifier(self.tab)+
#                 where +
#                 ' ORDER BY '+quote_identifier(self.col) )
#            try:
#                self.c.execute(sql,('{}%'.format(text),))
#            except db.Error as e:
#                logging.error('sqlite: ',e[0])
#        ret=self.c.fetchone()
#        if ret is not None:
#            return str(ret[0])
#        else:
#            return None
#
#    def push( field ):
#        self.colnum+=1
#        self.fields.append(field)


#Option parsing

parser=op.OptionParser()
parser.add_option('-d','--database',
                    action='store',
                    type='string',
                    dest='database',
                    metavar='<db_fname>',
                    help='specify database'
                    )
parser.add_option('-t','--table',
                    action='store',
                    type='string',
                    dest='table',
                    metavar='<table>',
                    help='specify table or view inside database'
                    )

(options,args)=parser.parse_args()

if options.database is None:
    parser.error('You must specify a database file! (-d <db_fname>)')
if options.table is None:
    parser.error('You must specify a table or view inside the database! (-t <table>)')

# Try opening database

try:
    conn=db.connect(options.database)
except sqlite3.Error as e:
    logging.error('sqlite: ',e.args[0])
    sys.exit(1)

# Check if table exists

t=conn.execute('SELECT type FROM sqlite_master WHERE name=?',(options.table,)).fetchone()

if t is None:
    logging.error('Table or view does not exist')
    sys.exit(1)
elif t[0] not in ['table','view']:
    logging.error('<table> must specify a table or view')
    sys.exit(1)

# Collect columns
columns=conn.execute('PRAGMA table_info('+sc.quote_identifier(options.table)+')').fetchall()

rl.parse_and_bind('tab: complete')
rl.set_completer_delims('')

comp=sc.completer(conn,options.table)
rl.set_completer(comp.completer)

input('> ')
