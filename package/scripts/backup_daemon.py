#!/usr/bin/python
#-*-encoding: UTF-8-*-
import time, sched
import threading
import interval
from xml.etree import ElementTree

from resource_management import *
s = sched.scheduler(time.time, time.sleep)
# 解析配置文件，得到要备份的数据库和定时备份的时间，精确到分钟

tree = ElementTree.parse("/etc/mysql_backup/conf/mysql_backup.xml")

# parse property file, then export into os env
def get(conf):
    root = tree.getroot()
    for p in root.findall('property'):
        name = p.find('name').text
        if name == conf:
            value = p.find('value').text
            return (name, value)

conf_dir = get("mysql.backup.conf.dir")[1]
daemon_dir = get("mysql.backup.daemon.pid.dir")[1]
daemon_pid_file = get("mysql.backup.daemon.pid.file")[1]
backup_hour = get("mysql.backup.hour")[1]
backup_minute = get("mysql.backup.minute")[1]
backup_local_dir = get("mysql.backup.local.directory")[1]
backup_hdfs_dir = get("mysql.backup.hdfs.directory")[1]
backup_log = get("mysql.backup.log")[1]

log = open("/var/log/mysql_backup.log", 'w')
now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
log.writelines(str(now) + "  MySQL Backup daemon start...\n")
log.write("configuration parameters:\n")

log.write("conf_dir : " + conf_dir + '\n')
log.write("daemon_dir: " + daemon_dir + '\n')
log.write("daemon_pid_file: " + daemon_pid_file + '\n')
log.write("backup_hour: " + backup_hour + '\n')
log.write("backup_minute: " +  backup_minute + '\n')
log.write("backup_local_dir: " +  backup_local_dir + '\n')
log.write("backup_hdfs_dir: " + backup_hdfs_dir + '\n')
log.write("backup_log: " + backup_log + '\n')

log.flush()

def mysql_backup(database):
    "\n----------------------------------------"
    log.write("begin time:\t" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '\n')
    log.write("thread id:\t" + threading.current_thread().getName() + '\n')
    log.write("backup mysql database :  " + database + '\n')
    time.sleep(10)
    log.write('end time:\t' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n')

def start_mysql_backup_daemon():
    try:
        while True:
            t1 = threading.Thread(target=mysql_backup, args=("ambari",))
            t2 = threading.Thread(target=mysql_backup, args=("hive",))
            seconds = interval.interval().get_interval()
            s.enter(seconds, 0, t1.start,())
            s.enter(seconds, 0, t2.start,())
            s.run()

    except Exception, e:
        log.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) , " error: ", e.message)
    finally:
        log.close()
    while True:
        t1 = threading.Thread(target=mysql_backup, args=("ambari",))
        t2 = threading.Thread(target=mysql_backup, args=("hive",))
        seconds = interval.interval().get_interval()
        s.enter(seconds, 0, t1.start,())
        s.enter(seconds, 0, t2.start,())
        s.run()
main = threading.Thread(target=start_mysql_backup_daemon(), args=())
main.setDaemon()
main.start()

print "ERROR: MySQL backup job ended."
