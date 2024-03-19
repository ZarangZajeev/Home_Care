from django import forms

class CustomerServiceSearchForm(forms.Form):
    city = forms.CharField(max_length=30, required=False)
    category = forms.CharField(max_length=30, required=False)
