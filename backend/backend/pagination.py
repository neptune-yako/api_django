from rest_framework.pagination import PageNumberPagination


class MyPaginator(PageNumberPagination):
    """
    自定义分页器
    """
    # 每页默认显示数量
    page_size = 10
    # 查询参数：自定义页码的参数名
    page_query_param = 'page'
    # 查询参数：自定义每页数量的参数名
    page_size_query_param = 'size'
    # 限制每页最大数量
    max_page_size = 40
