
import os
import shutil

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.http import FileResponse, HttpResponseForbidden, HttpResponse, HttpResponseRedirect
from django.views import View
from django.urls import reverse
from django.conf import settings

from .models import Document
from .forms import *
from .trans import *
from .stt import *
from .monowav import *
from .subenc import *
from .delay import *
import base64
from scipy.io import wavfile
from .deleteoldfile import delete_old_files
from .filenumbering import filenumber

from django.core.files.storage import default_storage
from django.contrib.auth.models import User, Group
from django.contrib import auth
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

'''
class DocumentList(LoginRequiredMixin, ListView):
    model = Document

    def get_queryset(self):
        queryset = Document.objects.all()
        user = self.request.user

        if not user.is_superuser:
            queryset = queryset.filter(
                created_by=user
            )

        return queryset
'''

class UserList(LoginRequiredMixin, ListView):
    model = User

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.all()
        if not user.is_superuser:
            queryset = None
        return queryset

def UserApprove(request, name):
    if (request.method=='POST' and request.POST['action']=='approve'):
        query = User.objects.get(username=name)
        group = Group.objects.get(name='faculty')
        if query.groups.filter(name='faculty').exists():
            query.groups.remove(group)
        else:
            query.groups.add(group)
            message = render_to_string('accounts/faculty_email.html', {
                'user' : query,
            })
            mail_title = "SNU Lecture Subtitle : Your account has been approved"
            mail_to = query.username + '@snu.ac.kr'
            email = EmailMessage(mail_title, message, to=[mail_to])
            email.send()

    return redirect("userlist")

def UserDelete(request, name):
    if (request.method=='POST' and request.POST['action']=='delete'):
        query = User.objects.get(username=name)
        documents = Document.objects.filter(created_by=query)
        for document in documents:
            document.delete()
        query.delete()
    return redirect("userlist")


def searchline(getline):
    line = getline.replace("\n", "")
    l = len(line)
    flag = False;
    for i in range(l):
        if (line[i] > '9' or line[i] < '0') and line[i]!=':' and line[i]!=',' and line[i]!='-' and  line[i]!='>' and line[i]!=' ':
            flag = True
            break
    return flag

class DocumentCreate(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm

    def get_context_data(self, **kwargs):
        queryset = Document.objects.all()
        user = self.request.user
        now = timezone.now()
        for query in queryset:
            if query.created_at < timezone.now() + datetime.timedelta(days=-6):
                query.deletewarn = True
                query.save()
            if query.created_at < timezone.now() + datetime.timedelta(days=-7):
                query.delete()
        queryset = Document.objects.all()
        if not user.is_superuser:
            queryset = queryset.filter(created_by=user)
        delete_old_files(settings.MEDIA_ROOT)
        return dict(
            super(DocumentCreate, self).get_context_data(**kwargs),
            queryset=queryset
        )

    def get_success_url(self):
        return reverse('home')

    def handle_uploaded_file(self, f, slan, alan, spec):
        ofilename, extension = os.path.splitext(f.name)
        ofilename = self.request.user.username + '_' + ofilename
        filename, extension = os.path.splitext(filenumber('video_'+ofilename, extension, settings.MEDIA_ROOT))
        filename = filename[6:]
        shutil.move(settings.MEDIA_ROOT+'/'+f.name, settings.MEDIA_ROOT+'/'+filename+extension)
        p, ext = settings.MEDIA_ROOT + '/' + filename, extension
        if os.path.isfile(settings.MEDIA_ROOT + '/' + f.name):
            os.remove(settings.MEDIA_ROOT + '/' + f.name)
        if not getWav(p + ext, filename) : return False
        path = p + '.wav'
        sample_rate_audio = wavfile.read(path)[0]
        upload_blob('snu_ensub', path, filename + '.wav')
        os.remove(path)
        audio = speech.types.RecognitionAudio(uri="gs://snu_ensub/" + filename + ".wav")

        rel_bf = filename + '_original.txt'
        full_bf = settings.MEDIA_ROOT + '/' + rel_bf
        rel_af = filename + '_subtitle.srt'
        full_af = settings.MEDIA_ROOT + "/" +  rel_af
        rel_f0 = filename + '_script.txt'
        full_f0 = settings.MEDIA_ROOT + '/' + rel_f0

        fout_bf = open(full_bf, 'w', encoding = 'UTF-8')
        f0 = open(full_f0, 'w', encoding = 'UTF-8')
        
        subtitle, script = stt(sample_rate_audio, audio, slan)

        fout_bf.write(subtitle)
        f0.write(script)
        fout_bf.close()
        f0.close()

        fin = open(full_bf, 'r', encoding = 'UTF-8')
        fout_af = open(full_af, 'w', encoding = 'UTF-8')
        while True:
            line = fin.readline()
            if not line: break
            if searchline(line):
                fout_af.write(translate_line_glossary(line, slan, alan, spec))
            else: fout_af.write(line)
        fin.close()
        fout_af.close()
        
        if os.path.isfile(settings.MEDIA_ROOT + '/' + 'video_'+filename + ext):
            video_bf = settings.MEDIA_ROOT + '/' + 'video_'+filename + ext
            video_af = settings.MEDIA_ROOT + '/' + 'sub_video_'+filename + ext
            shutil.copy(video_bf, video_af)
            #encodesub(video_bf, full_af, video_af)
            return rel_af, rel_f0, rel_bf, 'sub_video_'+filename+ext
        else:
            return rel_af, rel_f0, rel_bf, None

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        f = form.cleaned_data['file']
        form.instance.label = f.name
        f.name = f.name.replace(" ", "_")
        slan = 'ko-KR'
        alan = 'en'
        spec = form.cleaned_data['spec']
        form.instance.predict = timezone.now()
        form.instance.save()
        fullpath = settings.MEDIA_ROOT + '/' + f.name
        filename, extension = os.path.splitext(f.name)
        form.instance.predict= timezone.now() + datetime.timedelta(minutes=stt_translate_delay(fullpath))
        a = str(form.instance.predict)[0:20].replace(" ", "/")
        b = "Estimated End Time___"
        b = b.replace(" ", "-")
        form.instance.predictstr = b + a
        form.instance.save()
        if extension=='.mp4' or extension=='.mov' or extension=='.avi' or extension=='.MP4' or extension=='.MOV' or extension=='.AVI':
            form.instance.video=fullpath
            form.instance.save()

        if f:
            relative_path, tmp1, tmp2, tmp3 = self.handle_uploaded_file(f, slan, alan, spec)
            if (relative_path) :
                form.instance.file, form.instance.file0, form.instance.file1, form.instance.video = relative_path, tmp1, tmp2, tmp3
                f = open(settings.MEDIA_ROOT + '/' + relative_path)
                s = f.read()
                form.instance.before = s
                f.close()
                f = open(settings.MEDIA_ROOT + '/' + tmp2)
                s = f.read()
                form.instance.after = s
                f.close()
            form.instance.completed = True
            form.instance.save()
        return super().form_valid(form)

class DocumentDownload(View):
    def get(self, request, relative_path):
        if Document.objects.filter(file=relative_path).first():
            document = Document.objects.get(file=relative_path)
        elif Document.objects.filter(file0=relative_path).first():
            document = Document.objects.get(file0=relative_path)
        elif Document.objects.filter(video=relative_path).first():
            document = Document.objects.get(video=relative_path)
        if not request.user.is_superuser and document.created_by != request.user:
            return HttpResponseForbidden()
        absolute_path = '{}/{}'.format(settings.MEDIA_ROOT, relative_path)
        if os.path.isfile(absolute_path) : 
            response = FileResponse(open(absolute_path, 'rb'), as_attachment=True)
            return response

def DocumentDelete(request, pk):
    if request.method == 'POST':
        queryset = Document.objects.get(pk=pk)
        queryset.delete()
    return redirect("home")


def AudioEdit(request, relative_path):
    document = Document.objects.get(file=relative_path)
    abpath_bf = '{}/{}'.format(settings.MEDIA_ROOT, document.file1.name)
    abpath_af = '{}/{}'.format(settings.MEDIA_ROOT, relative_path)
    fbf = open(abpath_bf, 'r')
    faf = open(abpath_af, 'r')
    sbf = fbf.read()
    saf = faf.read()
    fbf.close()
    faf.close()
    
    if request.method == 'POST':
        if request.POST['action']=="save":
            fbf = open(abpath_bf, 'w', encoding='utf-8')
            faf = open(abpath_af, 'w', encoding='utf-8')
            fbf.write(request.POST.get('before'))
            faf.write(request.POST.get('after'))
            fbf.close()
            faf.close()
            document.created_at = timezone.now()
            document.save()

            fbf = open(abpath_bf, 'r', encoding='utf-8')
            abpath_s = '{}/{}'.format(settings.MEDIA_ROOT, document.file0.name)
            fscript = open(abpath_s, 'w', encoding='utf-8')
            while True:
                line = fbf.readline()
                if not line: break;
                if searchline(line):
                    fscript.write(line.replace("\n", " "))
            fscript.close()
            fbf.close()

            return HttpResponseRedirect(request.path_info)

        elif request.POST['action']=="trans":
            fbf = open(abpath_bf, 'w', encoding='UTF-8')
            fbf.write(request.POST.get("before"))
            fbf.close()
            document.created_at = timezone.now()
            document.save()

            fbf = open(abpath_bf, 'r', encoding = 'UTF-8')
            faf = open(abpath_af, 'w', encoding = 'UTF-8')
            abpath_s = '{}/{}'.format(settings.MEDIA_ROOT, document.file0.name)
            fscript = open(abpath_s, 'w', encoding='utf-8')
            while True:
                line = fbf.readline()
                if not line: break
                if searchline(line):
                    faf.write(translate_line_glossary(line, 'ko-KR', 'en', document.spec))
                    fscript.write(line.replace("\n", " "))
                else: faf.write(line)
            fbf.close()
            faf.close()
            fscript.close()

            return HttpResponseRedirect(request.path_info)

    return render(request, 'core/edit.html', {'bf' : sbf, 'af' : saf, 'video' : None})

def VideoEdit(request, relative_path):
    document = Document.objects.get(file=relative_path)
    abpath_bf = '{}/{}'.format(settings.MEDIA_ROOT, document.file1.name)
    abpath_af = '{}/{}'.format(settings.MEDIA_ROOT, relative_path)
    fbf = open(abpath_bf, 'r')
    faf = open(abpath_af, 'r')
    sbf = fbf.read()
    saf = faf.read()
    fbf.close()
    faf.close()
    
    if request.method == 'POST':
        if request.POST['action']=="save":
            fbf = open(abpath_bf, 'w', encoding='utf-8')
            faf = open(abpath_af, 'w', encoding='utf-8')
            fbf.write(request.POST.get('before'))
            faf.write(request.POST.get('after'))
            fbf.close()
            faf.close()
            document.created_at = timezone.now()
            document.save()

            fbf = open(abpath_bf, 'r', encoding='utf-8')
            abpath_s = '{}/{}'.format(settings.MEDIA_ROOT, document.file0.name)
            fscript = open(abpath_s, 'w', encoding='utf-8')
            while True:
                line = fbf.readline()
                if not line: break;
                if searchline(line):
                    fscript.write(line.replace("\n", " "))
            fscript.close()
            fbf.close()

            return HttpResponseRedirect(request.path_info)

        elif request.POST['action']=="trans":
            fbf = open(abpath_bf, 'w', encoding='UTF-8')
            fbf.write(request.POST.get("before"))
            fbf.close()
            document.created_at = timezone.now()
            document.save()

            fbf = open(abpath_bf, 'r', encoding = 'UTF-8')
            faf = open(abpath_af, 'w', encoding = 'UTF-8')
            abpath_s = '{}/{}'.format(settings.MEDIA_ROOT, document.file0.name)
            fscript = open(abpath_s, 'w', encoding='utf-8')
            while True:
                line = fbf.readline()
                if not line: break
                if searchline(line):
                    faf.write(translate_line_glossary(line, 'ko-KR', 'en', document.spec))
                    fscript.write(line.replace("\n", " "))
                else: faf.write(line)
            fbf.close()
            faf.close()
            fscript.close()

            return HttpResponseRedirect(request.path_info)

        elif request.POST["action"]=="render":
            document.completed=False
            document.encoded = True
            document.created_at = timezone.now()
            document.predict = timezone.now() + datetime.timedelta(minutes= encode_delay(document.video.size))
            a = str(document.predict)[0:20].replace(" ", "/")
            b = "Estimated End Time___"
            b = b.replace(" ", "-")
            document.predictstr = b + a
            print(document.predictstr)
            document.save()
            faf = open(abpath_af, 'w', encoding='utf-8')
            faf.write(request.POST['after'])
            faf.close()   
            video_bf = '{}/{}'.format(settings.MEDIA_ROOT, document.video.name[4:])
            video_af = '{}/{}'.format(settings.MEDIA_ROOT, document.video.name)
            encodesub(video_bf, abpath_af, video_af)
            document.completed=True
            document.save()
            return HttpResponseRedirect(request.path_info)
    
    return render(request, 'core/edit.html', {'bf' : sbf, 'af' : saf, 'video' : 'Yes'})



