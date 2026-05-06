from django.db import models


# USER MODEL
class User(models.Model):

    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    # Admin / Staff control
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



# FOOD MODEL
class Food(models.Model):

    name = models.CharField(max_length=150)

    description = models.TextField()

    price = models.DecimalField(max_digits=8, decimal_places=2)

    image = models.ImageField(upload_to='food_images/')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



# ORDER MODEL
class Order(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Delivered', 'Delivered'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    food = models.ForeignKey(Food, on_delete=models.CASCADE)

    quantity = models.IntegerField(default=1)

    total_price = models.DecimalField(max_digits=8, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.food.name}"



# REVIEW MODEL
class Review(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    food = models.ForeignKey(Food, on_delete=models.CASCADE)

    rating = models.IntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.food.name} - {self.rating}"