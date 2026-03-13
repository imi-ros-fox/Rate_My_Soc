from django import forms
from django.contrib.auth.models import User
from rango.models import UserProfile

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):

    #When registering users choose if they are student or soc president
    role = forms.ChoiceField(
        choices = UserProfile.ROLE_CHOICES,
        widget = forms.RadioSelect,
        initial='STUDENT',
        help_text='Please select whether you are a student or society president.'
    )

    #When registering users can add a bio if they want
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        max_length=500,
        help_text="Tell us a bit yourself (optional)"
    )

    #MIGHT NEED TO ADD SECTION TO ALLOW USER TO UPLOAD PROFILE PIC


    class Meta:
        model = UserProfile
        fields = ('website', 'picture', 'role', 'bio') #Updated this

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture', 'bio') #Doesn't allow role to be changed

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['picture'].required = False
            self.fields['bio'].required = False
            
