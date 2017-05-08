#!/usr/bin/python
#-*- encoding:utf-8 -*-
import datetime

class interval(object):
    interval = 60 * 60
    current_time = datetime.datetime.now()
    current_hour = current_time.hour
    current_minute = current_time.minute
    current_second = current_time.second
    init = False

    @classmethod
    def get_interval(self):
        '''
        每小时执行一次命令
        :return:
        '''
        if not self.init:
            self.init = True
            return 60 * 60 - 60 * self.current_minute - self.current_second
        else:
            return self.interval

    @classmethod
    def get_next_interval(self, next_time_hour, next_time_minute):
        '''
        每隔一天执行一次
        :param next_time_hour:  下次执行的小时
        :param next_time_minute:  下次执行的分钟
        :return: 当前时间，距离下次执行的秒数
        '''
        if not self.init:
            self.init = True
            current_seconds = self.current_hour * 3600 + self.current_minute * 60 + self.current_second
            target_seconds = next_time_hour * 3600 + 60 * next_time_minute
            if current_seconds < target_seconds:
                return target_seconds - current_seconds
            else:
                return 24 * 3600 - current_seconds + target_seconds
        else:
            return 60 * 60 * 24


