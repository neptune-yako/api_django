# 定义测试记录查询参数实现使用的过滤器
from django_filters import rest_framework as filters
from .models import Record


class RecordFilter(filters.FilterSet):
    """测试记录过虑的模型、继承FilterSet"""
    # 指定orm模型中过滤字段
    project = filters.NumberFilter(field_name="plan__project")

    class Meta:
        # 指定model
        model = Record
        # 指定过滤字段，列表类型或者字典类型
        fields = ['project', 'env', 'plan']
