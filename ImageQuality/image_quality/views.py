from select import select
from django.forms import formset_factory
from django.db.models import Count
# import datetime
from datetime import datetime 
import pandas as pd
from random import choice, sample
import random
from sys import prefix
from django import forms
from django.db import reset_queries
from django.forms.models import ModelForm
from django.http import request
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from pandas.core.indexes import category
import itertools
from .forms import Personal_infoForm, recipesRatingForm, Ghs_fkForm, ProfileForm, ChoiceEvaluationForm
from django.db.models import Q

from .models import  Personal_info, recipes, recipesRating, Ghs_fk, Profile, EvaluateChoices
# from .app import *
# Create your views here.
# person_id = 0
import string
import random
import re
from django.core.cache import cache
# Create your views here.


def home(request):
    request.session['person_id'] = 0
    
    # views = ["rate_sate", "rate_paste","rate_snacks","rate_dissert"]
    # shuffle`views`
    # index = 0 // 0-3
    # views[index]
    #prolific_id = , msg)
    #prolific_id = str(prolific_id.group(1))
    full_url = request.get_full_path()
    #request.GET['PROLIFIC_PID']
    # print('Full',request.get_full_path())
    #print(full_url)
    if 'PROLIFIC_PID' in full_url:
        prolific_id = re.search("PROLIFIC_PID=(.*?)&STUDY_ID",full_url)
        request.session['prolific_id'] = str(prolific_id.group(1))
        #print("----------",prolific_id.group(1))
    else:
        request.session['prolific_id'] = '000'
    return render(request, 'image_quality/homes.html')

        # index++
        
def personal_info(request):
    user_selected = Personal_info.objects.filter(id = request.session['person_id'])
    if user_selected:
        Personal_info.objects.filter(id=request.session['person_id']).delete()
    if request.method == 'POST':
        personl_info = Personal_infoForm(request.POST)
        if personl_info.is_valid():
            answer = personl_info.save(commit=False)
            
            rd_str =''.join(random.choice(string.ascii_lowercase) for _ in range(5))
            time_now = datetime.now().strftime('%H%M%S')
            gene_session = 'dars'+time_now +'_'+str(answer.id)+rd_str
            personl_info.instance.session_id = gene_session

            answer = personl_info.save(commit=True)
            
            request.session['person_id'] = answer.id
            gene_session = 'dars'+time_now +'_'+str(answer.id)+rd_str
            personl_info.instance.session_id = request.session['prolific_id']
            
            request.session['session_id'] = gene_session
            answer = personl_info.save(commit=True)
            request.session['n'] = 0

            request.session['person_id'] = answer.id
            # return redirect('image_quality:rate_salad')
            return redirect('image_quality:ghs_fk')
    else:
        personl_info = Personal_infoForm()
    return render(request, 'image_quality/personal_info.html', context={'form': personl_info})


def ghs_fk(request):
    user_selected = Ghs_fk.objects.filter(id = request.session['person_id'])
    if user_selected:
        ghs_fk.objects.filter(id=request.session['person_id']).delete()
    if request.method == 'POST':
        ghs_fk_form = Ghs_fkForm(request.POST)
        #print('------- Here')
        if ghs_fk_form.is_valid():
            answer = ghs_fk_form.save(commit=False)

            rd_str = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
            time_now = datetime.now().strftime('%H%M%S')
            gene_session = 'dars' +  time_now + '_' + str(answer.id) + rd_str
            ghs_fk_form.instance.session_id = gene_session
            ghs_fk_form.instance.person_id = request.session['person_id']
            #print(';;;;;;;;;;;here')
            answer = ghs_fk_form.save(commit = True)

            #request.session['person_id'] = answer.id
            return redirect('image_quality:profileBuilder')
        else:
            print('not valid')
    else:
        ghs_fk_form = Ghs_fkForm()
    return render(request, 'image_quality/Personal_knowledge.html', context={'form':ghs_fk_form})


def profileBuilder(request):
    user_selected = Profile.objects.filter(person_id = request.session['person_id'])
    if user_selected:
        Profile.objects.filter(person_id=request.session['person_id']).delete()
  
    if request.method == 'POST':
        profile_Form = ProfileForm(request.POST)
        person = request.session['person_id']
        ProfileM = Profile()
        if profile_Form.is_valid():
            # print("-----------here we are")
            # ChoiceEvaltion.person = request.session['person_id']
            profile_ = profile_Form.save(commit=False)
            profile_.person_id = person
            # ChoiceEvaltion.person_id = profile_form.foriengkey
            # profile_.session_id = request.session['prolific_id']
            profile_.save()
            return redirect('image_quality:rate_recipes')
    else:
         profile_Form = ProfileForm()
    return render(request, 'image_quality/ProfileBuilder.html', context={'form': profile_Form})








def rate_recipes(request):
    # print( request.session['n'])
    
    # rated = recipesRating.objects.all().order_by('?')
    # notyetrated = recipes.objects.exclude(id__in = rated)
    # notyetrated_id = recipes.objects.exclude(id__in = rated).values_list('id')
    
    user_selected  = recipesRating.objects.filter(person_id= request.session['person_id'])
    if request.method == "POST":    
        S1 = recipesRatingForm(request.POST, prefix='S1')
        S2 = recipesRatingForm(request.POST,prefix='S2')
        S3 = recipesRatingForm(request.POST,prefix='S3')
        S4 = recipesRatingForm(request.POST,prefix='S4')
        S5 = recipesRatingForm(request.POST,prefix='S5')
        S6 = recipesRatingForm(request.POST,prefix='S6')

        
        S_r1 = recipesRating()
        S_r2 = recipesRating()
        S_r3 = recipesRating()
        S_r4 = recipesRating()
        S_r5 = recipesRating()
        S_r6 = recipesRating()

        
        if S1.is_valid() and S2.is_valid() and S3.is_valid() and S4.is_valid() and  S5.is_valid() and S6.is_valid(): 
            person = Personal_info.objects.get(id=request.session['person_id'])
            
            S_r1.person = S_r2.person =S_r3.person=S_r4.person=S_r5.person= S_r6.person=person
            
            # S = cache.get('S')
            S = request.session['data']
            # print('----',S)

            S_r1.recipes_id = S[0][0]
            S_r1.rating = S1.cleaned_data.get('rating')
            S_r1.judging = S1.cleaned_data.get('judging')
            S_r1.save()
            
            S_r2.recipes_id = S[1][0]
            S_r2.rating = S2.cleaned_data.get('rating')
            S_r2.judging = S2.cleaned_data.get('judging')
            S_r2.save()       
                    
            S_r3.recipes_id = S[2][0]
            S_r3.rating = S3.cleaned_data.get('rating')
            S_r3.judging = S3.cleaned_data.get('judging')    
            S_r3.save()
            
            
            S_r4.recipes_id = S[3][0]
            S_r4.rating = S4.cleaned_data.get('rating')
            S_r4.judging = S4.cleaned_data.get('judging')
            S_r4.save()
                    
            S_r5.recipes_id = S[4][0]
            S_r5.rating = S5.cleaned_data.get('rating')
            S_r5.judging = S5.cleaned_data.get('judging')
            S_r5.save()

            S_r6.recipes_id = S[5][0]
            S_r6.rating = S6.cleaned_data.get('rating')
            S_r6.judging = S6.cleaned_data.get('judging')
            S_r6.save()
            
            # print('#######-N-####',request.session['n'])
            if request.session['n'] == 1:
                return redirect('image_quality:choice_evaluation')
                # user_selected  = recipesRating.objects.filter(person_id= request.session['person_id'])
    
            else :
                request.session['n'] += 1
                return redirect('image_quality:rate_recipes')
                # user_selected  = recipesRating.objects.filter(person_id= request.session['person_id'])
    
        else: 
            print('--------->>not valid')
        
    else:
        
        # for the first 13 user retrive 
        
        # user_selected  = recipesRating.objects.filter(person_id= request.session['person_id']).values_list('person_id')
        # print('-------------->>',user_selected[0][0], request.session['person_id'])
        rated = recipesRating.objects.all()
        if user_selected:
            
            # print('------', user_selected[0][0], request.session['person_id'])
            #person_id = request.session['person_id']
            # rated_recipes = recipes.objects.ex
            # unrated = recipes.objects.exclude(recipes_id = )
             
            # unique_rate = recipesRating.objects.filter(person_id = request.session['person_id'])
            # print('------ uniiiique :',unique_rate,len(unique_rate))
            # notRated =  recipes.objects.exclude(Q(id__in=unique_rate.values('recipes')) | Q(id__in=rated)).values_list("id","Name","image_link").order_by('?')
            
            rated = recipesRating.objects.all().values('recipes')
            print('rated')
            S =  recipes.objects.exclude(id__in=rated)
            
            notRated = S.exclude(id__in = user_selected).values_list("id","Name","image_link").order_by('?')
            
            
            print('not rated by user ',len(notRated))
            S = notRated
            # print("-------",S)
            cache.set('S',S)
            # print(S)
            request.session['data'] = list(S)
            # print(S[0])
            # print('-----',list(S))
            
        else:
            rated = recipesRating.objects.all().values('recipes')
            
            S =  recipes.objects.exclude(id__in=rated).order_by('?').values_list("id","Name","image_link")
            
            print('not rated--->', len(S))
            #all().order_by('?')
            # print('All--->',len(S))
            request.session['data'] = list(S)
            # print('-----',list(S))
            
            
            cache.set('S',S)
            # print(S)
            
            # if recipesRating.objects.all().distinct().count() == 400:
            #     recipesRating.seen += 1 
            # p = recipesRating.objects.values('person_id').distinct().count()
            # if 
            # number_user= recipesRating.objects.all().values_list('person_id').distinct()
            # print(len(number_user))
            # if len(S) == 400 and len(number_user) <:
            #     S = recipes.objects.all()

        S1 = recipesRatingForm(prefix='S1')
        S2 = recipesRatingForm(prefix='S2')
        S3 = recipesRatingForm(prefix='S3')
        S4 = recipesRatingForm(prefix='S4')
        S5 = recipesRatingForm(prefix='S5')
        S6 = recipesRatingForm(prefix='S6')

        context ={
                        'S1_F': S1,  's_1':S[0],
                        'S2_F':S2,  's_2':S[1],
                        'S3_F':S3, 's_3':S[2],
                        'S4_F':S4, 's_4':S[3],
                        'S5_F':S5, 's_5':S[4],
                        'S6_F': S6,  's_6':S[5],
                }

        return render(request, 'image_quality/rate_recipes.html', context)
    

def choice_evaluation(request):
    user_selected = EvaluateChoices.objects.filter(person_id = request.session['person_id'])
    if user_selected:
        EvaluateChoices.objects.filter(person_id=request.session['person_id']).delete()
  
    if request.method == 'POST':
        evaluation_form = ChoiceEvaluationForm(request.POST)
        person = request.session['person_id']
        ChoiceEvaltion = EvaluateChoices()
        if evaluation_form.is_valid():
            # print("-----------here we are")
            # ChoiceEvaltion.person = request.session['person_id']
            evaluation_ = evaluation_form.save(commit=False)
            evaluation_.person_id = person
            # ChoiceEvaltion.person_id = evaluation_form.foriengkey
            evaluation_.session_id = request.session['prolific_id']
#<<<<<<< HEAD
#=======
            #evaluation_.prolific_id = request.session['prolific_id']
#>>>>>>> e60f18877d25637f05dff25cde799b8906f7dcab
            evaluation_.save()
            return redirect('image_quality:thank_u')
    else:
         evaluation_form = ChoiceEvaluationForm()
    return render(request, 'image_quality/choice_evaluation.html', context={'eval_form': evaluation_form})
    


def thank_u(request):
    return render(request, 'image_quality/thanks.html', context={'session_id':request.session['session_id']})