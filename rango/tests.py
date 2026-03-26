from django.contrib.auth.models import User
from rango.models import UserProfile, Category, Society, Review, Rating, Upvote
from django.test import TestCase
from django.core.exceptions import ValidationError
from rango.forms import UserForm, UserProfileForm, SocietyForm, CategoryForm, RatingForm, ReviewForm, EditProfileForm
from rango import forms, views
from django import forms
from rango import forms as rango_forms
from django.urls import reverse
from django.test import TestCase, Client

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
    #Helper function to create a test review
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
    #Tests for all models in Rate My Society
    
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
        #Test UserProfile model attributes and methods
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
        # Test Society model attributes and methods

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
        #Test Review model attributes and methods

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
    #Tests for all forms in Rate My Society 
    
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
        #Test SocietyForm validation and field configuration

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
        #Test CategoryForm validation

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
        # Test RatingForm validation

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
        #Test ReviewForm validation


        # Test valid review
        valid_data = {'comment': 'This is a great society!'}
        form = ReviewForm(data=valid_data)
        self.assertTrue(form.is_valid())
        
        # Test empty comment (not allowed) as reviews and ratings are sperate
        form = ReviewForm(data={'comment': ''})
        self.assertFalse(form.is_valid())
        
        
#Views Tests


class IndexViewTests(TestCase):
    #Tests for the index view
    
    def setUp(self):
        self.client = Client()
        self.user = create_test_user()
        self.category = create_test_category('Sports')
        self.society1 = create_test_society('Football Club', self.user, [self.category])
        self.society2 = create_test_society('Basketball Club', self.user, [self.category])
        
        # Add ratings for top societies
        create_test_rating(self.society1, self.user, 5)
        other_user = create_test_user('otheruser')
        create_test_rating(self.society1, other_user, 4)

    def test_index_view_uses_correct_template(self):
        #Test that index view uses the correct template

        response = self.client.get(reverse('rango:index'))
        self.assertTemplateUsed(response, 'rango/home/index.html')  

    def test_index_view_context(self):
        #Test that index view passes correct context variables

        response = self.client.get(reverse('rango:index'))
        
        self.assertIn('societies', response.context)
        self.assertIn('top_societies', response.context)
        self.assertIn('categories', response.context)
        
        # Check societies list
        societies = response.context['societies']
        self.assertEqual(societies.count(), 2)
        
        # Check categories list
        categories = response.context['categories']
        self.assertEqual(categories.count(), 1)

    def test_index_category_filter(self):
        #Test filtering societies by category

        # Create another category and society
        another_category = create_test_category('Music')
        create_test_society('Choir', self.user, [another_category])
        
        # Filter by Sports category
        response = self.client.get(reverse('rango:index'), {'cat': 'Sports'})
        societies = response.context['societies']
        self.assertEqual(societies.count(), 2)
        self.assertTrue(all('Sports' in [c.name for c in s.categories.all()] for s in societies))


"""About tests no longer needed """
class AboutViewTests(TestCase):
     #Tests for the about view.
    
    def setUp(self):
        self.client = Client()
        self.user = create_test_user()
        self.society = create_test_society(created_by=self.user)
        create_test_rating(self.society, self.user, 5)   
    
    def test_about_view_uses_correct_template(self):
        #Test that about view uses the correct template
        response = self.client.get(reverse('rango:about'))
        self.assertTemplateUsed(response, 'rango/home/about.html')
    
    def test_about_view_context(self):
        #Test that about view passes correct context variables.
        response = self.client.get(reverse('rango:about'))
        
        self.assertIn('visits', response.context)
        self.assertIn('total_users', response.context)
        self.assertIn('total_societies', response.context)
        self.assertIn('top_societies', response.context)
        
        self.assertEqual(response.context['total_users'], User.objects.count())
        self.assertEqual(response.context['total_societies'], Society.objects.count())
    

class RegistrationViewTests(TestCase):
    #Tests for the registration view
    
    def setUp(self):
        self.client = Client()
    
    
    def test_register_view_uses_correct_template(self):
        #Test that registration view uses the correct template
        response = self.client.get(reverse('rango:register'))
        self.assertTemplateUsed(response, 'rango/authentication/register.html')
    
    def test_register_valid_user(self):
        #Test successful user registration
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'securepass123',
            'role': 'STUDENT',
            'bio': 'Test bio'
        }
        response = self.client.post(reverse('rango:register'), data)
        
        
        # Check user was created
        user = User.objects.get(username='newuser')
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('securepass123'))
        self.assertEqual(user.email, 'newuser@test.com')
        
        # Check profile was created
        self.assertEqual(user.userprofile.role, 'STUDENT')
        self.assertEqual(user.userprofile.bio, 'Test bio')
        
        # User should be logged in automatically
        self.assertIn('_auth_user_id', self.client.session)
    
    def test_register_password_too_short(self):
        #Test registration with password less than 8 characters

        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'short',
            'role': 'STUDENT'
        }
        response = self.client.post(reverse('rango:register'), data)
        
        # User should not be created
        self.assertFalse(User.objects.filter(username='newuser').exists())



class LoginViewTests(TestCase):
    #Tests for the login view
    
    def setUp(self):
        self.client = Client()
        self.user = create_test_user('testuser', 'correctpass')
    
    
    def test_login_view_uses_correct_template(self):
        #Test that login view uses the correct template
        response = self.client.get(reverse('rango:login'))
        self.assertTemplateUsed(response, 'rango/authentication/login.html')
    
    def test_login_valid_credentials(self):
        #Test successful login 
        response = self.client.post(reverse('rango:login'), {
            'username': 'testuser',
            'password': 'correctpass'
        })
        
        
        self.assertEqual(response.url, reverse('rango:index'))
        self.assertIn('_auth_user_id', self.client.session)
    
    def test_login_invalid_credentials(self):
        #Test unsuccessful login 

        response = self.client.post(reverse('rango:login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        
        # Stays on login page
        self.assertNotIn('_auth_user_id', self.client.session)
    
    def test_login_remember_me(self):
        #Test remember me functionality

        response = self.client.post(reverse('rango:login'), {
            'username': 'testuser',
            'password': 'correctpass',
            'remember_me': 'on'
        })
        
        # Check session expiry is set to 2 weeks (1209600 seconds)
        self.assertEqual(self.client.session.get_expiry_age(), 1209600)
    
    def test_login_next_url_redirect(self):
        #Test redirect to next URL after login

        next_url = reverse('rango:restricted')
        response = self.client.post(
            reverse('rango:login'),
            {
                'username': 'testuser',
                'password': 'correctpass',
                'next': next_url
            }
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, next_url)


class ProfileViewTests(TestCase):
    #Tests for the profile view
    
    def setUp(self):
        self.client = Client()
        self.user = create_test_user('testuser')
        self.client.login(username='testuser', password='testpassword123')
        
    
    
    def test_profile_view_uses_correct_template(self):
        #Test that profile view uses the correct template

        response = self.client.get(reverse('rango:profile', kwargs={'username': 'testuser'}))
        self.assertTemplateUsed(response, 'rango/profile/profile.html')
    
    def test_profile_view_context(self):
        #Test that profile view passes correct context

        society = create_test_society(created_by=self.user)
        review = create_test_review(society, self.user)
        upvote = Upvote.objects.create(user=self.user, review=review)
        
        response = self.client.get(reverse('rango:profile', kwargs={'username': 'testuser'}))
        
        self.assertEqual(response.context['profile_user'], self.user)
        self.assertEqual(response.context['profile'], self.user.userprofile)
        self.assertTrue(response.context['is_own_profile'])
        self.assertEqual(response.context['reviews'].count(), 1)
        self.assertEqual(response.context['upvotes'].count(), 1)


class EditProfileViewTests(TestCase):
    #Tests for the edit profile view
    
    def setUp(self):
        self.client = Client()
        self.user = create_test_user('testuser')
        self.client.login(username='testuser', password='testpassword123')
    
    
    def test_edit_profile_view_uses_correct_template(self):
        #Test that edit profile view uses the correct template
        response = self.client.get(reverse('rango:edit_profile'))
        self.assertTemplateUsed(response, 'rango/profile/edit_profile.html')
    
    def test_edit_profile_valid_data(self):
        #Test successful profile update

        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@test.com',
            'bio': 'Updated bio',
            'role': 'PRESIDENT'
        }
        response = self.client.post(reverse('rango:edit_profile'), data)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('rango:profile', kwargs={'username': 'testuser'}))
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.email, 'john@test.com')
        self.assertEqual(self.user.userprofile.bio, 'Updated bio')
        self.assertEqual(self.user.userprofile.role, 'PRESIDENT')
    
    def test_edit_profile_requires_login(self):
        #Test that edit profile requires authentication

        self.client.logout()
        response = self.client.get(reverse('rango:edit_profile'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('rango:login')))


class SocietyListAndDetailTests(TestCase):
    #Tests for society list and detail views
    
    def setUp(self):
        self.client = Client()
        # Create a president user with password
        self.user = create_test_user(
            username='president',
            password='testpass123',  
            role='PRESIDENT'
        )
        # Log in with the same password
        login_result = self.client.login(username='president', password='testpass123')
        self.assertTrue(login_result, "Login failed in setUp") 
        
        self.category = create_test_category('Sports')
        self.society = create_test_society('Football Club', self.user, [self.category])
    
    def test_society_list_view(self):
        #Test society list view

        response = self.client.get(reverse('rango:society_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rango/society/society_list.html')
        self.assertEqual(response.context['societies'].count(), 1)
    
    def test_society_detail_view(self):
        #Test society detail view

        response = self.client.get(reverse('rango:society_detail', kwargs={'pk': self.society.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rango/society/society_detail.html')
        self.assertEqual(response.context['society'], self.society)
        self.assertIn('avg_rating', response.context)
        self.assertIn('reviews', response.context)
        self.assertIn('review_form', response.context)
    
    def test_create_society_view(self):
        #Test create society view

        # Test GET - user is already logged in from setUp
        response = self.client.get(reverse('rango:create_society'))
        self.assertEqual(response.status_code, 200)
        
        # Test POST with valid data
        data = {
            'name': 'New Society',
            'description': 'This is a new society',
            'categories': [self.category.id]
        }
        response = self.client.post(reverse('rango:create_society'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('rango:index'))
        
        society = Society.objects.get(name='New Society')
        self.assertEqual(society.created_by, self.user)
    
    def test_create_society_requires_president_role(self):
        #Test that only presidents can create societies

        # Create a student user and log in as student
        student_user = create_test_user(
            username='student',
            password='testpass123',
            role='STUDENT'
        )
        self.client.login(username='student', password='testpass123')
        
        response = self.client.get(reverse('rango:create_society'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('rango:index'))
        
        # Log back in as president for other tests
        self.client.login(username='president', password='testpass123')
    
    def test_edit_society_view(self):
        #Test edit society view

        # User is already logged in as president from setUp
        response = self.client.get(reverse('rango:edit_society', kwargs={'pk': self.society.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Test POST update
        data = {
            'name': 'Updated Society',
            'description': 'Updated description',
            'categories': [self.category.id]
        }
        response = self.client.post(reverse('rango:edit_society', kwargs={'pk': self.society.pk}), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('rango:index'))
        
        self.society.refresh_from_db()
        self.assertEqual(self.society.name, 'Updated Society')
    
    def test_edit_society_unauthorized(self):
        #Test that non-creators can't edit society

        other_user = create_test_user(
            username='otheruser',
            password='testpass123',
            role='PRESIDENT'
        )
        self.client.login(username='otheruser', password='testpass123')
        
        response = self.client.get(reverse('rango:edit_society', kwargs={'pk': self.society.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('rango:index'))
        
        # Log back in as president
        self.client.login(username='president', password='testpass123')
    
    def test_delete_society_view(self):
        #Test delete society view

        # User is already logged in as president from setUp
        response = self.client.post(reverse('rango:delete_society', kwargs={'pk': self.society.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('rango:index'))
        self.assertFalse(Society.objects.filter(pk=self.society.pk).exists())

class RatingAndReviewTests(TestCase):
    #Tests for rating and review functionality
    
    def setUp(self):
        self.client = Client()
        self.user = create_test_user('testuser', password='testpass123')
        self.society = create_test_society(created_by=self.user)
        self.client.login(username='testuser', password='testpass123')
    
    def test_rate_society(self):
        #Test rating a society

        response = self.client.post(
            reverse('rango:rate_society', kwargs={'pk': self.society.pk}),
            {'star': 4}
        )
        self.assertEqual(response.status_code, 302)
        
        rating = Rating.objects.get(user=self.user, society=self.society)
        self.assertEqual(rating.star, 4)
    
    def test_update_rating(self):
        #Test updating an existing rating

        # Create initial rating
        self.client.post(
            reverse('rango:rate_society', kwargs={'pk': self.society.pk}),
            {'star': 3}
        )
        
        # Update rating
        response = self.client.post(
            reverse('rango:rate_society', kwargs={'pk': self.society.pk}),
            {'star': 5}
        )
        self.assertEqual(response.status_code, 302)
        
        rating = Rating.objects.get(user=self.user, society=self.society)
        self.assertEqual(rating.star, 5)
    
    def test_add_review(self):
        #Test adding a review

        response = self.client.post(
            reverse('rango:add_review', kwargs={'pk': self.society.pk}),
            {'comment': 'Good'}
        )
        self.assertEqual(response.status_code, 302)
        
        review = Review.objects.get(user=self.user, society=self.society)
        self.assertEqual(review.comment, 'Good')
    
    def test_duplicate_review(self):
        #Test that users cannot add multiple reviews for same society

        # Create first review
        create_test_review(self.society, self.user, 'First review')
        
        # Try to add second review
        response = self.client.post(
            reverse('rango:add_review', kwargs={'pk': self.society.pk}),
            {'comment': 'Second review'}
        )
        
        # Should still only have one review
        self.assertEqual(Review.objects.filter(user=self.user, society=self.society).count(), 1)
    
    def test_upvote_review(self):
        #Test upvoting a review

        # Create review from another user
        other_user = create_test_user('otheruser', password='testpass123')
        review = create_test_review(self.society, other_user, 'Good')
        
        response = self.client.post(reverse('rango:upvote_review', kwargs={'review_id': review.pk}))
        self.assertEqual(response.status_code, 302)
        
        upvote = Upvote.objects.filter(user=self.user, review=review)
        self.assertTrue(upvote.exists())
    
    def test_upvote_toggle(self):
        #Test that upvote can be removed

        # Create review from another user
        other_user = create_test_user('otheruser', password='testpass123')
        review = create_test_review(self.society, other_user, 'Good')
        
        # First upvote
        self.client.post(reverse('rango:upvote_review', kwargs={'review_id': review.pk}))
        self.assertTrue(Upvote.objects.filter(user=self.user, review=review).exists())
        
        # Should remove upvote
        self.client.post(reverse('rango:upvote_review', kwargs={'review_id': review.pk}))
        self.assertFalse(Upvote.objects.filter(user=self.user, review=review).exists())
