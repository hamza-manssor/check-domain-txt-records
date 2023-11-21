from django.db import models

class DNSRecord(models.Model):
    domain = models.CharField(max_length=255)
    txt_record = models.TextField()

    def __str__(self):
        return f"{self.domain}: {self.txt_record}"
