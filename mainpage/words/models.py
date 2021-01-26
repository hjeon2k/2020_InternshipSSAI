from django.db import models
from django.contrib.auth.models  import User
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.conf import settings

from .writecsv import *

# Create your models here.

SPEC_CHOICES = (('Engineering', 'Engineering'), ('Science', 'Science'), ('Arts', 'Arts'), 
                ('Education', 'Education'), ('Humanities', 'Humanities'))

class Wordset(models.Model):
    start = models.CharField(max_length=200)
    arrive = models.CharField(max_length=200)
    spec = models.CharField(max_length=20, choices=SPEC_CHOICES, default='Engineering')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(default=timezone.now)
    
    slug = models.SlugField(max_length=255, editable=False)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.start)
        return super(Wordset, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        delword(self.spec, self.start, self.arrive)
        super(Wordset, self).delete(*args, **kwargs)
