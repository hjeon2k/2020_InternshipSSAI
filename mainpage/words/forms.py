from .models import Wordset
from django import forms

class WordsetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WordsetForm, self).__init__(*args, **kwargs)
        self.fields['spec'].widget.attrs = {'class' : 'btn btn-light'}

    class Meta:
        model = Wordset
        fields = ['spec']
