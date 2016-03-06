from django.shortcuts import render
from django import forms
from  search.search import *
import os
parent = os.path.dirname(os.path.dirname(__file__))

PATH_to_searchpy = str(os.path.join(parent,'search/'))
print('\t\t'+PATH_to_searchpy)								# Can't get pickles to work :C
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
			result = get_results(args)
	c = {'form':form, 'result': result}
	return render(request, 'finder/start.html', c)

def get_results(args):
	'''
	Take args and use serach engine
	'''
	num_results = 10
	key_words = {}						# RENEEEEEE this is where your better words function goes
	for w in args.get('text').split():
		if w in key_words:
			key_words[w]+=1
		else:
			key_words[w]=1

	#key_words 	= str_to_dict(args.get('text'))   <<<<<<<<<<<<<<<<<<<<< this one specifically
	museums 	= args.get('museums')
	res = s_o.search(key_words,museums,num_results)

	if len(res) == 0:
		return [(' ','No results', None )]

	results = []
	for r in res:
		u = get_ex_attribute( r, 'url'  , PATH_to_searchpy)
		t = get_ex_attribute( r, 'title', PATH_to_searchpy)
		s = get_similar_results(r, museums)
		results += [(u,t,s)]

	return results

def get_similar_results(ex_id,museums):
	'''
	Given exhibit ID and seleced museums, similar_exhibits at those museums
	'''
	num_results = 10
	res = s_o.similar_exhibits(ex_id,museums,num_results)
	return [ ( 	get_ex_attribute( r, 'url'	, PATH_to_searchpy),
				get_ex_attribute( r, 'title', PATH_to_searchpy)	 )
			for r in res ]



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




