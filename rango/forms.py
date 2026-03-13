from django import forms
from django.contrib.auth.models import User
from rango.models import UserProfile, Society


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):

    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.RadioSelect,
        initial='STUDENT',
        help_text='Please select whether you are a student or society president.'
    )

    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        max_length=500,
        help_text="Tell us a bit about yourself (optional)"
    )

    class Meta:
        model = UserProfile
        fields = ('picture', 'role', 'bio')


class EditProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('picture', 'bio')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['picture'].required = False
        self.fields['bio'].required = False

class SocietyForm(forms.ModelForm):
    class Meta:
        model = Society
        fields = ['name', 'description', 'image', 'categories']
        widgets = {
            'category': forms.CheckboxSelectMultiple(),
            'description': forms.Textarea(attrs={'rows':4}),
        }