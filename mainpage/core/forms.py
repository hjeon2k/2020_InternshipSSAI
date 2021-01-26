from .models import Document
from django import forms 
from django.core.exceptions import ValidationError

class DocumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs = {'class' : 'btn btn-light'}
        self.fields['spec'].widget.attrs = {'class' : 'btn btn-light'}

    class Meta:
        model = Document
        fields = ['spec', 'file'] #, 'before', 'after']
        help_texts = {'file':'Maximum_file_size_500MB'}
        #widgets = {'before': forms.HiddenInput, 'after' : forms.HiddenInput}
