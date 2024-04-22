from django import forms
from home_service.models import City

class CustomerServiceSearchForm(forms.Form):
    city = forms.CharField(max_length=30, required=False)
    category = forms.CharField(max_length=30, required=False)

class AddCityForm(forms.ModelForm):
    class Meta:
        model=City
        fields=['city']