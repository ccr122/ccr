from django.shortcuts import render
from django import forms
#from django.http import HttpResponse


# Create your views here.

MUSEUMS = ['artic','MOMA','MCA','Random museum number 1'] # We should get this list from the sql table

OPTIONS = [(True,m) for m in MUSEUMS]

def start(request):
	'''
	Our main (only) page. Takes request
	checks if there is a form filled
	loads html with filler (results)
	'''
	if request.method == 'GET':
		form = searchform(request.GET)
		if form.is_valid():
			print '\n'
			print form.cleaned_data # NEED HELP - SELECTING ! OPTION SELECTS ALL OPTIONS!
		#fill_filler(form)

	result= None #[('google.com','google'),('facebook.com','facebook')]	

	c = {'form':form, 'result': result}
	return render(request, 'finder/start.html',c) # NEED HELP WITH HTML (CAN'T CALL ELEMENTS OF TUPLE)



class searchform( forms.Form  ):
	'''
	Takes the form, builds dictionary of args
	calls other function that'll search tables
	returns that function's result
	'''
	text = forms.CharField(label='Seach description & titles',
		required=False)

	museums = forms.MultipleChoiceField(
			OPTIONS,
			widget = forms.CheckboxSelectMultiple,
			label  = 'Select which museums to search from'
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


