#!/usr/bin/env python
#_*_ codig: utf8 _*_
import os, time, sqlite3
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from Modules.constants import *

def on_created(event):
    con=sqlite3.connect('data.db')
    cur=con.cursor()
    file_name=os.path.basename(event.src_path)
    r=cur.execute(f"select bytes from data where name like '{file_name}'").fetchall()
    if r==[]:
        file_size=os.path.getsize(f"{src_path}{file_name}")
        cur.execute(f"insert into data values('{file_name}', {file_size})")
        con.commit()
        print('Create', os.path.basename(event.src_path))
    else:
        pass
    con.close()

if __name__ == "__main__":
    event_handler = FileSystemEventHandler()
    event_handler.on_created = on_created
    observer = PollingObserver()
    observer.schedule(event_handler, src_path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
