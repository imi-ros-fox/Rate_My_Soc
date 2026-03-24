from django.contrib.auth.models import User
from rango.models import UserProfile, Category, Society, Review, Rating, Upvote

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