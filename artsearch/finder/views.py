from django.shortcuts import render
from django import forms
from  search.search import get_search_object, Search, get_ex_attribute

import os
#os.chdir('..')
print ('\n\n\n\n working directory:'+str(os.getcwd()))

parent = os.path.dirname(os.path.dirname(__file__))

PATH_to_searchpy = str(os.path.join(parent,'search/'))
print('\t\t'+PATH_to_searchpy)								# Can't get pickles to work :C
s_o = get_search_object(PATH_to_searchpy,force = True)



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
	if request.method == 'GET':
		form = searchform(request.GET)
		if form.is_valid():
			print ('\n')
			print (form.cleaned_data)
			args = form.cleaned_data
			result = get_results(args)

	#result= [('google.com','google'),('facebook.com','facebook')]	

	c = {'form':form, 'result': result}
	return render(request, 'finder/start.html',c) # NEED HELP WITH HTML (CAN'T CALL ELEMENTS OF TUPLE)

def get_results(args):
	'''
	Take args and use serach engine
	'''
	num_results = 5
	key_words 	= searchify(args.get('text'))
	museums 	= args.get('museums')
	res = s_o.search(key_words,museums,num_results)
	return [  (	get_ex_attribute(PATH_to_searchpy,r, 'url'),
			 	get_ex_attribute(PATH_to_searchpy,r, 'title') )
			for r in res    ]


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


	

#class fill_filler(self):
'''
	Takes the results after searching tables
	turns it into args for our html 
	'''
''' HTML CODE BECAUSE YOU CANT MULTILINE COMMENT IN HTML
<form method='get'>
	This is the form.
	<br>
	Keyword search:
	<input type='text'>
	<br>
	If you would like to select from specific museums, click it's button. By default we search from every museum
	<ul>
		{% for m in museum %}
		<input type ='radio'name={{m}}}>{{m}}</input>
		{% endfor %}
	</ul>
'''


