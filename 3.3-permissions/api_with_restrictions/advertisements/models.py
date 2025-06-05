# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User 

class AdvertisementStatusChoices(models.TextChoices):

    OPEN = "OPEN", "Открыто"
    CLOSED = "CLOSED", "Закрыто"
    DRAFT = "DRAFT", "Черновик" 


class Advertisement(models.Model):

    title = models.TextField()
    description = models.TextField(default='')
    status = models.CharField(
        max_length=10, 
        choices=AdvertisementStatusChoices.choices,
        default=AdvertisementStatusChoices.OPEN
    )
    creator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    is_favorite = models.BooleanField(default=False)  

    def __str__(self):
        return self.title