from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)  # optional?
    picture = models.ImageField(upload_to='profile_images', blank=True)
    role = models.CharField(max_length=50, default='student')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Society(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='society_images', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('STUDENT', 'Student'),
        ('PRESIDENT', 'Society President'),
    )

    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    
    #Added a bio - eg. in personas it mentions Ayaan might want to mention he's looking for beginner-friendly sports
    bio = models.TextField(blank=True, max_length=500)

    #Added a join date - could be used for filtering members? 
    join_date = models.DateTimeField(auto_now_add=True)

    #MIGHT WANT TO ADD FEATURES TO TRACK USER ACTIVITY HERE

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name_plural = 'User Profiles'

#Makes sure profiles are always created when a new user signs up
@receiver
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)

    class Meta:
        unique_together = ('user', 'review')  # one upvote per user per review

    def __str__(self):
        return f"{self.user.username} upvoted review {self.review.id}"