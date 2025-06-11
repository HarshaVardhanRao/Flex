from django.contrib import admin
from .models import *

admin.site.register(student)
admin.site.register(LeetCode)
admin.site.register(Certificate)
admin.site.register(Projects)
admin.site.register(Faculty)
admin.site.register(publications)
admin.site.register(certifications)
admin.site.register(Technology)
admin.site.register(FillOutForm)
admin.site.register(FillOutResponse)
admin.site.register(FillOutField)

@admin.register(CoordinatorRole)
class CoordinatorRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    filter_horizontal = ('faculties', 'providers')

admin.site.register(Provider)
