from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL

class Ingredient(models.Model):

    name = models.CharField(max_length=255, null=True, blank=True)
    details = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ingredients")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):

    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    ingredients = models.ManyToManyField(Ingredient, related_name="recipes", blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
