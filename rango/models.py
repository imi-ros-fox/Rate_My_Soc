from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     bio = models.TextField(blank=True)  # optional?
#     picture = models.ImageField(upload_to='profile_images', blank=True)
#     role = models.CharField(max_length=50, default='student')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.user.username
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('STUDENT', 'Student'),
        ('PRESIDENT', 'Society President'),
    )

    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
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


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Society(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='society_images', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField('Category')
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Society, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Societies'

    def __str__(self):
        return self.name


#Makes sure profiles are always created when a new user signs up
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    society = models.ForeignKey(Society, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'society')  # one review per user per society

    def __str__(self):
        return f"{self.user.username} review of {self.society.name}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    society = models.ForeignKey(Society, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    star = models.IntegerField(choices=[(i, i) for i in range(1, 6)])

    class Meta:
        unique_together = ('user', 'society')  # one rating per user per society

    def __str__(self):
        return f"{self.user.username} rates {self.society.name} {self.star}"

class Upvote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'review')  # one upvote per user per society

    def __str__(self):
        return f"{self.user.username} upvotes review on {self.review.society.name}"