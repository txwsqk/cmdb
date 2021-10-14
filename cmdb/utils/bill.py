# -*- coding:utf-8 -*-

import json
import os
from datetime import date, timedelta

from aliyunsdkbssopenapi.request.v20171214.QueryBillOverviewRequest import QueryBillOverviewRequest
from aliyunsdkbssopenapi.request.v20171214.QueryInstanceBillRequest import QueryInstanceBillRequest
from aliyunsdkcore.client import AcsClient
from aliyunsdkvpc.request.v20160428.DescribeEipAddressesRequest import DescribeEipAddressesRequest

from connection import Connection


class BillConnection(Connection):
    def __init__(self, region_id='cn-hangzhou'):
        self.access_key_id = os.environ.get('ALI_ACCESS_KEY')
        self.secret_access_key = os.environ.get('ALI_SECRET')

        super(BillConnection, self).__init__(
            region_id,
            'bill',
            access_key_id=self.access_key_id,
            secret_access_key=self.secret_access_key)

    def query_bill(self, period, page_num=1):
        params = {'Action': 'QueryInstanceBill',
                  'BillingCycle': period,
                  'ProductCode': 'ecs',
                  'SubscriptionType': 'Subscription',
                  'PageSize': 100,
                  'PageNum': page_num,
                  }
        return self.get(params)


prev_month = (date.today().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
ecs_bill_path = 'data/ecs_bill.dump.%s' % prev_month
ecs_info_path = 'data/ecs.dump'

product_line_ch = dict(
        bi=u'数据增长',
        tec1=u'技术一部',
        tec2=u'技术二部',
        common =u'公共组件',
        sre=u'基础设施',
        srv_center=u'服务中心',
    )


def generate_ecs_bill():
    bill = BillConnection()
    ecs_statistics = {}
    page_num = 1

    while True:
        result = bill.query_bill(prev_month, page_num=page_num)['Data']['Items']['Item']

        if result:
            page_num += 1
        else:
            break

        for i in result:
            instance_id = i['InstanceID']
            cost = i['PretaxAmount']

            ecs_statistics[instance_id] = cost

    with open(ecs_bill_path, 'w') as f:
        json.dump(ecs_statistics, f)


def get_ecs_bill():
    with open(ecs_info_path) as f:
        ecs_info = json.load(f)

    with open(ecs_bill_path) as f:
        ecs_bill = json.load(f)

    bill = {}
    bill_summary = {}
    bill_detail = {}

    for k, v in ecs_bill.items():
        try:
            instance_name = ecs_info.get(k)['instance_name']
            application = instance_name.split('-')[0]
            product_line = instance_name.split('.')[2]
            bill_summary.setdefault(product_line, []).append(v)

            bill_detail.setdefault(product_line, {})
            bill_detail[product_line].setdefault(application, []).append(v)

        except Exception, e:
            pass

    summary = {v: 0.0 for k, v in product_line_ch.items()}
    summary.update({product_line_ch[k]: '%d' % sum(v) for k, v in bill_summary.items()})
    bill['summary'] = summary

    temp = {}
    for k, v in bill_detail.items():
        for i, j in v.items():
            temp.setdefault(product_line_ch[k], {})[i] = int(sum(j))
    bill['detail'] = temp

    return bill


client = AcsClient(os.environ.get('ALI_ACCESS_KEY'),
                   os.environ.get('ALI_SECRET'),
                   'cn-beijing')


def get_bill_overview(period=prev_month):
    request = QueryBillOverviewRequest()
    request.set_accept_format('json')
    request.set_BillingCycle(period)
    response = client.do_action_with_exception(request)
    total_bill = {}
    for product in json.loads(response)['Data']['Items']['Item']:
        code = product['ProductCode']
        price = product['PretaxAmount']

        if 0 == int(price):
            continue
        total_bill.setdefault(code, []).append(int(price))

    return {k: "{0:.2f}".format(sum(v)) for k, v in total_bill.items()}


def get_rds_bill(period=prev_month):
    business = {
        'rr-2zec951mf8t2a72q0': 'LinkPage',
        'rr-2zejf6vu2a6u0n142': 'LinkActive',
        'rm-2ze612h7947fcb7lz': 'LinkAccount',
        'rm-2ze41ucspn0cl940y': 'LinkActive',
        'rm-2ze92707wkcnq6k7y': 'LinkActive',
        'rm-2zeblg3p7zlr0w4d1': 'LinkActive',
        'rm-2zevy2a782ydb786b': 'LinkPage',
    }

    request = QueryInstanceBillRequest()
    request.set_accept_format('json')
    request.set_PageSize(100)
    request.set_BillingCycle(period)
    request.set_IsHideZeroCharge(True)
    request.set_ProductCode('rds')
    response = client.do_action_with_exception(request)

    rds_bill = {}

    for rds in json.loads(response)['Data']['Items']['Item']:
        instance_id = rds['InstanceID']
        cost = rds['PretaxAmount']
        rds_bill.setdefault(business[instance_id], []).append(cost)

    bill = {v: 0.0 for k, v in product_line_ch.items()}
    bill.update({k: "{0:.2f}".format(sum(v)) for k, v in rds_bill.items()})
    return bill


def get_slb_bill(period=prev_month):
    request = QueryInstanceBillRequest()
    request.set_accept_format('json')
    request.set_PageSize(100)
    request.set_BillingCycle(period)
    request.set_IsHideZeroCharge(True)
    request.set_ProductCode('slb')
    response = client.do_action_with_exception(request)

    slb_bill = {}
    for slb in json.loads(response)['Data']['Items']['Item']:
        name = slb['NickName']
        cost = slb['PretaxAmount']

        if 'linkactive' in name:
            slb_bill.setdefault('LinkActive', []).append(cost)
        elif 'accslb' in name:
            slb_bill.setdefault('LinkAccount', []).append(cost)
        elif 'linkpage' in name:
            slb_bill.setdefault('LinkPage', []).append(cost)
        elif 'linkmp' in name:
            slb_bill.setdefault('LinkActive', []).append(cost)
        elif 'linkkeyword' in name:
            slb_bill.setdefault('LinkKeyWord', []).append(cost)
        else:
            slb_bill.setdefault(u'基础设施', []).append(cost)

    bill = {v: 0.0 for k, v in product_line_ch.items()}
    bill.update({k: "{0:.2f}".format(sum(v)) for k, v in slb_bill.items()})
    return bill


def get_yundisk_bill(period=prev_month):
    request = QueryInstanceBillRequest()
    request.set_accept_format('json')
    request.set_PageSize(100)
    request.set_BillingCycle(period)
    request.set_IsHideZeroCharge(True)
    request.set_ProductCode('yundisk')
    response = client.do_action_with_exception(request)

    ecs_info_path = 'data/ecs.dump'
    ecs_info = json.load(open(ecs_info_path))

    yundisk_bill = {}
    for disk in json.loads(response)['Data']['Items']['Item']:
        instance_config = disk['InstanceConfig']

        if not instance_config:
            continue
        cost = disk['PretaxAmount']
        instance_id = instance_config.split(':')[-1]
        try:
            instance_name = ecs_info.get(instance_id).get('instance_name')
            business_path = instance_name.split('.')[2]

            yundisk_bill.setdefault(product_line_ch[business_path], []).append(cost)
        except:
            pass
    bill = {v: 0.0 for k, v in product_line_ch.items()}
    bill.update({k: "{0:.2f}".format(sum(v)) for k, v in yundisk_bill.items()})
    return bill


def get_eip_info():
    request = DescribeEipAddressesRequest()
    request.set_accept_format('json')
    request.set_PageSize(100)
    response = client.do_action_with_exception(request)

    eip_info = {}

    for i in json.loads(response)['EipAddresses']['EipAddress']:
        eip_id = i.get('AllocationId')
        eip_name = i.get('Name')
        eip_info[eip_id] = eip_name if eip_name else 'free'

    return eip_info


def get_eip_bill(period=prev_month):
    request = QueryInstanceBillRequest()
    request.set_accept_format('json')
    request.set_PageSize(100)
    request.set_BillingCycle(period)
    # request.set_IsHideZeroCharge(True)
    request.set_SubscriptionType('PayAsYouGo')
    request.set_ProductCode('eip')
    response = client.do_action_with_exception(request)

    eip_info = get_eip_info()

    eip_bill = {}
    for i in json.loads(response)['Data']['Items']['Item']:
        eip_id = i.get('InstanceID')
        cost = i.get('PretaxAmount')

        eip_name = eip_info.get(eip_id, 'free')

        if 'free' != eip_name:
            business_path = eip_name.split('_')[-1]
        else:
            business_path = 'sre'

        eip_bill.setdefault(product_line_ch[business_path], []).append(cost)

    bill = {v: 0.0 for k, v in product_line_ch.items()}
    bill.update({k: "{0:.2f}".format(sum(v)) for k, v in eip_bill.items()})
    return bill


if __name__ == '__main__':
    if not os.path.isfile(ecs_bill_path):
        generate_ecs_bill()
