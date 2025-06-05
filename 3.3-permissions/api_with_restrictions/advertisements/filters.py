# -*- coding: utf-8 -*-
import django_filters as filters
from django_filters import DateFromToRangeFilter

from advertisements.models import Advertisement


class AdvertisementFilter(filters.FilterSet):
    created_at = DateFromToRangeFilter()

    class Meta:
        model = Advertisement
        fields = {
            'created_at': ['range'],
            'status': ['exact'],
            'is_favorite': ['exact']
        }