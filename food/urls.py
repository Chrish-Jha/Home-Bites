from django.urls import path
from . import views

urlpatterns = [

    # Home
    path('', views.home, name='home'),

    # User Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('logout/', views.logout_user, name='logout'),

    # Food
    path('foods/', views.food_list, name='food_list'),
    path('food/<int:id>/', views.food_detail, name='food_detail'),

    # Orders
    path('order/<int:food_id>/', views.place_order, name='place_order'),
    path('my-orders/', views.my_orders, name='my_orders'),

    # Profile & Addresses
    path('profile/', views.profile, name='profile'),
    path('address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('address/default/<int:address_id>/', views.set_default_address, name='set_default_address'),

    # Reviews
    path('review/<int:food_id>/', views.add_review, name='add_review'),


    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Order approve
    path('approve-order/<int:id>/', views.approve_order, name='approve_order'),

    # Order deliver
    path('deliver-order/<int:id>/', views.deliver_order, name='deliver_order'),

    path('add-food/', views.add_food, name='add_food'),

    path('admin-orders/', views.admin_orders, name='admin_orders'),

    path('admin-foods/', views.admin_foods, name='admin_foods'),
    path('delete-food/<int:id>/', views.delete_food, name='delete_food'),


    path('pay/<int:order_id>/', views.create_checkout_session, name='pay'),

    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),

    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),

]