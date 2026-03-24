from django import forms
from django.contrib.auth.models import User
from rango.models import UserProfile, Society, Rating, Review
from rango.models import Category


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
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = UserProfile
        fields = ('bio', 'picture', 'role')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['picture'].required = False
        self.fields['bio'].required = False
        self.fields['role'].required = False
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()
            profile.save()
        return profile

class SocietyForm(forms.ModelForm):
    class Meta:
        model = Society
        fields = ['name', 'description', 'image', 'categories']
        widgets = {
            'categories': forms.CheckboxSelectMultiple(),
            'description': forms.Textarea(attrs={'rows':4}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['star']
        widgets = {
            'star': forms.Select(choices=[(i, '⭐' * i) for i in range(1, 6)])
        }

    def clean_star(self):
        star = self.cleaned_data.get('star')
        if not star:
            raise forms.ValidationError("Please select a rating.")
        return star

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows':3, 'placeholder':'Write your review...'})
        }