
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.template.defaultfilters import slugify
import os
from django.conf import settings
from django.core.exceptions import ValidationError
from .validator import validate_file_extension

STR_CHOICES = [('ko-KR', 'Korean'), ('en-US', 'English')]
ARR_CHOICES = [('en', 'English'), ('ko', 'Korean'), ('zh', 'Chinese'), ('fr', 'French'),
        ('es', 'Spanish'), ('kk', 'Kazakh'),]
SPEC_CHOICES = (('Engineering', 'Engineering'), ('Science', 'Science'), ('Arts', 'Arts'), 
                ('Education', 'Education'), ('Humanities', 'Humanities'))

class Document(models.Model):
    label = models.CharField(max_length=200)
    file = models.FileField(validators=[validate_file_extension])
    file0 = models.FileField()
    file1 = models.FileField()
    video = models.FileField()
    spec = models.CharField(max_length=20, choices=SPEC_CHOICES, default='Engineering')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(max_length=255, editable=False)
    
    start = models.CharField(max_length=10, choices=STR_CHOICES, default='ko-KO')
    arrive = models.CharField(max_length=10, choices=ARR_CHOICES, default='en')

    completed = models.BooleanField(default=False)
    encoded = models.BooleanField(default=False)
    predict = models.DateTimeField()
    predictstr = models.TextField()

    deletewarn = models.BooleanField(default=False)

    #before = models.TextField()
    #after = models.TextField()

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.label)

        return super(Document, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        #for f in os.listdir(settings.MEDIA_ROOT):
            #if any(x in f for x in self.file.name):
                #os.remove(f)
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, self.file.name)):
                os.remove(os.path.join(settings.MEDIA_ROOT, self.file.name))
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, self.file0.name)):
                os.remove(os.path.join(settings.MEDIA_ROOT, self.file0.name))
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, self.file1.name)):
                os.remove(os.path.join(settings.MEDIA_ROOT, self.file1.name))
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, self.video.name[4:])):
                os.remove(os.path.join(settings.MEDIA_ROOT, self.video.name[4:]))
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, self.video.name)):
                os.remove(os.path.join(settings.MEDIA_ROOT, self.video.name))
        super(Document, self).delete(*args, **kwargs)
