from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter
from django.db.models import Q

from logistic.models import Product, Stock
from logistic.serializers import ProductSerializer, StockSerializer


class ProductFilter(FilterSet):
    search = CharFilter(field_name='products__title', lookup_expr='icontains') # или 'products__description'

    class Meta:
        model = Stock
        fields = ['search']


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title', 'description']


class StockViewSet(ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter