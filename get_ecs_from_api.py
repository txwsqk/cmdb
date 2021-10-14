#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import json
import logging
from pprint import pprint

from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest


logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

ali_ak = os.environ.get('ALI_ACCESS_KEY')
ali_secret = os.environ.get('ALI_SECRET')

clt = client.AcsClient(ali_ak, ali_secret, 'cn-beijing')


def _send_request(request):
    request.set_accept_format('json')
    try:
        response_str = clt.do_action_with_exception(request)
        logging.info(response_str)
        response_detail = json.loads(response_str)
        return response_detail
    except Exception as e:
        logging.error(e)


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
            pprint(i)
            raise SystemExit

        try:
            ret.setdefault(instance_id, dict(
                inner_ip=inner_ip,
                instance_name=instance_name,
                outer_ip=outer_ip,
                zone=zone,
                instance_type=instance_type,
            ))
        except Exception:
            pprint(i)
            raise SystemExit

    return ret


if __name__ == '__main__':
    ret = {}

    pagesize = 1
    while True:
        instances = describe_instances(pagesize)
        if instances:
            parse_instances(instances)
            pagesize += 1
        else:
            print 'finished checkout ecs'
            break

    with open('data/ecs.dump', 'w') as f:
        f.write(json.dumps(ret))