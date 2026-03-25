from django.urls import path
from rango import views

app_name = 'rango'

urlpatterns = [ 
    path('', views.index, name='index'),
    #path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('restricted/', views.restricted, name='restricted'),
    path('logout/', views.user_logout, name='logout'),
    # path('create_soc/', views.create_soc, name='create_Soc'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile'),


    #society CRUD
    path('societies/', views.society_list, name='society_list'),
    path('societies/create/', views.create_society, name='create_society'),
    path('societies/<int:pk>/edit/', views.edit_society, name='edit_society'),
    path('societies/<int:pk>/delete/', views.delete_society, name='delete_society'),
    path('societies/<int:pk>/', views.society_detail, name='society_detail'),
    path('societies/<int:pk>/rate/', views.rate_society, name='rate_society'),
    path('societies/<int:pk>/review/', views.add_review, name='add_review'),
    path('reviews/<int:review_id>/upvote/', views.upvote_review, name='upvote_review'),
    path('search/', views.search_societies, name='search_societies'),
    path('about/', views.about, name='about'),
    # path('societies/top/', views.top_rated_societies, name='top_societies'),

    #Category CRUD
    # path('categories/', views.category_list, name='category_list'),
    # path('categories/create/', views.create_category, name='create_category'),
    # path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    # path('categories/<int:pk>/edit/', views.edit_category, name='edit_category'),
    # path('categories/<int:pk>/delete/', views.delete_category, name='delete_category'),

    #My Review CRUD
    # path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('reviews/<int:pk>/edit/', views.edit_review, name='edit_review'),
    path('reviews/<int:pk>/delete/', views.delete_review, name='delete_review'),

    #My Upvote CRUD
    # path('my-upvotes/', views.my_upvotes, name='my_upvotes'),
    path('upvotes/<int:pk>/delete/', views.delete_upvote, name='delete_upvote'),
]