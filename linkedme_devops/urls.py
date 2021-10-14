"""linkedme_devops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import os

from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers

from cmdb import views


def print_url_pattern_names(patterns):
    """Print a list of url_pattern and their names"""
    for pat in patterns:
        if pat.__class__.__name__ == 'RegexURLResolver':
            print_url_pattern_names(pat.url_patterns)
        elif pat.__class__.__name__ == 'RegexURLPattern':
            if pat.name is not None:
                print '[API-URL] {} \t\t\t-> {}'.format(pat.name, pat.regex.pattern)


router = routers.DefaultRouter()
router.register(r'idc', views.IDCViewSet)
router.register(r'org', views.OrganizationViewSet)
router.register(r'product_line', views.ProductLineViewSet)
router.register(r'application', views.ApplicationViewSet)
router.register(r'physical_machine', views.PhysicalMachineViewSet)
router.register(r'virtual_machine', views.VirtualMachineViewSet)
router.register(r'yun_machine', views.YunMachineViewSet)
router.register(r'network_device', views.NetworkDeviceViewSet)
router.register(r'elec_equipment', views.ElectronicEquipmentViewSet)
router.register(r'line', views.LineViewSet)
router.register(r'domain_name', views.DomainNameViewSet)
router.register(r'cdn', views.CDNViewSet)
router.register(r'cert', views.CertificateViewSet)
router.register(r'user_behavior', views.UserBehaviorViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^ecs/add/', views.add_instances),
    url(r'^retire/(?P<name>[^/]+)/$', views.get_model_retire),
    url(r'^dashboard/$', views.get_dashboard_metric),
]

if 'prod' not in os.environ.get('DJANGO_SETTINGS_MODULE'):
    print_url_pattern_names(urlpatterns)
