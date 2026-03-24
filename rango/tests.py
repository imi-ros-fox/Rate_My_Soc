from django.contrib.auth.models import User
from rango.models import UserProfile, Category, Society, Review, Rating, Upvote
from django.test import TestCase
from django.core.exceptions import ValidationError
from rango.forms import UserForm, UserProfileForm, SocietyForm, CategoryForm, RatingForm, ReviewForm, EditProfileForm
from rango import forms, views
from django import forms
from rango import forms as rango_forms

def create_test_user(username='testuser', password='testpassword123', role='STUDENT'):
    #Helper function to create a test user with a profile
    user = User.objects.create_user(
        username=username,
        email=f'{username}@test.com',
        password=password
    )
    profile = user.userprofile
    profile.role = role
    profile.bio = f"Bio for {username}"
    profile.save()
    return user

def create_test_society(name='Test Society', created_by=None, categories=None):
    #Helper function to create a test society
    if created_by is None:
        created_by = create_test_user('society_creator')
    
    society = Society.objects.create(
        name=name,
        description='Test description',
        created_by=created_by
    )
    
    if categories:
        society.categories.set(categories)
    
    return society


def create_test_category(name='Test Category'):
    #Helper function to create a test category
    return Category.objects.create(name=name)


def create_test_review(society, user, comment='Test review'):
    #Helper function to create a test review.
    return Review.objects.create(
        society=society,
        user=user,
        comment=comment
    )



def create_test_rating(society, user, star=5):
    #Helper function to create a test rating
    return Rating.objects.create(
        society=society,
        user=user,
        star=star
    )


#Model Tests

class ModelTests(TestCase):
    #Tests for all models in the Rate My Society application.
    
    def setUp(self):
        self.user = create_test_user()
        self.category = create_test_category()
        self.society = create_test_society(created_by=self.user, categories=[self.category])
    
    def test_category_model(self):
        #Test Category model attributes and methods.

        # Test string representation
        self.assertEqual(str(self.category), 'Test Category')
        
        # Test name can be updated
        self.category.name = 'New Category Name'
        self.category.save()
        self.assertEqual(self.category.name, 'New Category Name')

        with self.assertRaises(Exception):
            Category.objects.create(name='Test Category')
        
        
    
    def test_user_profile_model(self):
        #Test UserProfile model attributes and methods.
        profile = self.user.userprofile
        
        # Test string representation
        self.assertEqual(str(profile), self.user.username)
        
        # Test default values
        self.assertEqual(profile.role, 'STUDENT')
        self.assertEqual(profile.bio, 'Bio for testuser')
        self.assertIsNotNone(profile.join_date)
        
        # Test profile creation signal
        new_user = User.objects.create_user(username='newuser', password='pass')
        self.assertTrue(hasattr(new_user, 'userprofile'))
        self.assertIsNotNone(new_user.userprofile)
        
        # Test president role
        president_user = create_test_user('president', role='PRESIDENT')
        self.assertEqual(president_user.userprofile.role, 'PRESIDENT')
    
    def test_society_model(self):
        # Test Society model attributes and methods.

        # Test string representation
        self.assertEqual(str(self.society), 'Test Society')
        
        
        # Test name can be updated
        self.society.name = 'New Society Name'
        self.society.save()
        self.assertEqual(self.society.name, 'New Society Name')
        
        # Test ManyToMany relationship with categories
        self.assertEqual(self.society.categories.count(), 1)
        self.assertEqual(self.society.categories.first().name, 'Test Category')
        
        # Test foreign key relationship
        self.assertEqual(self.society.created_by, self.user)
        
        # Test plural name
        self.assertEqual(Society._meta.verbose_name_plural, 'Societies')
    
    def test_review_model(self):
        #Test Review model attributes and methods.

        review = create_test_review(self.society, self.user)
        
        # Test string representation
        expected_str = f"{self.user.username} review of {self.society.name}"
        self.assertEqual(str(review), expected_str)
        
        # Test unique_together constraint
        with self.assertRaises(Exception):
            Review.objects.create(society=self.society, user=self.user, comment='Duplicate review')
        
        # Test created_at auto-population
        self.assertIsNotNone(review.created_at)



#Form tests

class FormTests(TestCase):
    #Tests for all forms in the Rate My Society application.
    
    def setUp(self):
        self.user = create_test_user()
        self.category = create_test_category()
        self.society = create_test_society(created_by=self.user, categories=[self.category])
    
    def test_user_form(self):
        #Test UserForm validation 

        # Valid data
        valid_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'securepass123'
        }
        form = UserForm(data=valid_data)
        self.assertTrue(form.is_valid())
        
        # Missing username case
        invalid_data = {
            'email': 'newuser@test.com',
            'password': 'securepass123'
        }
        form = UserForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        
        # Invalid email
        invalid_data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'securepass123'
        }
        form = rango_forms.UserForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        
        # Check form fields
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('password', form.fields)
        self.assertIsInstance(form.fields['password'].widget, forms.PasswordInput)
    
    def test_user_profile_form(self):
        #Test UserProfileForm 

        valid_data = {
            'role': 'STUDENT',
            'bio': 'This is my bio'
        }
        form = rango_forms.UserProfileForm(data=valid_data)
        self.assertTrue(form.is_valid())
        
        # Test role choices
        form = rango_forms.UserProfileForm(data={'role': 'PRESIDENT', 'bio': 'President bio'})
        self.assertTrue(form.is_valid())
        
        # Invalid role
        form = rango_forms.UserProfileForm(data={'role': 'INVALID', 'bio': 'Bio'})
        self.assertFalse(form.is_valid())
        
        # Test optional fields
        form = rango_forms.UserProfileForm(data={})
        self.assertFalse(form.is_valid())
        
        # Check field configuration
        self.assertIn('role', form.fields)
        self.assertIn('bio', form.fields)
        self.assertIn('picture', form.fields)
    
    def test_edit_profile_form(self):
        #Test EditProfileForm 

        # Test form initialisation with user
        form = EditProfileForm(instance=self.user.userprofile, user=self.user)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('email', form.fields)
        
        # Test valid data
        valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@test.com',
            'bio': 'Updated bio',
            'role': 'STUDENT'
        }
        form = EditProfileForm(data=valid_data, instance=self.user.userprofile, user=self.user)
        self.assertTrue(form.is_valid())
        
        # Test save functionality
        form = EditProfileForm(data=valid_data, instance=self.user.userprofile, user=self.user)
        if form.is_valid():
            profile = form.save()
            self.user.refresh_from_db()
            self.assertEqual(self.user.first_name, 'John')
            self.assertEqual(self.user.last_name, 'Doe')
            self.assertEqual(self.user.email, 'john@test.com')
            self.assertEqual(profile.bio, 'Updated bio')
    
    def test_society_form(self):
        #Test SocietyForm validation and field configuration.

        valid_data = {
            'name': 'New Society',
            'description': 'This is a new society',
            'categories': [self.category.id]
        }
        form = rango_forms.SocietyForm(data=valid_data)
        self.assertTrue(form.is_valid())
        
        # Test missing required fields
        invalid_data = {
            'name': '',
            'description': 'Test'
        }
        form = rango_forms.SocietyForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        
        
    
    def test_category_form(self):
        #Test CategoryForm validation.

        valid_data = {'name': 'New Category'}
        form = CategoryForm(data=valid_data)
        self.assertTrue(form.is_valid())
        
        # Test duplicate category
        form = CategoryForm(data={'name': 'Test Category'})  # Already exists
        self.assertFalse(form.is_valid())
        
        # Test empty name
        form = CategoryForm(data={'name': ''})
        self.assertFalse(form.is_valid())
    
    def test_rating_form(self):
        # Test RatingForm validation.

        # Test valid stars 1-5
        for star in range(1, 6):
            form = RatingForm(data={'star': star})
            self.assertTrue(form.is_valid(), f"Star {star} should be valid")
        
        # Test invalid star values
        for star in [0, 6, 10, -1]:
            form = RatingForm(data={'star': star})
            self.assertFalse(form.is_valid())
        
        # Test missing star
        form = RatingForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('star', form.errors)
        
        # Test clean_star method
        form = RatingForm(data={'star': 3})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['star'], 3)
    
    def test_review_form(self):
        #Test ReviewForm validation.


        # Test valid review
        valid_data = {'comment': 'This is a great society!'}
        form = ReviewForm(data=valid_data)
        self.assertTrue(form.is_valid())
        
        # Test empty comment (allowed)
        form = ReviewForm(data={'comment': ''})
        self.assertTrue(form.is_valid())
        
        



    
    
    