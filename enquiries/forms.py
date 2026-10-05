import re
from django import forms
from django.utils.html import strip_tags
from .models import Enquiry

class EnquiryForm(forms.ModelForm):
    consent = forms.BooleanField(label='I agree to be contacted regarding this enquiry.')
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={'tabindex':'-1', 'autocomplete':'off'}))
    token = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project_type'].choices = [('', 'Select project type (optional)')] + list(Enquiry._meta.get_field('project_type').choices)
    class Meta:
        model = Enquiry
        fields = ['name', 'company_name', 'email', 'phone', 'project_type', 'message', 'consent']
        labels = {'name': 'Name', 'company_name': 'Company name', 'email':'Email', 'phone':'Phone number',
                  'project_type':'Project type', 'message':'Message / project requirements'}
        widgets = {'name':forms.TextInput(attrs={'autocomplete':'name'}),
                   'company_name':forms.TextInput(attrs={'autocomplete':'organization'}),
                   'email':forms.EmailInput(attrs={'autocomplete':'email'}),
                   'phone':forms.TextInput(attrs={'type':'tel','autocomplete':'tel','placeholder':'+971', 'pattern':r'\+?[0-9 \(\)\-]{7,31}'}),
                   'message':forms.Textarea(attrs={'rows':3,'maxlength':4000})}

    def clean(self):
        data = super().clean()
        for key in ['name','company_name','message']:
            value = data.get(key, '')
            value = strip_tags(value)
            value = ''.join(c for c in value if c in '\n\t' or ord(c) >= 32).strip()
            data[key] = value
            if key != 'message' and not value:
                self.add_error(key, 'Please enter this information.')
        return data

    def clean_email(self): return self.cleaned_data['email'].strip().lower()

    def clean_phone(self):
        value = self.cleaned_data['phone'].strip()
        if not re.fullmatch(r'\+?[0-9 ()\-]+', value):
            raise forms.ValidationError('Enter a phone number, including country code.')
        digits = re.sub(r'\D', '', value)
        if not 7 <= len(digits) <= 15:
            raise forms.ValidationError('Enter between 7 and 15 digits.')
        return ('+' if value.startswith('+') else '') + digits
