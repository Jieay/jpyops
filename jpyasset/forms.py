#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms

from jpyasset.models import IDC, Items, Areas, Functions, HostAsset, IpAsset, CloudRecord, ServerType, ApplyFile
from jpyasset.models import ApplyVocational, ConfigVocational, VersionVocational, TaskName, ConfigPlanTask, PlanVocational

class IdcForm(forms.ModelForm):

    class Meta:
        model = IDC

        fields = [
            "name", "idcmark", "linkman", "phone", "cloudid", "cloudkey", "cloudregid", "idc_type", "operator", "comment"
        ]
        

class ItemsForm(forms.ModelForm):

    class Meta:
        model = Items

        fields = [
            "name", "itemmark", "linkman", "phone", "comment"
        ]


class AreasForm(forms.ModelForm):

    class Meta:
        model = Areas

        fields = [
            "name", "areamark", "nation_type", "comment"
        ]


class FunctionsForm(forms.ModelForm):

    class Meta:
        model = Functions

        fields = [
            "name", "functionmark", "comment"
        ]


class HostsForm(forms.ModelForm):

    class Meta:
        model = HostAsset

        fields = [
            "wan_ip", "lan_ip", "other_ip", "hostname", "idc", "item", "area", "functs", "username", "password",
            "port", "number", "cpu", "memory","disk", "mac", "system_type", "system_version", "plan", "status",
            "cretime", "exptime", "imageid", "banwidth", "comment"
        ]


class IpassetForm(forms.ModelForm):

    class Meta:
        model = IpAsset

        fields = [
            "ip", "name", "ipmark", "comment"
        ]



class CloudRecordForm(forms.ModelForm):

    class Meta:
        model = CloudRecord

        fields = [
            "idc", "assetcloud", "wordkey", "status"
        ]


class ServerTypeForm(forms.ModelForm):

    class Meta:
        model = ServerType

        fields = [
            "name", "vers", "comment"
        ]


class ApplyVocationalForm(forms.ModelForm):

    class Meta:
        model = ApplyVocational

        fields = [
            "name", "applymark", "comment"
        ]


class ApplyFileForm(forms.ModelForm):

    class Meta:
        model = ApplyFile

        fields = [
            "servername", "name", "appfile", "apply_type", "appvers", "comment"
        ]


class ConfigVocationalForm(forms.ModelForm):

    class Meta:
        model = ConfigVocational

        fields = [
            "configmark", "servername", "tools_type", "idc", "item", "area", "functs", "ostype", "comment"
        ]


class TaskNameForm(forms.ModelForm):

    class Meta:
        model = TaskName

        fields = [
            "name", "confstep", "comment"
        ]
        

class ConfigPlanTaskForm(forms.ModelForm):

    class Meta:
        model = ConfigPlanTask

        fields = [
            "name", "servername", "confname", "confstep", "comment"
        ]        


class PlanVocationalForm(forms.ModelForm):

    class Meta:
        model = PlanVocational

        fields = [
            "name", "planmark", "idc", "item", "area", "functs", "comment"
        ]





