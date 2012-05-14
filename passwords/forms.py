from django.forms import ModelForm, Textarea, Select, ModelChoiceField, ChoiceField

from .models import Password

class PasswordForm(ModelForm):
    ldapGroup = ChoiceField()
    
    def __init__(self, *args, **kwargs):
        ldapGroup_choices = kwargs.pop('ldap_groups_choices', []) 
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['ldapGroup'].choices = sorted(ldapGroup_choices, key=lambda g: g[0])

    class Meta:
        model = Password
        exclude = ('accessRight',)    
        widgets = {
            'description': Textarea(attrs={'cols': 50, 'rows': 6}),
        }
