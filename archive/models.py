from django.db import models

# Create your models here.
class Profile(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    activite = models.CharField(max_length=1000)
    contrat = models.TextField()
    articles = models.TextField()
    materiels = models.TextField()
    date_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-date_added']
