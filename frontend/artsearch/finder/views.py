from django.shortcuts import render
from django import forms
#from django.http import HttpResponse


# Create your views here.

MUSEUMS = ['artic','MOMA','MCA']
OPTIONS = [(True,m) for m in MUSEUMS]

def start(request):
	'''
	Our main (only) page. Takes request
	checks if there is a form filled
	loads html with filler (results)
	'''
	if request.method == 'GET':
		form = searchform(request.GET)
		print form
		#fill_filler(form)
	c = {'form':form}

	return render(request, 'finder/start.html',c)


class searchform( forms.Form  ):
	'''
	Takes the form, builds dictionary of args
	calls other function that'll search tables
	returns that function's result
	'''
	text = forms.CharField(label='Seach description & titles',
		required=False)

	museums = forms.MultipleChoiceField(
		OPTIONS
		, widget=forms.CheckboxSelectMultiple
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


