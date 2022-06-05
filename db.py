from os import environ
import sqlite3
from models import User
from models import Counter, CounterInfo
from typing import List

def init_db(db_name: str):
   CREATE_SQL = """
        drop table if exists user;
        drop table if exists counter;
        drop table if exists user_counter;
        drop table if exists counter_history;

        create table user
        (
            id TEXT PRIMARY KEY,
            name TEXT
        );

        create table counter
        (
            uuid TEXT PRIMARY KEY,
            factory TEXT,
            owner TEXT,
            contract TEXT
        );

        create table user_counter
        (
            user_id TEXT,
            counter_uuid TEXT,
            FOREIGN KEY(user_id) REFERENCES user(id),
            FOREIGN KEY(counter_uuid) REFERENCES counter(uuid),
            UNIQUE(user_id, counter_uuid)
        );

        create table counter_history
        (
            counter_uuid TEXT,
            period TEXT,
            value INT,
            FOREIGN KEY(counter_uuid) REFERENCES counter(uuid),
            UNIQUE(counter_uuid, period)
        );


   """ 
   with sqlite3.connect(db_name) as conn:
       curr = conn.cursor()
       curr.executescript(CREATE_SQL)
       conn.commit()
       curr.close() 

   

def add_user(user_id: str, user_name: str) -> User:
    with sqlite3.connect(str(environ.get('DB_NAME'))) as conn:
        curr = conn.cursor()
        curr.execute('select * from user where id = :user_id', (user_id,))
        row = curr.fetchone()
        if row:
            return User(id=row[0], name=row[1])
        else:
            before_tran = conn.total_changes
            curr.execute("insert into user values(?, ?)", (user_id, user_name,))    
            conn.commit()
            after_tran  = conn.total_changes
            if after_tran > before_tran:
                return User(user_id, user_name)
            else:
                return None    

def delete_user(user_id: str) -> User:
    u = None
    with sqlite3.connect(str(environ.get('DB_NAME'))) as conn:
        curr = conn.cursor()
        curr.execute('select * from user where id = :user_id', (user_id,))
        fetched = curr.fetchone()
        if fetched:
            u = User(fetched[0], fetched[1])
            before_tran = conn.total_changes
            curr.execute('delete from user where id = :user_id', (user_id,))
            conn.commit()   
            if (conn.total_changes == before_tran):
                u = None # user deletion has been failed...
    return u                    

def update_or_if_not_create_counter(counter: Counter, user_id: str) -> Counter:
    u = _get_user_by_id(user_id=user_id)    

    if not u:
        return None

    with sqlite3.connect(str(environ.get('DB_NAME'))) as conn:
        curr = conn.cursor()
        curr.execute('select * from counter where uuid = :uuid', (counter.counter_uuid,))
        row = curr.fetchone()
        if row:
            try:
                total_changes_before = conn.total_changes
                curr.execute('insert into user_counter values(?, ?)', (u.id, counter.counter_uuid,))
                conn.commit()
                if conn.total_changes > total_changes_before:
                    return counter
                else:
                    return None
            except sqlite3.IntegrityError as e:
                return counter

        else:
            total_changes_before = conn.total_changes
            curr.execute('insert into counter values(?,?,?,?)', (
                counter.counter_uuid,
                counter.counter_factory,
                counter.owner_name,
                counter.contract_number
                ,
            ))
            conn.commit()
            if conn.total_changes > total_changes_before:
                try:
                    _total_changes = conn.total_changes
                    curr.execute('insert into user_counter values(?, ?)', (u.id, counter.counter_uuid,))
                    conn.commit()
                    if conn.total_changes > _total_changes:
                        return counter
                    else:
                        return None
                except sqlite3.IntegrityError as e:
                    return counter        
            else:
                return None    

def counter_info_by_user(user_id: str) -> List[CounterInfo]:
    u = _get_user_by_id(user_id=user_id)
    if u:
        with sqlite3.connect(environ.get('DB_NAME')) as conn:
            curr = conn.cursor()
            curr.execute("""
                select uuid, factory, owner, contract from counter where uuid in (
                 select counter_uuid from user_counter where user_id = :id)
            """, (user_id, ))
            rows = curr.fetchall()
            counters = []
            for row in rows:
                counters.append(CounterInfo(counter_uuid=row[0], counter_factory=row[1], owner_name=row[2], contract_number=row[3]))
            return counters
    return []    


def delete_counter(user_id: str, counter_uuid: str) -> bool:
    success = True
    u = _get_user_by_id(user_id)
    if u:
        with sqlite3.connect(environ.get('DB_NAME')) as conn:
            cur = conn.cursor()
            cur.execute("""
                delete from user_counter where user_id = :id and counter_uuid = :uuid
            """, (user_id, counter_uuid,))
            conn.commit()
                
    else:
        success = False    

    return success


def _get_user_by_id(user_id: str) -> User:
    with sqlite3.connect(str(environ.get('DB_NAME'))) as conn:
        curr = conn.cursor()
        curr.execute('select * from user where id = :user_id', (user_id,))
        row = curr.fetchone()
        if row:
            return User(id=row[0], name=row[0])
        else:
            return None 

if __name__ == '__main__':
    init_db('viberbot.db')