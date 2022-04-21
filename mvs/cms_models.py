from cms.extensions import PageExtension, extension_pool
from django.db import models


class ColorExtension(PageExtension):
    color = models.CharField(max_length=7)


extension_pool.register(ColorExtension)
