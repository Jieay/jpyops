#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from jpyasset.models import HostAsset, PlanVocational


TASK_STATUS = (
    (1, u"未执行"),
    (2, u"已执行")
    )

class Tasklist(models.Model):
    taskid = models.BigIntegerField(verbose_name=u"任务ID")
    host = models.ManyToManyField(HostAsset, verbose_name=u"主机ID")
    plan = models.ManyToManyField(PlanVocational, blank=True, null=True, verbose_name=u'方案ID')
    status = models.IntegerField(choices=TASK_STATUS, blank=True, null=True, default=1, verbose_name=u"任务状态")
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.taskid  


RATE_STATUS = (
    (1, u"执行成功"),
    (2, u"执行失败")
    )

class Taskrate(models.Model):
    task = models.ForeignKey("Tasklist", blank=True, null=True, on_delete=models.SET_NULL, verbose_name=u'任务ID')
    status = models.IntegerField(choices=RATE_STATUS, blank=True, null=True, default=1, verbose_name=u"执行状态")
    create_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.status
    

class Taskcmdhistory(models.Model):
    task = models.ForeignKey("Tasklist", blank=True, null=True, on_delete=models.SET_NULL, verbose_name=u'任务ID')
    fruits = models.TextField()
    create_time = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.fruits
    
    
class TaskTest(models.Model):
    hostip = models.CharField(max_length=128, blank=True, null=True)
    fruits = models.TextField()
    create_time = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.fruits    

