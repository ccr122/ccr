from django.shortcuts import render
from django import forms
from  search.search import *
import os
import csv

### get search information
parent = os.path.dirname(os.path.dirname(__file__))
PATH_to_searchpy = str(os.path.join(parent,'search/'))
museum_csv = PATH_to_searchpy+'csvs/musid_name.csv'
with open(museum_csv,'r') as f:
	r = csv.reader(f,delimiter='|')
	next(r)
	MUSEUMS = []
	for row in r:
		MUSEUMS.append( (row[0],row[1]) )		
s_o = get_search_object(PATH_to_searchpy,force = False)

def start(request):
	'''
	Our main (only) page. Takes request
	checks if there is a form filled
	shows results
	'''
	result = None
	if request.method == 'GET':				# <-TA said this was good practice
		form = searchform(request.GET)
		if form.is_valid():
			args   = form.cleaned_data
			result = s_o.get_results(args,PATH_to_searchpy)
	c = {'form':form, 'result': result}
	return render(request, 'finder/start.html', c)

def update(request):
	'''
	Go to this page to force search object to update
	'''
	s_o = get_search_object(PATH_to_searchpy,force = True)
	render(request,'finder/updated.html')

class searchform( forms.Form  ):
	'''
	Takes the form, builds dictionary of args
	calls other function that'll search tables
	returns that function's result
	'''
	text = forms.CharField(
			label		= 'Seach description & titles',
			required	= True,
		)

	museums = forms.MultipleChoiceField(
			required 	= False,
			choices 	= MUSEUMS,
			widget 		= forms.CheckboxSelectMultiple,
			label  		= 'Select which museums to search from'
		)