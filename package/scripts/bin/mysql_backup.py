
#-*-encoding: UTF-8-*-
import time, sched
import threading
from xml.etree import ElementTree
import os
import datetime

def get_next_interval(conf):
    if conf.has_key("init"):
        return 3600 * 24
    else:
        current_time = datetime.datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        next_hour = int(conf['mysql.backup.hour'])
        next_minute = int(conf['mysql.backup.minute'])
        now_sec = current_hour * 3600 + current_minute * 60
        next_sec = next_hour * 3600 + next_minute * 60
        if now_sec < next_sec:
            return next_sec - now_sec
        else:
            return 3600 * 24 - now_sec + next_sec

s = sched.scheduler(time.time, time.sleep)

kvs = {}

tree = ElementTree.parse("/etc/mysql_backup/conf/mysql_backup.xml")
root = tree.getroot()
for p in root.findall('property'):
    name = p.find('name').text
    value = p.find('value').text
    kvs[name] = value

# daemon_dir = kvs["mysql.backup.daemon.pid.dir"]
# daemon_pid_file = kvs["mysql.backup.daemon.pid.file"]
# backup_hour = kvs["mysql.backup.hour"]
# backup_minute = kvs["mysql.backup.minute"]
# backup_local_dir = kvs["mysql.backup.local.directory"]
# backup_hdfs_dir = kvs["mysql.backup.hdfs.directory"]
# backup_log = kvs["mysql.backup.log"]

backup_databases = kvs['mysql.backup.databases'].split(',')
backup_dir_local = kvs['mysql.backup.local.directory']
backup_dir_hdfs = kvs['mysql.backup.hdfs.directory']
backup_log_file = kvs['mysql.backup.log']

log = open(backup_log_file, 'w')
now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
log.writelines(now + "  MySQL Backup daemon start...\n")
log.write("configuration parameters:\n")
# print configuration parameters
for kv in kvs:
    log.write(kv + " : " + kvs[kv] + "\n")

log.flush()

def mysql_backup(databases):
    log.write("\n----------------- backup -----------------------\n")
    for database in databases:
        log.write("begin time:\t" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\n")
        log.write("thread id:\t" + threading.current_thread().getName() + "\n")
        log.write("backup mysql database :  " + database + "\n")
        # cmd = 'mysqldump -uroot -pManWei1234_  ' + database + " > " + database + ".bk." + time.strftime("%Y%m%d%H%M%S")
        cmd = "mysqldump -uroot -pManWei1234_  %s > %s/%s.bk.%s" % (database, backup_dir_local, database, time.strftime("%Y%m%d%H%M%S"))
        log.write(cmd + "\n")
        lines = os.popen(cmd).readlines()
        log.write(str(lines))
        time.sleep(5)
        log.write('\nend time:\t' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n")
        log.flush()

def start_mysql_backup_daemon():
    try:
        while True:
            # start a daemon to backup databases in sequence
            t = threading.Thread(target=mysql_backup, args=(backup_databases,))
            seconds = get_next_interval(kvs)
            s.enter(seconds, 0, t.start,())
            s.run()
            kvs['init'] = 'True'
    except Exception, e:
        log.write("%s:  ERROR:  %s" %(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), str(e)))
    finally:
        log.close()
start_mysql_backup_daemon()

