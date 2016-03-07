from django.shortcuts import render
from django import forms
from  search.search import make_file_paths, Search, get_search_object
import os
parent = os.path.dirname(os.path.dirname(__file__))

PATH_to_searchpy = str(os.path.join(parent,'search/'))
print('\t\t'+PATH_to_searchpy)	

s_o = get_search_object(PATH_to_searchpy)



# Create your views here.

MUSEUMS = [	('001', 'Art Institute of Chicago'),
			('002', 'Museum of Contemporary Art'),
			('003', 'Metrolitan Museum of Art'),
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
			print ('\n')
			print (form.cleaned_data)
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
	text = forms.CharField(label='Seach description & titles',
		required=True)

	museums = forms.MultipleChoiceField(
			choices = MUSEUMS,
			widget 	= forms.CheckboxSelectMultiple,
			label  	= 'Select which museums to search from'
		)




