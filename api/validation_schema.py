from django import forms

class MyValidationForm(forms.Form):
    first = forms.CharField()
    second = forms.IntegerField()
    third = forms.IntegerField()