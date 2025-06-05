# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', 'is_favorite')
        read_only_fields = ('creator', 'created_at')

    def validate(self, data):

        user = self.context['request'].user
        if user.is_authenticated:
            open_ads_count = Advertisement.objects.filter(creator=user, status='OPEN').count()
            #  Проверяем, что если это новое объявление или статус меняется на "OPEN", то не превышен ли лимит
            if (self.instance is None or data.get('status') == 'OPEN') and open_ads_count >= 10 and data.get('status', 'OPEN') == 'OPEN':
                raise serializers.ValidationError("У вас уже есть 10 открытых объявлений.")

            #  Проверяем, что автор не добавляет свое объявление в избранное
            if self.instance and data.get('is_favorite') and self.instance.creator == user:
                raise serializers.ValidationError("Вы не можете добавлять свои объявления в избранное.")

        return data

  