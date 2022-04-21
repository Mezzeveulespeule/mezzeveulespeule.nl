from cms.extensions import PageExtensionAdmin
from django.contrib import admin
from django.forms import ModelForm
from django.forms.widgets import TextInput
from import_export import resources, fields
from import_export.admin import ExportMixin
from import_export.widgets import ManyToManyWidget

from .cms_models import ColorExtension
from .models import Dag, Taak, Aanmelding, Vrijwilliger


class AanmeldingResource(resources.ModelResource):
    class Meta:
        model = Aanmelding


class AanmeldingAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = AanmeldingResource


class VrijwilligerResource(resources.ModelResource):
    taken = fields.Field(attribute='taken', widget=ManyToManyWidget(Taak, field='naam', separator=',\n'))
    dagen = fields.Field(attribute='dagen', widget=ManyToManyWidget(Dag, field='naam', separator=',\n'))

    class Meta:
        model = Vrijwilliger


class VrijwilligerAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = VrijwilligerResource


class ColorExtensionForm(ModelForm):
    class Meta:
        model = ColorExtension
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color', 'style': 'width: 100px; height: 100px;'}),
        }


class ColorExtensionAdmin(PageExtensionAdmin):
    form = ColorExtensionForm


admin.site.register(ColorExtension, ColorExtensionAdmin)

admin.site.register(Dag)
admin.site.register(Taak)
admin.site.register(Aanmelding, AanmeldingAdmin)
admin.site.register(Vrijwilliger, VrijwilligerAdmin)
