from django.db import models

# Create your models here.

#These are test models for the API and just serve as examples
class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.CharField(max_length=50)

    @classmethod
    def create(cls, username, password, email):
        user = cls(username=username, password=password, email=email)
        return user

    def __str__(self):
        return self.username