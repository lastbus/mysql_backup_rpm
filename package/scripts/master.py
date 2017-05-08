#!/usr/bin/python

#-*-encoding: utf-8 -*-

import time, sched
import threading
from resource_management import *

class MySQLBackup(Script):

    def install(self, env):
        print "======  install MySQLBackup service ======"
        cp_cmd = format('cp /var/lib/ambari-server/resources/stacks/HDP/2.5/services/MYSQLBACKUP/configuration/mysql_backup.xml  /etc/mysql_backup/conf ')
        Execute(cp_cmd, user = 'root')

    def configure(self, env):
	import params
	env.set_params(params)
        print 'Configure the MySQL backup service'

    def stop(self, env):
        print 'Stopped the Sample Srv Master'
        daemon_cmd = format("/var/lib/ambari-server/resources/stacks/HDP/2.5/services/MYSQLBACKUP/package/scripts/bin/mysql_backup.sh stop ")
	try:
		Execute(daemon_cmd, user = "root")
	except:
		show_logs(params.backup_log, user = 'root')
		raise
	print "stop mysql backup service succeed!"


    def start(self, env):
        print '====== start the mysql_backup daemon  ========='
        import params
	print 'params.conf_dir'
	print params.conf_dir
        env.set_params(params)
	self.configure(env)
	print 'env'
	print dir(env)
        daemon_cmd = format("/var/lib/ambari-server/resources/stacks/HDP/2.5/services/MYSQLBACKUP/package/scripts/bin/mysql_backup.sh start")
        try:
            Execute(daemon_cmd, user = "root")
        except:
            show_logs(params.backup_log, user='root')
            raise
        print "===== start mysql_backup daemon succeed  ========"

    def restart(self, env):
        print 'Restart the mysql_backup'
        daemon_cmd = format("/var/lib/ambari-server/resources/stacks/HDP/2.5/services/MYSQLBACKUP/package/scripts/bin/mysql_backup.sh restart")
	try:
		Execute(daemon_cmd, user = 'root')
	except:
		show_log(params.backup_log, user = 'root')
		raise
	print "restart mysql backup service succeed!"

    def status(self, env):
        print 'Status of the mysql_back'
        daemon_cmd = format("/var/lib/ambari-server/resources/stacks/HDP/2.5/services/MYSQLBACKUP/package/scripts/bin/mysql_backup.sh status")
	try:
		Execute(daemon_cmd, user = 'root')
	except:
		show_log(params.backup_log, user = 'root')
		raise	

if __name__ == '__main__':
	MySQLBackup().execute()
