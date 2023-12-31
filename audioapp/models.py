from django.core.validators import MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db import models
from faker import Faker
import random
import os

fake = Faker()
testimonial = []
baseUrl = os.getenv("BASE_URL")
designations = ["Web & Integrations at Coverdash", "Marketing Director", "Entrepreneur, Professor, Author, Activist",
                "Writer"]
pixels = [340, 446, 200, 500, 400, 290]
platform = ["twitter", "instagram"]


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class Testimonial(models.Model):
    username = models.CharField(max_length=255)
    avatar = models.CharField(max_length=255, null=True, blank=True)
    rating = models.IntegerField(default=0, validators=[MaxValueValidator(5)])
    social_platform = models.CharField(max_length=255, null=True, blank=True)
    platform_handle = models.CharField(max_length=255, null=True, blank=True)
    post_image = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} Shared feedback from {self.social_platform}"


class SavedNote(models.Model):
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} saved a Note"


@receiver(post_migrate)
def create_initial_records(sender, **kwargs):
    if Testimonial.objects.count() == 0:
        for _ in range(100):
            testimonial.append({"username": fake.name(),
                                "avatar": f"{baseUrl}/{random.choice(pixels)}",
                                "rating": fake.random_int(min=1, max=5),
                                "social_platform": random.choice(platform),
                                "platform_handle": fake.user_name() if fake.boolean(chance_of_getting_true=50) else "",
                                "post_image": f"{baseUrl}/{random.choice(pixels)}/{random.choice(pixels)}" if fake.boolean(
                                    chance_of_getting_true=10) else "",
                                "description": fake.paragraph(nb_sentences=random.randint(5, 10))
                                })
        objs = [
            Testimonial(
                username=row['username'],
                avatar=row['avatar'],
                rating=row['rating'],
                social_platform=row['social_platform'] if row['platform_handle'] else '',
                platform_handle=f"@{row['platform_handle']}" if row['platform_handle'] else random.choice(designations),
                post_image=row['post_image'],
                description=row['description']

            )
            for row in testimonial
        ]
        Testimonial.objects.bulk_create(objs)
