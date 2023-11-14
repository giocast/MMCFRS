from django.contrib import admin
from django.db.models.base import Model
from .models import *
# Register your models here.
import csv
from django.http import HttpResponse

from import_export.admin import ImportExportModelAdmin
from import_export.admin import ImportExportMixin
from django import forms


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


def export_as_csv_action(description="Export selected objects as CSV file", fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        opts = modeladmin.model._meta
        field_names = [field.name for field in opts.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(opts)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response


    export_as_csv.short_description = description
    return export_as_csv

# @admin.register(Personal_info)
class Personal_infoAdmin(ImportExportMixin,admin.ModelAdmin):
    list_display = ('id','session_id','created','age','gender','country','education')
    actions = [export_as_csv_action("CSV Export")]

    
class ProfileAdmin(ImportExportMixin,admin.ModelAdmin):
    list_display = (('id', 'person',
    'Height','Weight','RecipeWebUsage','HomeCook','CookingExp','EatingGoals',
    'Depression','PhysicalActivity','SleepHours','CookingTime'
    # 'image_link',
    ))
    actions = [export_as_csv_action("CSV Export")] 


class recipesAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (('id','Name','image_link','attractiveness', 'category'))
    actions = [export_as_csv_action("CSV Export")]

class Ghs_fkAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (('id','person','FK_9','FK_10','FK_11','FK_12','CS_9','CS_10','CS_11','CS_12','CS_13','CS_14'))
    actions = [export_as_csv_action("CSV Export")]
        
class recipesRatingAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (('id','person','recipes','created','rating','judging'))
    actions = [export_as_csv_action("CSV Export")]
    
    
    
    

admin.site.register(Personal_info, Personal_infoAdmin)



admin.site.register(Ghs_fk, Ghs_fkAdmin)



admin.site.register(recipes, recipesAdmin)
admin.site.register(recipesRating, recipesRatingAdmin)

admin.site.register(Profile, ProfileAdmin)