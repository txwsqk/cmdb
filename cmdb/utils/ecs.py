#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import json
import logging

from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest

from cmdb.models import *

logger = logging.getLogger(__name__)

ali_ak = os.environ.get('ALI_ACCESS_KEY')
ali_secret = os.environ.get('ALI_SECRET')

clt = client.AcsClient(ali_ak, ali_secret, 'cn-beijing')


def _send_request(request):
    request.set_accept_format('json')
    try:
        response_str = clt.do_action_with_exception(request)
        logger.info(response_str)
        response_detail = json.loads(response_str)
        return response_detail
    except Exception as e:
        logger.error(e)


def describe_instances(pagenumber):
    request = DescribeInstancesRequest()
    request.set_PageNumber(pagenumber)
    request.set_PageSize(100)

    return _send_request(request).get('Instances').get('Instance')


def parse_instances(instances):
    global ret

    for i in instances:
        try:
            outer_ip = ''
            instance_id = i.get('InstanceId')
            instance_name = i.get('InstanceName')
            zone = i.get('ZoneId')
            instance_type = i.get('InstanceType')

            if 'classic' == i.get('InstanceNetworkType'):
                inner_ip = i.get('InnerIpAddress').get('IpAddress')[0]

                if i.get('PublicIpAddress').get('IpAddress'):
                    outer_ip = i.get('PublicIpAddress').get('IpAddress')[0]
            else:
                inner_ip = i.get('NetworkInterfaces').get('NetworkInterface')[0].get('PrimaryIpAddress')

                if i.get('EipAddress'):
                    outer_ip = i.get('EipAddress').get('IpAddress')
        except Exception:
            logger.error('parse_instances error: %s', i)

        try:
            ret.setdefault(inner_ip, dict(
                instance_id=instance_id,
                instance_name=instance_name,
                outer_ip=outer_ip,
                zone=zone,
                instance_type=instance_type,
            ))
        except Exception:
            logger.error('parse_instances() setdefault error: %s', i)

    return ret


ret = {}
cache_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data/ecs.dump')


def get_instances_from_api():
    global ret

    pagesize = 1
    while True:
        instances = describe_instances(pagesize)
        if instances:
            parse_instances(instances)
            pagesize += 1
        else:
            logger.info('finished checkout ecs')
            break

    with open(cache_file, 'w') as f:
        f.write(json.dumps(ret))

    return ret


def get_instances(load_cache=True):
    if os.path.isfile(cache_file) and load_cache:
        return json.load(open(cache_file))

    return get_instances_from_api()


def add_new_instances2cmdb(ips,
                           serve_type,
                           business_manager,
                           maintainer,
                           applicant,
                           application):
    yun_machines = []
    instances = get_instances(load_cache=False)

    for ip in ips.split(','):
        detail = instances.get(ip)
        instance_name = detail.get('instance_name')
        instance_id = detail.get('instance_id')
        outer_ip = detail.get('outer_ip')
        application = Application.objects.get(name=application)

        if '172.16' in ip:
            idc = IDC.objects.get(name='ALI-CN-BEIJING-C')

        try:
            yun_machine = YunMachine(idc=idc,
                                     ip=json.dumps({'inner': ip, 'outer': outer_ip}),
                                     status='online',
                                     serve_type=serve_type,
                                     business_manager=business_manager,
                                     maintainer=maintainer,
                                     applicant=applicant,
                                     application=application,
                                     name=instance_name,
                                     asset_number=instance_id,
                                     is_capitalized=False, )
        except Exception as e:
            logger.error('add_new_instances2cmdb exception:', ip, instance_name)

        yun_machines.append(yun_machine)

    YunMachine.objects.bulk_create(yun_machines)

