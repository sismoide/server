from django.contrib import admin

from map.models import Coordinates
from mobile_res.models import EmergencyType, ThreatType, ThreatReport, EmergencyReport, Report


class ReportAdmin(admin.ModelAdmin):
    readonly_fields = ('created_on',)


admin.site.register(EmergencyType)
admin.site.register(ThreatType)
admin.site.register(Report, ReportAdmin)

admin.site.register(ThreatReport)
admin.site.register(EmergencyReport)

admin.site.register(Coordinates)
