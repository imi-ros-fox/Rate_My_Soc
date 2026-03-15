from django.contrib import admin
from rango.models import UserProfile, Society, Upvote, Review, Category, Rating

admin.site.register(UserProfile)
admin.site.register(Society)
admin.site.register(Upvote)
admin.site.register(Review)
admin.site.register(Category)
admin.site.register(Rating)