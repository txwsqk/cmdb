# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from django.core.cache import cache


class CmdbConfig(AppConfig):
    name = 'cmdb'

    @classmethod
    @receiver(post_save)
    @receiver(post_delete)
    def purge_cache(sender, **kwargs):
        cache.clear()

    def ready(self):
        CmdbConfig.purge_cache()

