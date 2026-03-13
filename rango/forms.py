from django import forms
from rango.models import Page, Category
from django.contrib.auth.models import User
from rango.models import UserProfile

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, 
                           help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Category
        fields = ('name',)

class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, 
                            help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200, 
                         help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        if url and not (url.startswith('http://') or url.startswith('https://')): 
            url = f'http://{url}'
            cleaned_data['url'] = url
        
        return cleaned_data

    class Meta:
        model = Page
        exclude = ('category',)

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
            
