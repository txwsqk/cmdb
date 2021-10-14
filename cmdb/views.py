# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core import serializers as S
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from cmdb.serializers import *
from utils import ecs, bill


class UserBehaviorViewSet(viewsets.ModelViewSet):
    queryset = UserBehavior.objects.all()
    serializer_class = UserBehaviorSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filter_fields = ('username', 'db')
    search_fields = ('username', 'db')


class IDCViewSet(viewsets.ModelViewSet):
    queryset = IDC.objects.all()
    serializer_class = IDCSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filter_fields = ('name', 'contract_num', 'location')
    search_fields = ('name', 'contract_num', 'location')


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filter_fields = ('name', 'acronym')
    search_fields = ('name', 'acronym')


class ProductLineViewSet(viewsets.ModelViewSet):
    queryset = ProductLine.objects.all()
    serializer_class = ProductLineSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filter_fields = ('name',)
    search_fields = ('name',)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filter_fields = ('name', 'business_path__acronym', 'product_line__name')
    search_fields = ('name', 'business_path__acronym', 'product_line__name')


class LineViewSet(viewsets.ModelViewSet):
    queryset = Line.objects.all()
    serializer_class = LineSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filter_fields = ('name', 'number', 'contacts', 'contract_num')
    search_fields = ('name', 'number', 'contacts', 'contract_num')


class PhysicalMachineFilter(FilterSet):
    class Meta:
        model = PhysicalMachine
        fields = {
            'name': ['iexact', 'in', 'icontains', 'regex'],
            'asset_number': ['iexact', 'in', 'icontains', 'regex'],
            'sn': ['iexact', 'in', 'icontains', 'regex'],
            'ip': ['iexact', 'in', 'icontains', 'regex'],
            'application__name': ['iexact', 'in', 'icontains', 'regex'],
        }


class PhysicalMachineViewSet(viewsets.ModelViewSet):
    queryset = PhysicalMachine.objects.all().exclude(status='retire')
    serializer_class = PhysicalMachineSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filter_class = PhysicalMachineFilter
    search_fields = ('name', 'asset_number', 'ip', 'sn', 'contract_num',
                     'status', 'idc__name', 'serve_type', 'applicant',
                     'application__name', 'application__business_path__acronym',
                     'application__product_line__name')


class VirtualMachineFilter(FilterSet):
    class Meta:
        model = VirtualMachine
        fields = {
            'name': ['iexact', 'in', 'icontains', 'regex'],
            'ip': ['iexact', 'in', 'icontains', 'regex'],
            'application__name': ['iexact', 'in', 'icontains', 'regex'],
        }


class VirtualMachineViewSet(viewsets.ModelViewSet):
    queryset = VirtualMachine.objects.all().exclude(status='retire')
    serializer_class = VirtualMachineSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filter_class = VirtualMachineFilter
    search_fields = ('name', 'ip', 'asset_number', 'status', 'application__name',
                     'serve_type', 'status', 'physical_machine__name',
                     'application__business_path__acronym', 'applicant',
                     'application__product_line__name')


class YunMachineFilter(FilterSet):
    class Meta:
        model = YunMachine
        fields = {
            'name': ['iexact', 'in', 'icontains', 'regex'],
            'ip': ['iexact', 'in', 'icontains', 'regex'],
            'serve_type': ['iexact', 'in', 'icontains', 'regex'],
            'status': ['iexact', 'in', 'icontains', 'regex'],
            'application__name': ['iexact', 'in', 'icontains', 'regex'],
        }


class YunMachineViewSet(viewsets.ModelViewSet):
    queryset = YunMachine.objects.all().exclude(status='retire')
    serializer_class = YunMachineSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filter_class = YunMachineFilter
    search_fields = ('name', 'ip', 'asset_number', 'application__name',
                     'idc__name', 'serve_type', 'status', 'business_manager',
                     'application__business_path__acronym', 'maintainer',
                     'application__product_line__name')


class NetworkDeviceFilter(FilterSet):
    class Meta:
        model = NetworkDevice
        fields = {
            'name': ['iexact', 'in', 'icontains', 'regex'],
            'admin_ip': ['iexact', 'in', 'icontains', 'regex'],
            'asset_number': ['iexact', 'in', 'icontains', 'regex'],
        }


class NetworkDeviceViewSet(viewsets.ModelViewSet):
    queryset = NetworkDevice.objects.all().exclude(status='retire')
    serializer_class = NetworkDeviceSerializer
    filter_class = NetworkDeviceFilter
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    search_fields = ('name', 'sn', 'admin_ip', 'applicant', 'application__name',
                     'application__business_path__acronym', 'maintainer',
                     'application__product_line__name', 'brand', 'rack')


class DomainNameViewSet(viewsets.ModelViewSet):
    queryset = DomainName.objects.all()
    serializer_class = DomainNameSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    search_fields = ('name', 'contacts')


class CDNViewSet(viewsets.ModelViewSet):
    queryset = CDN.objects.all()
    serializer_class = CDNSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    search_fields = ('name', 'cname')


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    search_fields = ('name', 'domain', 'contacts')


class ElectronicEquipmentFilter(FilterSet):
    class Meta:
        model = ElectronicEquipment
        fields = {
            'name': ['iexact', 'in', 'icontains', 'regex'],
            'sn': ['iexact', 'in', 'icontains', 'regex'],
            'applicant': ['iexact', 'in', 'icontains', 'regex'],
            'category': ['iexact', 'in', 'icontains', 'regex'],
            'brand': ['iexact', 'in', 'icontains', 'regex'],
        }


class ElectronicEquipmentViewSet(viewsets.ModelViewSet):
    queryset = ElectronicEquipment.objects.all().exclude(status='retire')
    serializer_class = ElectronicEquipmentSerializer
    filter_class = ElectronicEquipmentFilter
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    search_fields = ('name', 'sn', 'applicant', 'brand',
                     'status', 'supplier_info')


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def add_instances(request):
    params = request.POST
    ips = params.get('ips')
    serve_type = params.get('serve_type')
    business_manager = params.get('business_manager')
    maintainer = params.get('maintainer')
    applicant = params.get('applicant')
    application = params.get('application')

    try:
        ecs.add_new_instances2cmdb(ips,
                                   serve_type,
                                   business_manager,
                                   maintainer,
                                   applicant,
                                   application)
        return JsonResponse({'status': 200}, safe=False)
    except Exception, e:
        import sys
        import traceback

        e_type, e_value, e_tb = sys.exc_info()
        print traceback.extract_tb(e_tb)
        return JsonResponse({'errors': str(e)}, safe=False, status=500)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_model_retire(request, name):
    model_map = dict(
        physical_machine=PhysicalMachine,
        virtual_machine=VirtualMachine,
        yun_machine=YunMachine,
        network_device=NetworkDevice,
        elec_equipment=ElectronicEquipment,
    )

    try:
        qs = model_map.get(name).objects.filter(status='retire')

        return JsonResponse(S.serialize('json', qs), safe=False)
    except Exception, e:
        return JsonResponse({'errors': str(e)}, safe=False, status=500)


def get_model_statistics():
    model_map = dict(
        physicalmachine=PhysicalMachine,
        virtualmachine=VirtualMachine,
        yunmachine=YunMachine,
        networkdevice=NetworkDevice,
        electronicequipment=ElectronicEquipment,
    )

    ret = {}
    for k, v in model_map.items():
        total_count = v.objects.exclude(status='retire').count()
        status_nums = v.objects.values('status').annotate(scount=Count('id')).order_by()

        org_statistics = {}
        status_statistics = {}
        application_statistics = {}
        productline_statistics = {}
        productline_detail = {}

        if getattr(v, 'application', False):
            app_prodline = Application.objects.annotate(num=Count(k))
            for m in app_prodline:
                if m.num == 0:
                    pass
                else:
                    productline_detail.setdefault(m.product_line.name, {})[m.name] = m.num

            prod_nums = ProductLine.objects.annotate(num_p=Count('application__%s' % k))

            for t in prod_nums:
                if t.num_p == 0:
                    continue
                productline_statistics[t.name] = t.num_p

            org_nums = Organization.objects.annotate(num_m=Count('application__%s' % k))

            for i in org_nums:
                if i.num_m == 0:
                    continue
                org_statistics[i.name] = i.num_m

                app = v.objects.filter(application__business_path__acronym=i.acronym) \
                    .values('application__name') \
                    .annotate(scount=Count('id')).order_by()

                for t in app:
                    application_statistics.setdefault(i.name, {})[t['application__name']] = t['scount']

        for j in status_nums:
            status_statistics[j['status']] = j['scount']

        ret[k] = dict(total_count=total_count,
                      org_statistics=org_statistics,
                      status_statistics=status_statistics,
                      application_statistics=application_statistics,
                      productline_statistics=productline_statistics,
                      productline_detail=productline_detail,
                      )

    return ret


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
@cache_page(3600 * 6)
def get_dashboard_metric(request):
    s = get_model_statistics()

    aliyun_bill = dict()
    bill_overview = bill.get_bill_overview()
    aliyun_bill['overview'] = bill_overview
    aliyun_bill['ecs'] = bill.get_ecs_bill()
    aliyun_bill['rds'] = bill.get_rds_bill()
    aliyun_bill['slb'] = bill.get_slb_bill()
    aliyun_bill['eip'] = bill.get_eip_bill()
    aliyun_bill['yundisk'] = bill.get_yundisk_bill()

    # statistics by product_line
    product_line_statistics = {v: 0.0 for k, v in bill.product_line_ch.items()}
    for k in product_line_statistics:
        product_line_statistics[k] = "{0:.2f}".format(float(aliyun_bill['eip'][k]) +
                                                      float(aliyun_bill['rds'][k]) +
                                                      float(aliyun_bill['ecs']['summary'][k]) +
                                                      float(aliyun_bill['yundisk'][k]) +
                                                      float(aliyun_bill['slb'][k]))

    sre_extension = "{0:.2f}".format(float(product_line_statistics[u'基础设施']) +
                                     float(bill_overview['alikafka']) +
                                     float(bill_overview['cdn']) +
                                     float(bill_overview['snapshot']) +
                                     float(bill_overview['vpn']) +
                                     float(bill_overview['oss']))

    product_line_statistics[u'基础设施'] = sre_extension

    aliyun_bill['summary'] = product_line_statistics

    s.update(dict(bill=aliyun_bill))

    return JsonResponse(s, safe=False)
