from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Product(models.Model):
	name = models.CharField(max_length=200)
	price = models.FloatField()
	digital = models.BooleanField(default=False,null=True, blank=True)
	image = models.ImageField(null=True, blank=True)

	def __str__(self):
		return self.name

	@property
	def imageURL(self):
		try:
			url = self.image.url
		except:
			url = ''
		return url

class Order(models.Model):
	customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)

	def __str__(self):
		return str(self.id)
		
