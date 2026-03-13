from django.urls import path
from rango import views

app_name = 'rango'

urlpatterns = [ 
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
 #   path('category/<slug:category_name_slug>/',
 #         views.show_category, name='show_category'),
 #   path('add_category/' , views.add_category, name='add_category'),
 #   path('category/<slug:category_name_slug>/add_page/',
 #         views.add_page, name='add_page'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('restricted/', views.restricted, name='restricted'),
    path('logout/', views.user_logout, name='logout'),
    path('create_soc/', views.create_soc, name='create_Soc'),
    #society CRUD
    # path('societies/', views.society_list, name='society_list'),
    # path('society/create/', views.create_society, name='create_society'),
    # path('society/<int:society_id>/', views.society_detail, name='society_detail'),
    # path('society/<int:society_id>/edit/', views.edit_society, name='edit_society'),
    # path('society/<int:society_id>/delete/', views.delete_society, name='delete_society'),
    path('societies/', views.society_list, name='society_list'),
    path('societies/create/', views.create_society, name='create_society'),
    path('societies/<int:pk>/edit/', views.edit_society, name='edit_society'),
    path('societies/<int:pk>/delete/', views.delete_society, name='delete_society'),
    path('societies/<int:pk>/', views.society_detail, name='society_detail'),
]