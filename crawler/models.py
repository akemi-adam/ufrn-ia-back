from django.db import models

class Collection(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(unique=True)
    last_scraping = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
