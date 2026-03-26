import os

from django import views
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rate_my_soc_project.settings')

import django

django.setup()
from rango.models import Category, Society
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

if __name__=='__main__':
    print('Starting Rango population script...')
    populate()