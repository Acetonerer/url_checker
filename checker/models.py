from django.db import models


class LinkCheckResult(models.Model):
    url = models.URLField(unique=True)
    results = models.JSONField() 
    checked_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.url
