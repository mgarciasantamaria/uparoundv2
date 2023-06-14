#!/usr/bin/env python
#_*_ codig: utf8 _*_
import time, sqlite3, os, boto3, json, datetime, traceback
from Modules.functions import *
from Modules.constants import *

Counter=0
Replace_list=[]
aws_session=boto3.Session(profile_name='pythonapps')
s3=aws_session.client('s3')

while True:
    try:
        time.sleep(300)
        con=sqlite3.connect('data.db')
        cur=con.cursor()
        response1=cur.execute("select * from data").fetchall()
        time.sleep(60)
        Counter_Before=Counter
        for file in response1:
            file_size=os.path.getsize(f"{src_path}{file[0]}")
            if file_size==file[1]:
                file_path=f"{src_path}{file[0]}"
                if s3.list_objects_v2(Bucket=bucket, Prefix=file[0])['KeyCount'] != 0:
                    file_path=f"{src_path}{file[0]}"
                    s3.upload_file(file_path, bucket, file[0], Callback=ProgressPercentage(file_path))
                    time.sleep(5)
                    os.remove(file_path)
                    cur.execute(f"delete from data where name like '{file[0]}'")
                    con.commit()
                    print(f"{file[0]} file eliminado")
                    Counter+=1
                    Replace_list.append(file)
                else:
                    s3.upload_file(file_path, bucket, file[0], Callback=ProgressPercentage(file_path))
                    time.sleep(5)
                    os.remove(file_path)
                    cur.execute(f"delete from data where name like '{file[0]}'")
                    con.commit()
                    print(f"{file[0]} file eliminado")
                    Counter+=1
            else:
                cur.execute(f"update data set bytes={file_size} where name like '{file[0]}'")
                con.commit()
                pass
        con.close()
        if Counter!=0 and Counter==Counter_Before:
            with open(json_path, "r") as json_file:
                    json_data=json.load(json_file)
            date_json=str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'))
            json_data[date_json]={
                "Total videos uploaded": Counter,
                "Replace List": Replace_list
            }
            with open(json_path, "w") as json_file:
                json.dump(json_data, json_file)
            text_log=f"Total videos uploaded: {Counter}\nReplace List {Replace_list}"
            print(text_log)
            Counter=0
            Replace_list=[]
        else:
            print("File not found\n\t\t\tEnd\n")
    except:
        error=sys.exc_info()[2]
        error_Info=traceback.format_tb(error)[0]
        text_log=f"Total videos uploaded: {Counter}\nReplace List {Replace_list}"
        print(text_log)
        text_Mail=f"An error occurred while executing the awsupload application on the RUNAPPSPROD server (10.10.130.39)\nTraceback info: {error_Info}\nError_Info:{str(sys.exc_info()[1])}\n\n"+text_log
        print(text_log)
        Send_Mail(text_Mail, "Error awsuploadaround")
        quit()