from django import forms

class Weather(forms.Form):
    city = forms.CharField(label = "Укажите город", help_text="Казань",
                           error_messages = {'required': 'Поле не должно быть пустым'})
