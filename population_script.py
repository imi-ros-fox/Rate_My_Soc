import os

from django import views
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rate_my_soc_project.settings')

import django

django.setup()
from rango.models import Category, Society, Review, Rating
from django.contrib.auth.models import User


def populate():
    # Create a dummy user for created_by
    user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'})
    if created:
        user.set_password('password')
        user.save()

    # Define categories
    categories = ['Sports', 'Arts', 'Academic', 'Social', 'Cultural']

    # Create categories
    cat_objects = {}
    for cat_name in categories:
        cat_objects[cat_name] = add_cat(cat_name)

    # Define societies
    societies = [
        {'name': 'Football Club', 'description': 'A society for football enthusiasts.', 'categories': ['Sports'], 'image': 'football_society_image.jpg'},
        {'name': 'Drama Society', 'description': 'For those interested in acting and theater.', 'categories': ['Arts'], 'image': 'drama_society_image.jpg'},
        {'name': 'Tech Society', 'description': 'Tech lovers unite!', 'categories': ['Academic'], 'image': 'tech_society_image.jpg'},
        {'name': 'Debate Club', 'description': 'Sharpen your debating skills.', 'categories': ['Academic', 'Social'], 'image': 'debate_society_image.jpg'},
        {'name': 'Music Society', 'description': 'For musicians and music lovers.', 'categories': ['Arts', 'Cultural'], 'image': 'music_society_image.jpg'},
        {'name': 'Chess Club', 'description': 'Strategic minds welcome.', 'categories': ['Academic', 'Social'], 'image': 'chess_society_image.png'},
        {'name': 'Photography Club', 'description': 'Capture the world through lenses.', 'categories': ['Arts'], 'image': 'photography_society_image.png'},
        {'name': 'Volunteering Society', 'description': 'Give back to the community.', 'categories': ['Social'], 'image': 'volunteering_society.jpg'},
    ]

    # Create societies
    for soc_data in societies:
        cat_list = [cat_objects[cat] for cat in soc_data['categories']]
        add_society(soc_data['name'], soc_data['description'], user, cat_list, soc_data.get('image', ''))

    # Add reviews to each society
    reviews_data = [
        {'society': 'Football Club', 'comment': 'Had a great time here. People are friendly and the weekend matches are always enjoyable.', 'rating': 5},
        {'society': 'Drama Society', 'comment': 'A solid society overall. Rehearsals can be quite long, but the productions turn out well and it definitely helped with my confidence on stage.', 'rating': 3},
        {'society': 'Tech Society', 'comment': 'It’s decent. The workshops are useful when they happen, but updates can be inconsistent. Could be better organised.', 'rating': 3},
        {'society': 'Debate Club', 'comment': 'Great for improving public speaking. Members are genuinely engaged and discussions are interesting. Would recommend.', 'rating': 4},
        {'society': 'Music Society', 'comment': 'Really welcoming atmosphere. It’s nice being around people who are genuinely interested in music.', 'rating': 5},
        {'society': 'Chess Club', 'comment': 'I joined to learn, but many members are quite advanced. It can feel a bit intimidating for beginners.', 'rating': 2},
        {'society': 'Photography Club', 'comment': 'Enjoyable overall. The trips are a highlight and you do learn a lot, though meeting times can sometimes clash with my schedule.', 'rating': 4},
        {'society': 'Volunteering Society', 'comment': 'A good choice if you want to do something meaningful. The volunteering experiences are rewarding.', 'rating': 5},
    ]
    
    for review_data in reviews_data:
        soc = Society.objects.get(name=review_data['society'])
        add_review(user, soc, review_data['comment'], review_data['rating'])

    # Print out the societies and their categories
    for s in Society.objects.all():
        print(f'- {s}: {s.description}')
        print(f'  Categories: {[cat.name for cat in s.categories.all()]}')


def add_society(name, description, created_by, categories, image=''):
    s = Society.objects.get_or_create(name=name, defaults={'description': description, 'created_by': created_by})[0]
    if image:
        s.image = f'society_images/{image}'
    for cat in categories:
        s.categories.add(cat)
    s.save()
    return s

def add_cat(name):
    c = Category.objects.get_or_create(name=name)[0]
    return c

def add_review(user, society, comment, rating):
    review, created = Review.objects.get_or_create(
        user=user, 
        society=society,
        defaults={'comment': comment}
    )
    
    # Add rating for the review
    Rating.objects.get_or_create(
        user=user,
        society=society,
        defaults={'star': rating}
    )
    
    return review

if __name__=='__main__':
    print('Starting Rango population script...')
    populate()