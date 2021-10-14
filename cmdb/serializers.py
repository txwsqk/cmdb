from rest_framework import serializers

from .models import UserBehavior, Organization, Application, IDC, \
    Line, PhysicalMachine, VirtualMachine, \
    YunMachine, NetworkDevice, DomainName, CDN, Certificate, ElectronicEquipment, \
    ProductLine


class UserBehaviorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserBehavior
        fields = '__all__'


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class ProductLineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProductLine
        fields = '__all__'


class ApplicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'


class IDCSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IDC
        fields = '__all__'


class LineSerializer(serializers.HyperlinkedModelSerializer):
    src_idc = serializers.SlugRelatedField(read_only=False,
                                           slug_field='name',
                                           queryset=IDC.objects.all())
    dst_idc = serializers.SlugRelatedField(read_only=False,
                                           slug_field='name',
                                           queryset=IDC.objects.all())

    class Meta:
        model = Line
        fields = '__all__'


class PhysicalMachineSerializer(serializers.HyperlinkedModelSerializer):
    idc = serializers.SlugRelatedField(read_only=False,
                                       slug_field='name',
                                       queryset=IDC.objects.all())

    application = serializers.SlugRelatedField(read_only=False,
                                               slug_field='name',
                                               queryset=Application.objects.all())

    business_path = serializers.CharField(source='application.business_path',
                                          read_only=True)
    product_line = serializers.CharField(source='application.product_line',
                                         read_only=True)

    class Meta:
        model = PhysicalMachine
        fields = '__all__'


class VirtualMachineSerializer(serializers.HyperlinkedModelSerializer):
    physical_machine = serializers.SlugRelatedField(read_only=False,
                                                    slug_field='name',
                                                    queryset=PhysicalMachine.objects.filter(
                                                        name__startswith='kvmcluster'))

    application = serializers.SlugRelatedField(read_only=False,
                                               slug_field='name',
                                               queryset=Application.objects.all())

    business_path = serializers.CharField(source='application.business_path',
                                          read_only=True)
    product_line = serializers.CharField(source='application.product_line',
                                         read_only=True)

    class Meta:
        model = VirtualMachine
        fields = '__all__'


class YunMachineSerializer(serializers.HyperlinkedModelSerializer):
    idc = serializers.SlugRelatedField(read_only=False,
                                       slug_field='name',
                                       queryset=IDC.objects.all())

    application = serializers.SlugRelatedField(read_only=False,
                                               slug_field='name',
                                               queryset=Application.objects.all())

    business_path = serializers.CharField(source='application.business_path',
                                          read_only=True)
    product_line = serializers.CharField(source='application.product_line',
                                         read_only=True)

    class Meta:
        model = YunMachine
        fields = '__all__'


class NetworkDeviceSerializer(serializers.HyperlinkedModelSerializer):
    idc = serializers.SlugRelatedField(read_only=False,
                                       slug_field='name',
                                       queryset=IDC.objects.all())

    application = serializers.SlugRelatedField(read_only=False,
                                               slug_field='name',
                                               queryset=Application.objects.all())

    business_path = serializers.CharField(source='application.business_path',
                                          read_only=True)
    product_line = serializers.CharField(source='application.product_line',
                                         read_only=True)

    class Meta:
        model = NetworkDevice
        fields = '__all__'


class DomainNameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DomainName
        fields = '__all__'


class CDNSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CDN
        fields = '__all__'


class CertificateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'


class ElectronicEquipmentSerializer(serializers.HyperlinkedModelSerializer):
    business_path = serializers.SlugRelatedField(read_only=False,
                                                 slug_field='name',
                                                 queryset=Organization.objects.all())

    class Meta:
        model = ElectronicEquipment
        fields = '__all__'
