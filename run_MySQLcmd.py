#! /usr/bin/env python

import sys
import os
from utils.common_function import Common_function


class Run_commander(Common_function):

 def __init__(self, values):

  ### current Working directory
  self.directory=os.getcwd()
  ### default log file information
  self.log_d=self.directory+"/log"
  self.run_syslog=self.log_d+"/runsys.log"
  ### default database table information 
  self.synctb_d=self.directory+"/database_sync"
  ### shell name define
  self.shell_name=values[0]
  # Confrim the folder status 
  self.create_directory_if_exists_not([self.directory,"log"])
  self.create_directory_if_exists_not([self.directory,"database_sync"])


 def run_command(self,values):

  # Confirm the input values
  self.command, self.values = Common_function.get_input_values(self, values)
  self.function[self.command](self,self.values)


if __name__=='__main__':
 command = Run_commander(sys.argv)
 command.run_command(sys.argv)
 
