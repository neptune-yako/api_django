from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import Handle, Bug


class HandleSerializer(serializers.ModelSerializer):
    """bug处理记录的序列化器"""

    class Meta:
        model = Handle
        fields = '__all__'


class BugSerializer(serializers.ModelSerializer):
    """bug管理的序列化器"""
    interface_url = serializers.StringRelatedField(source='interface.url', read_only=True)
    handle = HandleSerializer(many=True, source="handle_set", read_only=True)

    class Meta:
        model = Bug
        fields = '__all__'


class BugListSerializer(serializers.ModelSerializer):
    """bug管理的序列化器"""
    interface_url = serializers.StringRelatedField(source='interface.url', read_only=True)
    pro_name = serializers.StringRelatedField(read_only=True, source='project.name')
    handle_time = serializers.SerializerMethodField()

    @extend_schema_field(serializers.DateTimeField(allow_null=True))
    def get_handle_time(self, obj):
        handle_time = obj.handle_set.order_by('-update_time').first()
        return handle_time.update_time

    class Meta:
        model = Bug
        fields = '__all__'
