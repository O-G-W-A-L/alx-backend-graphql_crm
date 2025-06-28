import django_filters
from django.db.models import Q
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    name_icontains = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    email_icontains = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    created_at_gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    phone_pattern = django_filters.CharFilter(method='filter_phone_pattern')

    order_by = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('email', 'email'),
            ('created_at', 'created_at'),
        ),
        field_labels={
            'name': 'Name',
            'email': 'Email',
            'created_at': 'Created At',
        },
        label='Sort by'
    )

    def filter_phone_pattern(self, queryset, name, value):
        # Example: filter phone numbers starting with +1
        return queryset.filter(phone__startswith=value)

    class Meta:
        model = Customer
        fields = [
            'name_icontains', 'email_icontains',
            'created_at_gte', 'created_at_lte',
            'phone_pattern',
        ]


class ProductFilter(django_filters.FilterSet):
    name_icontains = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    price_gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    stock_gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')

    order_by = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('price', 'price'),
            ('stock', 'stock'),
        ),
        field_labels={
            'name': 'Name',
            'price': 'Price',
            'stock': 'Stock',
        },
        label='Sort by'
    )

    class Meta:
        model = Product
        fields = [
            'name_icontains', 'price_gte', 'price_lte',
            'stock_gte', 'stock_lte',
        ]


class OrderFilter(django_filters.FilterSet):
    total_amount_gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    order_date_gte = django_filters.DateFilter(field_name='order_date', lookup_expr='gte')
    order_date_lte = django_filters.DateFilter(field_name='order_date', lookup_expr='lte')
    customer_name_icontains = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name_icontains = django_filters.CharFilter(method='filter_by_product_name')
    product_id = django_filters.NumberFilter(method='filter_by_product_id')

    order_by = django_filters.OrderingFilter(
        fields=(
            ('total_amount', 'total_amount'),
            ('order_date', 'order_date'),
        ),
        field_labels={
            'total_amount': 'Total Amount',
            'order_date': 'Order Date',
        },
        label='Sort by'
    )

    def filter_by_product_name(self, queryset, name, value):
        return queryset.filter(products__name__icontains=value).distinct()

    def filter_by_product_id(self, queryset, name, value):
        return queryset.filter(products__id=value).distinct()

    class Meta:
        model = Order
        fields = [
            'total_amount_gte', 'total_amount_lte',
            'order_date_gte', 'order_date_lte',
            'customer_name_icontains', 'product_name_icontains', 'product_id',
        ]
