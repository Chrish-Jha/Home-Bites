from django.contrib import admin
from .models import User, Food, Order, Review


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'mobile_number', 'created_at')


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'food', 'quantity', 'total_price', 'status', 'order_date')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'food', 'rating', 'created_at')