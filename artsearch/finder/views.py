from django.shortcuts import render
from django import forms
from  search.search import *
import os
parent = os.path.dirname(os.path.dirname(__file__))

PATH_to_searchpy = str(os.path.join(parent,'search/'))
print('\t\t'+PATH_to_searchpy)	

s_o = get_search_object(PATH_to_searchpy,force=False)



# Create your views here.

MUSEUMS = [	('001', 'Art Institute of Chicago'),
			('002', 'Museum of Contemporary Art'),
			('003', 'Metropolitan Museum of Art'),
			('004', 'Museum of Modern Art'),
			('005', 'DeYoung Museum'),
			('006', 'Legion of Honor')	]

def start(request):
	'''
	Our main (only) page. Takes request
	checks if there is a form filled
	loads html with filler (results)
	'''
	result = None
	similar_results = None
	if request.method == 'GET':
		form = searchform(request.GET)
		if form.is_valid():
			args = form.cleaned_data
			result = s_o.get_results(args,PATH_to_searchpy)
	c = {'form':form, 'result': result}
	return render(request, 'finder/start.html', c)

class searchform( forms.Form  ):
	'''
	Takes the form, builds dictionary of args
	calls other function that'll search tables
	returns that function's result
	'''
	text = forms.CharField(
			label='Seach description & titles',
			required=True,
		)

	museums = forms.MultipleChoiceField(
			required 	= False,
			choices 	= MUSEUMS,
			widget 		= forms.CheckboxSelectMultiple,
			label  		= 'tSelect which museums to search from'
		)