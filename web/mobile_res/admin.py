from django.contrib import admin

from mobile_res.models import EmergencyType, ThreatType, Report, ThreatReport, EmergencyReport, Coordinates


class ReportAdmin(admin.ModelAdmin):
    readonly_fields = ('created_on',)


admin.site.register(EmergencyType)
admin.site.register(ThreatType)
admin.site.register(Report, ReportAdmin)

admin.site.register(ThreatReport)
admin.site.register(EmergencyReport)

admin.site.register(Coordinates)
