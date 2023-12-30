from django.contrib import admin
from .models import Customer,Order,OrderItem,Product,ShippingAddress,Department,Category

# Register your models here.
admin.site.register(Department)
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Product)
admin.site.register(ShippingAddress)
