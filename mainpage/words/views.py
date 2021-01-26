from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.views import View
from .models import Wordset
from .forms import WordsetForm
from django.urls import reverse
from .writecsv import *
# Create your views here.

class WordsetCreate(CreateView):
    model = Wordset
    form_class = WordsetForm
    def get_success_url(self):
        return reverse('wordset')
    def get_context_data(self, **kwargs):
        queryset = Wordset.objects.all()
        return dict(super(WordsetCreate, self).get_context_data(**kwargs), queryset = queryset)

    def form_valid(self, form):
        if self.request.POST['action']=="add":
            form.instance.created_by=self.request.user
            form.instance.start=self.request.POST['start']
            form.instance.arrive=self.request.POST['arrive']
            form.instance.spec = form.cleaned_data['spec']
            form.instance.save()
            addword(form.instance.spec, form.instance.start, form.instance.arrive)
        return super().form_valid(form)

def WordsetDelete(request, pk):
    if (request.method == 'POST' and request.POST['action']=="del"):
        queryset = Wordset.objects.get(pk=pk)
        queryset.delete()
    return redirect('wordset')
