import django_filters
from django.db.models import Q
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    """
    Filter class for Customer model with various search options.
    """
    name = django_filters.CharFilter(lookup_expr='icontains', help_text="Case-insensitive partial match for customer name")
    email = django_filters.CharFilter(lookup_expr='icontains', help_text="Case-insensitive partial match for customer email")
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte', help_text="Filter customers created after this date")
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte', help_text="Filter customers created before this date")
    
    # Custom filter for phone number pattern
    phone_pattern = django_filters.CharFilter(method='filter_phone_pattern', help_text="Filter customers with phone numbers starting with specific pattern")
    
    class Meta:
        model = Customer
        fields = ['name', 'email', 'created_at__gte', 'created_at__lte', 'phone_pattern']
    
    def filter_phone_pattern(self, queryset, name, value):
        """
        Custom filter method to match phone numbers with specific patterns.
        """
        if value:
            return queryset.filter(phone__startswith=value)
        return queryset


class ProductFilter(django_filters.FilterSet):
    """
    Filter class for Product model with price and stock filtering.
    """
    name = django_filters.CharFilter(lookup_expr='icontains', help_text="Case-insensitive partial match for product name")
    price__gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte', help_text="Filter products with price greater than or equal to this value")
    price__lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte', help_text="Filter products with price less than or equal to this value")
    stock__gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte', help_text="Filter products with stock greater than or equal to this value")
    stock__lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte', help_text="Filter products with stock less than or equal to this value")
    stock = django_filters.NumberFilter(field_name='stock', lookup_expr='exact', help_text="Filter products with exact stock amount")
    
    # Custom filter for low stock
    low_stock = django_filters.BooleanFilter(method='filter_low_stock', help_text="Filter products with low stock (less than 10)")
    
    class Meta:
        model = Product
        fields = ['name', 'price__gte', 'price__lte', 'stock__gte', 'stock__lte', 'stock', 'low_stock']
    
    def filter_low_stock(self, queryset, name, value):
        """
        Custom filter method to find products with low stock.
        """
        if value:
            return queryset.filter(stock__lt=10)
        return queryset


class OrderFilter(django_filters.FilterSet):
    """
    Filter class for Order model with amount, date, and related field filtering.
    """
    total_amount__gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte', help_text="Filter orders with total amount greater than or equal to this value")
    total_amount__lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte', help_text="Filter orders with total amount less than or equal to this value")
    order_date__gte = django_filters.DateFilter(field_name='order_date', lookup_expr='gte', help_text="Filter orders created after this date")
    order_date__lte = django_filters.DateFilter(field_name='order_date', lookup_expr='lte', help_text="Filter orders created before this date")
    
    # Related field filters
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains', help_text="Filter orders by customer name (case-insensitive partial match)")
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains', help_text="Filter orders by product name (case-insensitive partial match)")
    
    # Custom filter for specific product ID
    product_id = django_filters.NumberFilter(method='filter_by_product_id', help_text="Filter orders that include a specific product ID")
    
    class Meta:
        model = Order
        fields = [
            'total_amount__gte', 'total_amount__lte', 
            'order_date__gte', 'order_date__lte',
            'customer_name', 'product_name', 'product_id'
        ]
    
    def filter_by_product_id(self, queryset, name, value):
        """
        Custom filter method to find orders containing a specific product.
        """
        if value:
            return queryset.filter(products__id=value).distinct()
        return queryset
