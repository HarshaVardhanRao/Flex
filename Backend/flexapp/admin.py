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
    list_display = ('name', 'description', 'can_view_certificates', 'can_view_publications', 'can_view_projects', 'can_view_placement')
    list_filter = ('can_view_certificates', 'can_view_publications', 'can_view_projects', 'can_view_placement')
    filter_horizontal = ('faculties', 'providers')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Permissions', {
            'fields': ('can_view_certificates', 'can_view_publications', 'can_view_projects', 'can_view_placement')
        }),
        ('Associations', {
            'fields': ('faculties', 'providers')
        }),
    )

admin.site.register(Provider)
