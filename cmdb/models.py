# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class UserBehavior(models.Model):
    username = models.CharField(u'用户', max_length=20)
    db = models.CharField(u'涉及数据库', max_length=20)
    action = models.CharField(u'动作', max_length=10)
    detail = models.CharField(u'详情', max_length=200)
    dt = models.DateTimeField(u'时间', auto_now_add=True)

    class Meta:
        ordering = ['-dt']

    def __str__(self):
        return '%s %s %s %s %s' % (self.username, self.db, self.action, self.detail, self.dt)


@python_2_unicode_compatible
class Organization(models.Model):
    name = models.CharField(u'名称', max_length=100, unique=True)
    acronym = models.CharField(u'简称', max_length=20)

    class Meta:
        ordering = ['acronym']

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ProductLine(models.Model):
    name = models.CharField(u'名称', max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Application(models.Model):
    name = models.CharField(u'名称', max_length=50, unique=True)
    business_path = models.ForeignKey(Organization,
                                      verbose_name=u'业务树',
                                      on_delete=models.PROTECT)

    product_line = models.ForeignKey(ProductLine,
                                     verbose_name=u'产品线',
                                     on_delete=models.PROTECT)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return '%s|%s|%s' % (self.business_path.acronym,
                             self.product_line.name,
                             self.name)


@python_2_unicode_compatible
class CommonInfo(models.Model):
    name = models.CharField(u'名称', max_length=100, unique=True)
    contract_num = models.CharField(u'合同编号', max_length=100, null=True, blank=True)
    is_capitalized = models.BooleanField(u'是否资本化')
    operate_version = models.TextField(u'操作记录', null=True, blank=True)
    extend = models.TextField(u'扩展', null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


MACHINE_STATUS_CHOICES = (
    ('online', u'在线'),
    ('offline', u'离线'),
    ('stock', u'库存'),
    ('retire', u'退库'),
    ('receive', u'领用'),
    ('pending', u'退还中'),
)


class IDC(CommonInfo):
    type = models.CharField(max_length=100, verbose_name=u'类型')
    location = models.CharField(max_length=100, verbose_name=u'位置')
    rack = models.CharField(max_length=200, verbose_name=u'机柜')
    cost = models.CharField(max_length=200, verbose_name=u'采购费用')
    ip_range = models.CharField(max_length=200, verbose_name=u'IP段')
    contacts = models.CharField(max_length=200, verbose_name=u'联系人')


class Line(CommonInfo):
    src_idc = models.ForeignKey(IDC, related_name='src_line', on_delete=models.PROTECT)
    dst_idc = models.ForeignKey(IDC, related_name='dst_line', on_delete=models.PROTECT)
    number = models.CharField(verbose_name=u'专线号码', max_length=50)
    line_type = models.CharField(max_length=100, verbose_name=u'线路类型')
    src_link_ip = models.CharField(max_length=100, verbose_name=u'互联源IP')
    dst_link_ip = models.CharField(max_length=100, verbose_name=u'互联目的IP')
    bandwidth = models.CharField(max_length=100, verbose_name=u'带宽')
    ip_range = models.CharField(max_length=200, verbose_name=u'IP段', null=True, blank=True)
    cost = models.CharField(max_length=200, verbose_name=u'采购费用')
    contacts = models.CharField(max_length=200, verbose_name=u'联系人')


class PhysicalMachine(CommonInfo):
    idc = models.ForeignKey(IDC, related_name='physical_machines', on_delete=models.PROTECT)
    asset_number = models.CharField(verbose_name=u'盘点号', max_length=50, unique=True)
    rack = models.CharField(max_length=100, verbose_name=u'机柜信息')
    brand = models.CharField(max_length=100, verbose_name=u'品牌型号')
    sn = models.CharField(verbose_name=u'SN', max_length=100)
    network_interfaces = models.TextField(verbose_name=u'网卡信息')
    ip = models.CharField(max_length=100, verbose_name=u'IP', unique=True)
    cpu = models.IntegerField(verbose_name=u'CPU')
    memory = models.IntegerField(verbose_name=u'内存')
    hard_disk = models.TextField(verbose_name=u'硬盘')
    os_info = models.CharField(max_length=100, verbose_name=u'系统信息')
    status = models.CharField(max_length=10, verbose_name=u'服务状态', choices=MACHINE_STATUS_CHOICES)
    procurement = models.TextField(verbose_name=u'购买明细')
    application = models.ForeignKey(Application, verbose_name=u'应用单元', on_delete=models.PROTECT)
    business_manager = models.CharField(max_length=100, verbose_name=u'业务负责人')
    maintainer = models.CharField(max_length=100, verbose_name=u'运维')
    applicant = models.CharField(max_length=20, verbose_name=u'领用人', null=True, blank=True)
    serve_type = models.CharField(max_length=200, verbose_name=u'服务类型', null=True, blank=True)


class VirtualMachine(CommonInfo):
    physical_machine = models.ForeignKey(PhysicalMachine, related_name='virtual_machines', on_delete=models.PROTECT)
    ip = models.CharField(max_length=100, verbose_name=u'IP', unique=True)
    asset_number = models.UUIDField(u'盘点号', default=uuid.uuid4, editable=False)
    cpu = models.IntegerField(verbose_name=u'CPU')
    memory = models.IntegerField(verbose_name=u'内存')
    hard_disk = models.CharField(max_length=100, verbose_name=u'硬盘')
    os_info = models.CharField(max_length=100, verbose_name=u'系统信息')
    status = models.CharField(max_length=10, verbose_name=u'服务状态', choices=MACHINE_STATUS_CHOICES)
    application = models.ForeignKey(Application, verbose_name=u'应用单元', on_delete=models.PROTECT)
    business_manager = models.CharField(max_length=100, verbose_name=u'业务负责人')
    maintainer = models.CharField(max_length=100, verbose_name=u'运维')
    applicant = models.CharField(max_length=20, verbose_name=u'领用人', null=True, blank=True)
    serve_type = models.CharField(max_length=100, verbose_name=u'服务类型', null=True, blank=True)


class YunMachine(CommonInfo):
    idc = models.ForeignKey(IDC, related_name='yun_machines', on_delete=models.PROTECT)
    ip = models.CharField(max_length=100, verbose_name=u'IP', unique=True)
    asset_number = models.CharField(verbose_name=u'盘点号', max_length=50, unique=True)
    status = models.CharField(max_length=10, verbose_name=u'服务状态', choices=MACHINE_STATUS_CHOICES)
    application = models.ForeignKey(Application, verbose_name=u'应用单元', on_delete=models.PROTECT)
    business_manager = models.CharField(max_length=100, verbose_name=u'业务负责人')
    maintainer = models.CharField(max_length=100, verbose_name=u'运维')
    applicant = models.CharField(max_length=20, verbose_name=u'领用人', null=True, blank=True)
    serve_type = models.CharField(max_length=100, verbose_name=u'服务类型', null=True, blank=True)


class NetworkDevice(CommonInfo):
    idc = models.ForeignKey(IDC, related_name='network_device', on_delete=models.PROTECT)
    asset_number = models.CharField(verbose_name=u'盘点号', max_length=50, unique=True)
    sn = models.CharField(verbose_name=u'SN', max_length=100)
    brand = models.CharField(max_length=100, verbose_name=u'品牌型号')
    device_type = models.CharField(max_length=100, verbose_name=u'设备类型')
    cost = models.IntegerField(u'采购费用')
    rack = models.CharField(max_length=100, verbose_name=u'机柜信息')
    purchase_time = models.DateField(u'采购时间')
    procurement = models.TextField(u'购买明细')
    supplier_info = models.CharField(max_length=100, verbose_name=u'供应商')
    warranty_deadline = models.DateField(u'保修截止期')
    depreciation = models.IntegerField(u'折旧年限')
    status = models.CharField(max_length=10, verbose_name=u'服务状态')
    application = models.ForeignKey(Application, verbose_name=u'应用单元', on_delete=models.PROTECT)
    serve_type = models.CharField(max_length=200, verbose_name=u'服务类型', null=True, blank=True)
    admin_ip = models.CharField(max_length=32, verbose_name=u'管理地址')
    applicant = models.CharField(max_length=20, verbose_name=u'领用人', null=True, blank=True)
    maintainer = models.CharField(max_length=100, verbose_name=u'运维')


class DomainName(CommonInfo):
    purchase_time = models.DateField(u'采购时间')
    expiration_time = models.DateField(u'到期时间')
    supplier_info = models.CharField(u'供应商', max_length=50)
    cost = models.IntegerField(u'采购费用')
    owner = models.CharField(u'所有人', max_length=50)
    contacts = models.CharField(u'联系人', max_length=50)
    status = models.CharField(u'域名状态', max_length=10)


class CDN(CommonInfo):
    supplier_info = models.CharField(u'供应商', max_length=50)
    cname = models.CharField(u'cname地址', max_length=50)
    source_address = models.CharField(u'回源地址', max_length=50)
    strategy = models.CharField(u'加速策略', max_length=50)
    cost = models.IntegerField(u'采购费用')
    sre = models.CharField(u'运维人员', max_length=50)
    rd = models.CharField(u'业务负责人', max_length=50)


class Certificate(CommonInfo):
    domain = models.CharField(u'授权域', max_length=50)
    purchase_time = models.DateField(u'采购时间')
    expiration_time = models.DateField(u'到期时间')
    cost = models.IntegerField(u'采购费用')
    supplier_info = models.CharField(u'供应商', max_length=50)
    owner = models.CharField(u'所有人', max_length=50)
    contacts = models.CharField(u'联系人', max_length=50)


class ElectronicEquipment(CommonInfo):
    brand = models.CharField(max_length=50, verbose_name=u'品牌')
    sn = models.CharField(verbose_name=u'SN', max_length=100)
    category = models.CharField(verbose_name=u'品类', max_length=50)
    status = models.CharField(max_length=10, verbose_name=u'状态', choices=MACHINE_STATUS_CHOICES)
    procurement = models.CharField(u'购买明细', max_length=200)
    purchase_time = models.DateField(u'采购时间')
    cost = models.IntegerField(u'采购费用')
    supplier_info = models.CharField(max_length=100, verbose_name=u'供应商')
    warranty_deadline = models.DateField(u'保修截止期')
    depreciation = models.IntegerField(u'折旧年限')
    business_path = models.ForeignKey(Organization, verbose_name=u'服务路径', on_delete=models.PROTECT)
    location = models.CharField(max_length=50, verbose_name=u'位置')
    applicant = models.CharField(max_length=20, verbose_name=u'领用人', null=True, blank=True)
    administrator = models.CharField(max_length=20, verbose_name=u'管理员')
