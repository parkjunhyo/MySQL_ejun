#! /usr/bin/env python

import sys
from databases_function import Databases_function

class Help_manual(Databases_function):

 def show_manual(self,values):
  print "\n"
  print "this is the [ "+self.shell_name+" ] command manual"
  print "\n"
  print "  : priv_user (new user) (new pass)"
  print "          >> give the auth to access from remote\n"
  print "  : send_msg (database) (\"query\") (echo,option)"
  print "          >> send the query and report the result\n" 
  print "  : sync_db (database table file)"
  print "          >> sync the database table (adding new table)" 
  print "          >> reference the database_sync directory\n" 


 function={"-h":show_manual,
           "--help":show_manual,
           "priv_user":Databases_function.priv_user,
           "send_msg":Databases_function.send_msg,
           "sync_db":Databases_function.sync_db}

 
