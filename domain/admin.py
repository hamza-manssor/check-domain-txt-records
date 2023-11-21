from django.contrib import admin
from .models import DNSRecord  # Import your model

@admin.register(DNSRecord)
class DNSRecordAdmin(admin.ModelAdmin):
    list_display = ('domain', 'txt_record')
    search_fields = ('domain', 'txt_record')
