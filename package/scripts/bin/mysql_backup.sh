#!/bin/bash

export mysql_backup_pid_dir=/var/run
export mysql_backup_pid=mysql_backup.pid
export mysql_backup_log=/var/log/mysql_backup.log

pidf=${mysql_backup_pid_dir}/${mysql_backup_pid}

usage="Usage: mysql_backup.sh [start|stop|restart|status]"

bin=`dirname "${BASH_SOURCE[0]}"`
bin=`cd "$bin"; pwd`

if [ $# != 1 ]; then
	echo "error options"
	echo $usage
	exit 1
fi

function get_all_daemons() {
	return pids=`ps -ef | grep $bin/mysql_backup.py | grep -v grep | awk '{print $2}'`
}

function kill_all_daemon() {
	pids=`ps -ef | grep $bin/mysql_backup.py | grep -v grep | awk '{print $2}'`
	for p in $pids
	do
		kill -9 $p
		sleep 1
	done	

}


case $1 in
start)
	# whethe service is healthy
	if [ -f ${pidf} ]; then
		if kill -0 `cat ${pidf}` > /dev/null 2>&1; then
			echo "Mysql_backup service is running, pid is `cat ${pidf}`, please stop it first!"
			exit 1
		fi
	fi
	# start the service
	nohup  python $bin/mysql_backup.py >${mysql_backup_log} 2>&1 &
	k=$!
	if [ -n "$k" ]; then
		echo $k > $pidf
		echo "mysql backup service started succeed, pid is $k, saved in $pidf"
	else
		echo "mysql backup service started failed!"
	fi
	;;
stop)
	# stop the service daemon
	if [ -f ${pidf} ]; then
		if kill -0 `cat $pidf` > /dev/null 2>&1; then
			echo "stop the service..."
			kill -9 `cat $pidf`
			if [ $? != 0 ]; then
				echo "stop mysql_backup service failed, service pid is`cat ${pidf}`" 
				exit 2
			fi
			rm -f ${pidf}
			echo "stop service succeed!"
			exit 0
		else
			echo "mysql backup service is not running."
		fi
	else
		echo "cannot found mysql_backup pid, please confirm it is running."
	fi
	;;
status)
	if [ -f "$pidf" ]; then
		if kill -0 `cat $pidf` > /dev/null 2>&1; then
			echo "mysql_backup is running."
			exit 0
		else
			echo "find mysql backup pid file, but cannot find the daemon, it may not running."
		fi
	else
		echo "cannot found mysql sevice pid file, may it not running"
		exit 5
	fi
	;;
restart)
	# whether service is runnning
	echo " restart mysql backup..."
	kill_all_daemon
	nohup python $bin/mysql_backup.py > ${mysql_backup_log} 2>&1 &
	if [ $? != 0 ]; then
		echo "restart mysql backup service failed."
		exit 1
	fi
	echo $! > $pidf
	echo " restart mysql backup service succeed, pid is $!, saved to $pidf"
	;;
*)
	echo "cannot known option: $1"
	echo $usage
esac


