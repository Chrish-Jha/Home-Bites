from django.db import models


# USER MODEL
class User(models.Model):

    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    # Admin / Staff control
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def profile_photo_url(self):
        if self.profile_photo:
            return self.profile_photo.url
        return '/media/Logo/Logo_Circular.jpeg'


# DELIVERY ADDRESS MODEL
class Address(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, default='Home')
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    landmark = models.CharField(max_length=150, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.label} - {self.user.name}"

    def formatted(self):
        parts = [self.address_line, self.city, self.state, self.pincode]
        if self.landmark:
            parts.insert(1, self.landmark)
        return ', '.join(parts)



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

    delivery_address = models.TextField(blank=True)

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