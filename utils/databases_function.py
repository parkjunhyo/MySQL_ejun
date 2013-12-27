#! /usr/bin/env python

import sys
import os
import time
import re
import MySQLdb
from system_info import *

class Databases_function:

 ### access the databases
 def access_database(self,db_host, db_user, db_pass, db_name):
  try:
   if db_name == 'none':
    db=MySQLdb.connect(host=db_host,user=db_user,passwd=db_pass)
   else:
    db=MySQLdb.connect(host=db_host,user=db_user,passwd=db_pass,db=db_name)
  except:
   msg="[ error : "+time.asctime()+" ] can't access database "+db_name
   self.logging_msg(self.run_syslog,msg)
   sys.exit()
  # create cursor
  try:
   cursor=db.cursor()
  except:
   msg="[ error : "+time.asctime()+" ] can't create cursor"
   self.logging_msg(self.run_syslog,msg)
   db.close()
   sys.exit()
  return db,cursor

 ### close the databases
 def close_database(self,db,cursor):
  cursor.close()
  db.close()

 ### priviliges the account user to access from remote
 def priv_user(self,values):
  if self.confirm_serveris():
   new_user, new_pass = self.confirm_input_number(values,[2])
   db,cursor=self.access_database('localhost', 'root', database_passwd, 'none')
   ### create privilige query
   msg=r"grant all privileges on *.* to '"+new_user+"'@'%' identified by'"+new_pass+"';"
   try:
    cursor.execute(msg)
    db.commit()
   except:
    error_msg="[ error : "+time.asctime()+" ] can't priv_user "+new_user+" by "+new_pass
    self.logging_msg(self.run_syslog,error_msg)
    self.close_database(db,cursor)
    sys.exit()
   self.close_database(db,cursor)
   return True

 ### send the database query message to server
 def send_msg(self,values):
  ### confirm the variables  
  info_values = self.confirm_input_number(values,[2,3])
  database_name = info_values[0]
  database_msg = info_values[1]
  options = False
  if len(info_values) == 3:
   options = info_values[2]   
  ### send the query messages 
  db,cursor=self.access_database(database_host, 'root', database_passwd, database_name)
  try:
   cursor.execute(database_msg)
   db.commit()
  except:
   error_msg="[ error : "+time.asctime()+" ] can't send_msg "+database_msg
   self.logging_msg(self.run_syslog,error_msg)
   self.close_database(db,cursor)
   sys.exit()
  ### get the resulte data from query
  exec_result=cursor.fetchall()
  self.close_database(db,cursor)
  ### display the result into the monitor
  if options == 'echo':
   self.display_monitor(exec_result)
  ### return the result
  return exec_result

 ### sync the database tables
 def sync_db(self,values):
  if self.confirm_serveris():
   info_values = self.confirm_input_number(values,[1])
   file_name = info_values[0].split("/")[len(info_values[0].split("/"))-1]
   file_path = self.synctb_d+"/"+file_name

   if self.confirm_file_existance(file_path):

    ### step 1. create the database if not exist
    all_databases=[]
    for dbname in self.send_msg(['none', 'show databases;']):
     if dbname[0] not in all_databases:
      all_databases.append(dbname[0])
    if file_name not in all_databases:
     self.send_msg(['none','create database '+file_name+';'])
     log_msg="[ logging : "+time.asctime()+" ] create the database "+file_name
     self.logging_msg(self.run_syslog,log_msg)

    ### step 2. find table lists (db,file) to add table
    # search the table list from database
    table_names_from_db=[]
    for table_name in self.send_msg([file_name, 'show tables;']):
     if table_name[0] not in table_names_from_db:
      table_names_from_db.append(table_name[0])
    # search the table list from file
    table_names_from_file=[]
    fopen = open(file_path,'r')
    read_msg = fopen.readline().strip()
    while read_msg: 
     table_name = read_msg.split()[0]
     if table_name not in table_names_from_file:
      table_names_from_file.append(table_name)
     read_msg = fopen.readline().strip()
    fopen.close()
    # find new, origin and old_table list in the database
    new_tables, origin_tables, old_tables = self.compare_lists(table_names_from_file,table_names_from_db)

    ### step 3. create new table in the database (new table process)
    for new_table in new_tables:
     fopen = open(file_path,'r')
     read_line = fopen.readline().strip()
     line_selected=[]
     while read_line:
      if new_table == re.sub(r',$','',read_line).split()[0]:
       read_matched = ' '.join(re.sub(r',$','',read_line).split()[1:])
       if read_matched not in line_selected:
        line_selected.append(read_matched)
       else:
        error_msg="[ error : "+time.asctime()+" ] there is duplicated entry "+read_matched+"for new table :"+new_table
        self.logging_msg(self.run_syslog,error_msg)
        sys.exit()
      read_line = fopen.readline().strip()
     fopen.close()
     ### send the query to database
     self.send_msg([file_name, "create table "+new_table+" ("+','.join(line_selected)+");"])
     log_msg="[ logging : "+time.asctime()+" ] create the table "+new_table+" in the database "+file_name
     self.logging_msg(self.run_syslog,log_msg)

    ### step 4. update the new entry in the table (existed table process)
    for origin_table in origin_tables:

     ## step 4-1. find out the table entites from database
     entry_from_db=[] 
     for enties in self.send_msg([file_name, 'desc '+origin_table+';']):
      if enties[0] not in entry_from_db:
       entry_from_db.append(enties[0])

     ## step 4-2. find out the table entites from files
     entry_from_file=[]
     fopen = open(file_path,'r')
     read_msg = fopen.readline().strip()
     while read_msg:
      if read_msg.split()[0] == origin_table:
       if read_msg.split()[1] not in entry_from_file:
        entry_from_file.append(read_msg.split()[1])
       else:
        error_msg="[ error : "+time.asctime()+" ] there is duplicated entry "+read_msg.split()[1]+"for new table :"+origin_table
        self.logging_msg(self.run_syslog,error_msg)
        sys.exit()
      read_msg = fopen.readline().strip()
     fopen.close()
     
     ### step 4-3. search the new, origin, old entries in the table
     new_enties, origin_enties, old_enties = self.compare_lists(entry_from_file,entry_from_db) 

     ### step 4-4. update the new entities into the table
     for new_entry in new_enties:
      fopen = open(file_path,'r')
      read_line = fopen.readline().strip()
      line_selected=[]
      while read_line:
       lines_msg = re.sub(r',$','',read_line).split()
       if lines_msg[0] == origin_table and lines_msg[1] == new_entry:
        self.send_msg([file_name, "alter table "+origin_table+" add "+new_entry+" "+' '.join(lines_msg[2:])])
        log_msg="[ logging : "+time.asctime()+" ] add new entry "+new_entry+" in "+origin_table+" of "+file_name
        self.logging_msg(self.run_syslog,log_msg)
       read_line = fopen.readline().strip()
      fopen.close()

 ### get the table enties list from datase
 def _get_table_enties_from_database(self,database_name):
  table_enties_dict={}
  for table_names in self.send_msg([database_name,"show tables;"]):
   enties_lists=[]
   for enties in self.send_msg([database_name,"desc "+table_names[0]+";"]):
    if enties[0] not in enties_lists:
     enties_lists.append(enties[0])
    else:
     msg="[ error : "+time.asctime()+" ] there is duplicated entry, during desc "+table_names[0]+"; in "+database_name
     self.logging_msg(self.run_syslog,msg)
     sys.exit()
   ### arrange the result
   table_enties_dict[table_names[0]]=enties_lists
  ### return the result
  return table_enties_dict
