from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin

from django.db import models
from .apps.photos import PhotosFolder
import datetime
import random


class SideBox(CMSPlugin):
    title = models.CharField(max_length=50, default='')

    def __str__(self):
        return self.title


@plugin_pool.register_plugin
class SideBoxPlugin(CMSPluginBase):
    model = SideBox
    name = 'Side Box'
    render_template = "sidebox.html"
    cache = False
    allow_children = True


@plugin_pool.register_plugin
class PhotoPerDayPlugin(CMSPluginBase):
    name = 'Foto van de Dag'
    render_template = "photoperday.html"
    cache = False
    allow_children = False

    def render(self, context, instance, placeholder):
        context = super(PhotoPerDayPlugin, self).render(
            context, instance, placeholder)

        album = PhotosFolder(PhotosFolder.get_root(), '0. 25 jaar speule')
        day = int(datetime.datetime.now().timestamp() / 86400)
        random.seed(day)
        photo = random.choice(album.get_photos())
        context.update({
            'photo': photo,
        })
        return context
