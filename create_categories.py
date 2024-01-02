from django.db import models
from store.models import Category, Department
# Create the Department
department, created = Department.objects.get_or_create(name="Clothing & Fashion")

# Create the top-level parent category "Women's Clothing"
parent_category, created = Category.objects.get_or_create(
    name="Women's Clothing",
    department=department
)

# Create the second-level parent category "Top" under "Women's Clothing"
top_category, created = Category.objects.get_or_create(
    name="Footwear",
    parent=parent_category,
    department=department
)

# Create the individual categories under "Top"
categories = [

    "Flats",
    "Heels",
    "Boots (ankle, knee-high, over-the-knee)",
    "Sneakers",
    "Sandals",
    "Wedges",
    "Loafers",
    "Espadrilles",
    "Mules",
    "Slippers",
]

for category_name in categories:
    category, created = Category.objects.get_or_create(
        name=category_name,
        parent=parent_category,
        parenttwo=top_category,

        department=department
    )
