# Sqlite_completer module
import readline as rl
import rlstack as rls
import sqlite3 as db
import logging

logger=logging.Logger('sql_completer')
### Helper functions

### shameless StackOverflow paste for safe (?) sqlite identifier sanitizing
# http://stackoverflow.com/questions/6514274/how-do-you-escape-strings-for-sqlite-table-column-names-in-python#answer-6701665
def quote_identifier(s, errors="strict"):
    encodable = s.encode("utf-8", errors).decode("utf-8")

    nul_index = encodable.find("\x00")

    if nul_index >= 0:
        error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                                   nul_index, nul_index + 1, "NUL not allowed")
        error_handler = codecs.lookup_error(errors)
        replacement, _ = error_handler(error)
        encodable = encodable.replace("\x00", replacement)

    return "\"" + encodable.replace("\"", "\"\"") + "\""
### /StackOverflow

### method definitions

# sqlite_input
def _sqlite_input__add_input(self,inputarg):
    self.inputseq.append(inputarg)

def _sqlite_input__input(self):
    ret=[]
    for i in self.inputseq:
        ret.append(i.input())
    return ret

# input_type
def _input_type__input(self):
    if self.typ=='new' :
        sqlite_input.rlstate.push()
        rl.set_completer(__null_completer)
        self.ret=input(self.name+': ')
        sqlite_input.rlstate.pop()
        return self.ret
    if self.typ=='identifier':
        sqlite_input.rlstate.push()
        rl.set_completer(self.completer)
        rl.set_completer_delims('')
        for source in self.source:
            ret=input(source+': ')
            self.push(ret)
        sql=('SELECT '+quote_identifier(self.target)+' , count() '
                ' FROM '+quote_identifier(self.table)+
                ' WHERE '+quote_identifier(self.source[-1])+' = ? ')
        logger.debug('sql: '+sql)
        self.cur.execute(sql,(self.fields[-1],))
        ret=self.cur.fetchone()
        sqlite_input.rlstate.pop()
        if ret[1]>1:
            raise LookupError('Couldn\'t get unique id from specified field')
        elif ret[1]==0:
            raise LookupError('Field does not exist')
        return ret[0]

def _input_type__push(self,value):
    if self.typ=='identifier':
        self.fields.append(value)
    else:
        raise ValueError('push only supported for identifiers')

def _input_type__completer(self,text,state):
    #if len(text)<1 :
        #return None
    if state==0:
        #TODO build sql statement
        pos=len(self.fields)

        if pos==0 :
            where2=' 1 '
        else:
            where2=' AND '.join([ quote_identifier(x[0])+ ' = ' +quote_identifier(x[1])
                for x in zip(source[:pos],fields[:pos])
                ])

        where=(' WHERE ( CAST ( ' + quote_identifier(self.source[pos]) + ' AS TEXT) LIKE ? AND ' +
                where2 +' )')
        sql=('SELECT DISTINCT ' + quote_identifier(self.source[pos]) +
                ' FROM ' + quote_identifier(self.table) +
                where +
                ' ORDER BY ' + quote_identifier(self.source[pos]) )
        self.cur.execute(sql,('{}%'.format(text),))

        #/TODO
    ret=self.cur.fetchone()
    if ret is not None:
        return ret[0]
    else:
        return None

### class declaration
class sqlite_input:
    rlstate=rls.rlstack()
    class input_type:
        def __init__(self,
                     conn,
                     typ='identifier',
                     table=None,
                     source=None,
                     target=None,
                     name=None):
            if typ not in ['identifier','new']:
                raise ValueError('Incorrect type')
            self.typ    = typ
            self.conn   = conn
            self.cur    = conn.cursor()
            if self.typ=='identifier':
                self.table  = table
                self.source = source
                self.target = target
                self.fields = []
            elif self.typ=='new':
                self.name   = name
        input = __input
        push  = __push
        completer = __completer

    # methods
    def __init__(self):
        self.inputseq=[]
    add_input = __add_input
    input = __input
### /class

