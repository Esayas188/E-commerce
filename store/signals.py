from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.contrib.auth.models import User
from .models import Customer

from django.core.mail import send_mail
from django.conf import settings

# @receiver(post_save, sender=Profile)


def createCustomer(sender, instance, created, **kwargs):
    print("createCustomer signal triggered!")
    print('let us see created: ',created)
    if created:
        user = instance
        customer = Customer.objects.create(
            user=user,
            name=user.username,
            email=user.email,

        )
def updateCustomer(sender, instance, created, **kwargs):
    user = instance
    customer = Customer.objects.get(user=user)
    print('this is customer',customer.name)

    if created == False:
        customer.name = user.username
        customer.email = user.email
        customer.save()
# def updateUser(sender, instance, created, **kwargs):
#     customer = instance
#     user = customer.user

#     if not created:
#         user.username = customer.name
#         user.email = customer.email
#         user.save()


def deleteUser(sender, instance, **kwargs):
    try:
        user = instance.user
        user.delete()
    except:
        pass


post_save.connect(createCustomer, sender=User)
post_save.connect(updateCustomer, sender=User)

# post_save.connect(updateUser, sender=Customer)
post_delete.connect(deleteUser, sender=Customer)
