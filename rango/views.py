from datetime import datetime
from urllib import response

from django.contrib.auth.models import User
from django.db.models import Avg, Q, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import os
from rango.forms import UserForm, UserProfileForm, SocietyForm, CategoryForm, ReviewForm
from .models import UserProfile, Society, Category, Rating, Review, Upvote


def index(request):
    context_dict = {}
    visitor_cookie_handler(request)
    response = render(request, 'rango/index.html', context=context_dict)
    return response

def about(request):
    visitor_cookie_handler(request)
    total_users = User.objects.count()
    total_societies = Society.objects.count()
    # Top 3
    top_societies = Society.objects.annotate(
        avg_rating=Avg('rating__star')
    ).filter(avg_rating__isnull=False).order_by('-avg_rating')[:3]

    context_dict = {
        'visits': request.session['visits'],
        'total_users': total_users,
        'total_societies': total_societies,
        'top_societies': top_societies,
    }

    return render(request, 'rango/about.html', context=context_dict)

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():

            password = user_form.cleaned_data.get('password')
            if len(password) < 8:
                messages.error(request, 'Password must be at least 8 characters long')
                return render(request, 'rango/register.html', {
                    'user_form': user_form,
                    'profile_form': profile_form,
                    'registered': registered
                    #upd
                })

            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = user.userprofile

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.role = profile_form.cleaned_data.get('role', 'STUDENT')
            profile.bio = profile_form.cleaned_data.get('bio', '')
            profile.save()

            login(request, user)
            registered = True

            if profile.role == 'PRESIDENT':
                messages.success(request,
                    'Welcome to Rate My Society! You can now create and manage societies.')
            else:
                messages.success(request,
                    'Welcome to Rate My Society! You can now explore and review societies.')

            return redirect(reverse('rango:index'))

        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered
    })

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        #Added a remember me feature
        remember_me = request.POST.get('remember_me')

        user = authenticate(username=username, password = password)

        if user:
            if user.is_active:
                login(request, user)

                #Users login details are remembered for 2 weeks
                if remember_me:
                    request.session.set_expiry(1209600)
                else:
                    request.session.set_expiry(0)

                #Checks to see whether user is student or president
                try:
                    request.session['user_role'] = user.userprofile.role
                except UserProfileForm.DoesNotExist:
                    UserProfile.objects.create(user=user)
                    request.session['user_role'] = 'STUDENT'
                
                messages.success(request, f'Welcome back, {user.username}')

                #Makes sure if user is not logged in  when reviewing, they are forced to log in and then be redirected to review page instead of homepage
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url:
                    return redirect(next_url)

                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rate my Society account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html')

#Created a new profile view
@login_required
def profile_view(request, username):
    try:
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('rango:index')
    except UserProfile.DoesNotExist:
        #Create a profile if it doesn't exist
        profile = UserProfile.objects.create(user=user)

    if profile.role == 'PRESIDENT':
        societies_managed = []
    else:
        societies_managed = []
    
    context = {
        'profile_user': user,
        'profile': profile,
        'is_own_profile': request.user == user,
        'societies_managed': societies_managed,
    }

    return render(request, 'rango/profile.html', context)

#Created a new edit profile view
from .forms import EditProfileForm

@login_required
def edit_profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('rango:profile', username=request.user.username)
        else:
            messages.error(request, 'Please fix the following errors')
    else:
        form = EditProfileForm(instance=profile)
    
    return render(request, 'rango/edit_profile.html', {'form': form})

#Created a delete profile view

@login_required
def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        password = request.POST.get('password')

        if not user.check_password(password):
            messages.error(request, 'Incorrect password. Account is still active.')
            return redirect('rango:edit_profile')
        
        #Logout and delete
        logout(request)
        user.delete()
        messages.success(request, 'Account has been deleted.')
        return redirect('rango:index')
    return render(request, 'rango/delete_profile.html')

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1')) 
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now())) 
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S') 
    if (datetime.now()- last_visit_time).days > 0: 
        visits = visits + 1 
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits

@login_required
def create_soc(request):
    if request.user.userprofile.role != 'PRESIDENT':
        messages.error(request, 'Only Society Presidents can create societies.')
        return redirect('rango:society_list')

    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        category_ids = request.POST.getlist('tags[]')

        if not name or not description or not category_ids:
            messages.error(request, 'Please fill in all required fields and select at least one category.')
            return render(request, 'rango/create_soc.html', {'categories': categories})

        society = Society.objects.create(
            name=name,
            description=description,
            image=image,
            created_by=request.user
        )
        society.categories.set(category_ids)
        society.save()

        messages.success(request, f'Society "{society.name}" created successfully!')
        return redirect('rango:index')

    return render(request, 'rango/create_soc.html', {'categories': categories})

@login_required
def society_list(request):
    societies = Society.objects.all()
    return render(request, 'rango/society_list.html', {'societies': societies})

@login_required
def create_society(request):

    if request.user.userprofile.role != 'PRESIDENT':
        messages.error(request, 'Only Society Presidents can create societies.')
        return redirect('rango:society_list')

    if request.method == 'POST':
        form = SocietyForm(request.POST, request.FILES)
        if form.is_valid():
            society = form.save(commit=False)
            society.created_by = request.user
            society.save()
            form.save_m2m()
            messages.success(request, 'Society created successfully!')
            return redirect('rango:society_list')
    else:
        form = SocietyForm()
    return render(request, 'rango/create_society.html', {'form': form})

@login_required
def edit_society(request, pk):
    society = get_object_or_404(Society, pk=pk)

    if request.user != society.created_by or request.user.userprofile.role != 'PRESIDENT':
        messages.error(request, 'You are not allowed to edit this society.')
        return redirect('rango:society_list')

    if request.method == 'POST':
        form = SocietyForm(request.POST, request.FILES, instance=society)
        if form.is_valid():
            form.save()
            messages.success(request, 'Society updated successfully!')
            return redirect('rango:society_list')
    else:
        form = SocietyForm(instance=society)
    return render(request, 'rango/edit_society.html', {'form': form, 'society': society})

@login_required
def delete_society(request, pk):
    society = get_object_or_404(Society, pk=pk)

    if request.user != society.created_by or request.user.userprofile.role != 'PRESIDENT':
        messages.error(request, 'You are not allowed to delete this society.')
        return redirect('rango:society_list')

    if request.method == 'POST':
        society.delete()
        messages.success(request, 'Society deleted successfully!')
        return redirect('rango:society_list')

    return render(request, 'rango/delete_society.html', {'society': society})

@login_required
def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'rango/category_list.html', {'categories': categories})

@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    societies = Society.objects.filter(categories=category)
    context = {
        'category': category,
        'societies': societies
    }
    return render(request, 'rango/category_detail.html', context)

@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('rango:category_list')

    else:
        form = CategoryForm()

    return render(request, 'rango/create_category.html', {'form': form})

@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('rango:category_list')

    else:
        form = CategoryForm(instance=category)

    return render(request, 'rango/edit_category.html', {'form': form, 'category': category})

@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('rango:category_list')
    return render(request, 'rango/delete_category.html', {'category': category})

@login_required
def society_detail(request, pk):
    society = get_object_or_404(Society, pk=pk)
    avg_rating = Rating.objects.filter(society=society).aggregate(Avg('star'))['star__avg']
    user_rating = None
    try:
        user_rating = Rating.objects.get(user=request.user, society=society)
    except Rating.DoesNotExist:
        pass
    reviews = Review.objects.filter(society=society).annotate(
        upvote_count=Count('upvote')
    ).order_by('-upvote_count', '-created_at')
    review_form = ReviewForm()

    range_5 = range(1,6)

    context = {
        'society': society,
        'avg_rating': avg_rating,
        'user_rating': user_rating,
        'reviews': reviews,
        'review_form': review_form,
        'range_5': range_5,
    }
    return render(request, 'rango/society_detail.html', context)


@login_required
def rate_society(request, pk):
    society = get_object_or_404(Society, pk=pk)

    if request.method == 'POST':
        star = request.POST.get('star')
        if star:
            star = int(star)
            rating, created = Rating.objects.get_or_create(
                user=request.user,
                society=society,
                defaults={'star': star}
            )
            if not created:
                rating.star = star
                rating.save()
        return redirect('rango:society_detail', pk=society.pk)
    return redirect('rango:society_detail', pk=society.pk)

@login_required
def add_review(request, pk):
    society = get_object_or_404(Society, pk=pk)
    if request.method == 'POST':
        if Review.objects.filter(user=request.user, society=society).exists():
            messages.error(request, "You have already written a review for this society.")
            return redirect('rango:society_detail', pk=pk)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.society = society
            review.save()
    return redirect('rango:society_detail', pk=pk)

@login_required
def upvote_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    upvote, created = Upvote.objects.get_or_create(
        user=request.user,
        review=review
    )
    if not created:
        upvote.delete()  # toggle like
    return redirect('rango:society_detail', pk=review.society.pk)

def search_societies(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Society.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
    context = {
        'query': query,
        'results': results
    }
    return render(request, 'rango/search_results.html', context)

def top_rated_societies(request):
    N = 5
    societies = Society.objects.annotate(
        avg_rating=Avg('rating__star')
    ).filter(
        avg_rating__isnull=False
    ).order_by('-avg_rating')[:N]
    context = {
        'societies': societies,
        'N': N
    }
    return render(request, 'rango/top_societies.html', context)