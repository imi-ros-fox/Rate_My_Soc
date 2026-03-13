from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

# Create your models here.
# class Category(models.Model):
#     name = models.CharField(max_length=128, unique=True)
#     views = models.IntegerField(default=0)
#     likes = models.IntegerField(default=0)
#     slug = models.SlugField(unique=True)
#
#     def save(self, *args, **kwargs):
#         self.slug = slugify(self.name)
#         super(Category, self).save(*args, **kwargs)
#
#     class Meta:
#         verbose_name_plural = 'Categories'
#
#     def __str__(self):
#         return self.name
    

# class Page(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     title = models.CharField(max_length=128)
#     url = models.URLField()
#     views = models.IntegerField(default=0)
#
#     def __str__(self):
#         return self.title

class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username

class Society(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=300)
    picture = models.ImageField(upload_to='society_images', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Society, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Societies'

    def __str__(self):
        return self.name