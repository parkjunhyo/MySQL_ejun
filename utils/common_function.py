#! /usr/bin/env python

import sys
import os
import time
from help_manual import Help_manual
from system_info import *

class Common_function(Help_manual):

 def get_input_values(self,values):
  if len(values) == 1:
   self.show_manual(values)
   sys.exit()
  else:
   if values[1] in self.function.keys():
    command = values[1]
    if command == "-h" or command == "--help":
     self.function[command](self,values)
     sys.exit()
    ### correct input
    return values[1], values[2:]
   else:
    self.show_manual(values)
    sys.exit()

 def logging_msg(self,filename,msg):
  fopen=open(filename,'a')
  fopen.write(msg+"\n")
  fopen.close()

 def confirm_serveris(self):
  if client_mode == 'server':
   return True
  else:
   print "this command is server only"
   sys.exit()
   return False

 def confirm_input_number(self,values,number_lists):
  if len(values) in number_lists:
   return values
  else:
   self.show_manual(values)
   sys.exit()

 def create_directory_if_exists_not(self,values):
  if values[1] not in os.listdir(values[0]):
   os.mkdir(values[0]+"/"+values[1])

 def display_monitor(self,values):
  for value in values:
   print value

 def confirm_file_existance(self,file_path):
  if os.path.isfile(file_path):
   return True
  else:
   error_msg="[ error : "+time.asctime()+" ] the "+file_path+" does not exist!"
   self.logging_msg(self.run_syslog,error_msg)
   sys.exit()
   return False

 def compare_lists(self,list_A,list_B):
  ## confirm adding elements
  adding_element=[]
  keeping_element=[]
  for list in list_A:
   if list not in list_B:
    adding_element.append(list)
   else:
    keeping_element.append(list)
  ## confirm removing elements
  removing_element=[]
  for list in list_B:
   if list not in list_A:
    removing_element.append(list)
  ## return result
  return adding_element, keeping_element, removing_element
