
from django import forms
from posters.models import Poster

class PDFForm(forms.ModelForm):
    class Meta:
        model = Poster
        fields = ('pdf', )
