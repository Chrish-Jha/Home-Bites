from django.db.models import Avg, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import User, Food, Order, Review


# HOME PAGE
def home(request):

    popular_foods = Food.objects.annotate(
        avg_rating=Avg('review__rating'),
        order_count=Count('order'),
    ).order_by('-order_count', '-avg_rating')[:6]

    testimonials = Review.objects.select_related('user', 'food').order_by('-created_at')[:3]

    current_user = None
    if 'user_id' in request.session:
        current_user = User.objects.filter(id=request.session['user_id']).first()

    return render(request, 'food/home.html', {
        'popular_foods': popular_foods,
        'testimonials': testimonials,
        'current_user': current_user,
        'chef_count': User.objects.filter(is_staff=False).count(),
        'food_count': Food.objects.count(),
        'order_count': Order.objects.filter(status='Delivered').count(),
        'happy_customers': Order.objects.values('user').distinct().count(),
    })


# REGISTER
def register(request):

    if request.method == "POST":

        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User(
            name=name,
            mobile_number=mobile,
            email=email,
            password=password
        )

        user.save()

        return redirect(f'{reverse("login")}?registered=1')

    return render(request,'food/register.html')


# LOGIN
def login_user(request):

    if 'user_id' in request.session:
        user = User.objects.filter(id=request.session['user_id']).first()
        if user:
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('dashboard')

    if request.method == "POST":

        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = User.objects.filter(email=email, password=password).first()

        if user:

            request.session['user_id'] = user.id

            if user.is_staff:
                return redirect('admin_dashboard')

            return redirect('dashboard')

        return render(request, 'food/login.html', {
            'error': 'Invalid email or password. Please try again.',
            'email': email,
        })

    return render(request, 'food/login.html', {
        'success': request.GET.get('registered'),
    })


# LOGOUT
def logout_user(request):

    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.filter(id=request.session['user_id']).first()

    if request.method == "POST":
        request.session.flush()
        return render(request, 'food/logout.html', {
            'logged_out': True,
        })

    return render(request, 'food/logout.html', {
        'logged_out': False,
        'user': user,
    })


# USER DASHBOARD
def dashboard(request):

    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])

    foods = Food.objects.all()

    orders = Order.objects.filter(user=user)

    reviews = Review.objects.filter(user=user)

    return render(request,'food/dashboard.html',{
        'foods':foods,
        'orders':orders,
        'reviews':reviews
    })


# FOOD LIST
def food_list(request):

    foods = Food.objects.all()

    return render(request,'food/food_list.html',{
        'foods':foods
    })


# FOOD DETAIL
def food_detail(request,id):

    food = get_object_or_404(Food,id=id)

    reviews = Review.objects.filter(food=food)

    return render(request,'food/food_detail.html',{
        'food':food,
        'reviews':reviews
    })


# PLACE ORDER
def place_order(request, food_id):

    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    food = Food.objects.get(id=food_id)

    if request.method == "POST":

        quantity = int(request.POST.get('quantity'))

        total_price = quantity * food.price

        order = Order.objects.create(
            user=user,
            food=food,
            quantity=quantity,
            total_price=total_price
        )

        # Redirect to payment
        return redirect('pay', order_id=order.id)

    return render(request,'food/place_order.html',{
        'food':food
    })


# MY ORDERS
def my_orders(request):

    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])

    orders = Order.objects.filter(user=user).order_by('-order_date')

    return render(request,'food/my_orders.html',{
        'orders':orders
    })


# ADD REVIEW
def add_review(request,food_id):

    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])

    food = Food.objects.get(id=food_id)

    if request.method == "POST":

        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Review.objects.create(
            user=user,
            food=food,
            rating=rating,
            comment=comment
        )

        return redirect('food_detail',id=food_id)

    return render(request,'food/add_review.html',{
        'food':food
    })


# ==============================
# ADMIN DASHBOARD
# ==============================

from django.http import JsonResponse

def admin_dashboard(request):

    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])

    # Only staff allowed
    if not user.is_staff:
        return redirect('dashboard')

    users = User.objects.all()
    foods = Food.objects.all()
    orders = Order.objects.all()
    pending_orders = Order.objects.filter(status='Pending')

    return render(request,'food/admin_dashboard.html',{
        'users':users,
        'foods':foods,
        'orders':orders,
        'pending_orders':pending_orders
    })


# APPROVE ORDER (ADMIN ONLY)
def approve_order(request,id):

    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])

    if not user.is_staff:
        return redirect('dashboard')

    order = Order.objects.get(id=id)

    order.status = "Accepted"
    order.save()

    return redirect('admin_dashboard')


# DELIVER ORDER (ADMIN ONLY)
def deliver_order(request,id):

    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])

    if not user.is_staff:
        return redirect('dashboard')

    order = Order.objects.get(id=id)

    order.status = "Delivered"
    order.save()

    return redirect('admin_dashboard')

# add food (Admin Only)

def add_food(request):

    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])

    # Only staff can add food
    if not user.is_staff:
        return redirect('dashboard')

    if request.method == "POST":

        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.FILES.get('image')

        Food.objects.create(
            name=name,
            description=description,
            price=price,
            image=image
        )

        return redirect('admin_dashboard')

    return render(request,'food/add_food.html')

def admin_orders(request):

    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])

    # Only staff allowed
    if not user.is_staff:
        return redirect('dashboard')

    orders = Order.objects.select_related('user','food').order_by('-order_date')

    return render(request,'food/admin_orders.html',{
        'orders':orders
    })


def admin_foods(request):

    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])

    if not user.is_staff:
        return redirect('dashboard')

    foods = Food.objects.all()

    return render(request,'food/admin_foods.html',{
        'foods':foods
    })


def delete_food(request,id):

    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])

    if not user.is_staff:
        return redirect('dashboard')

    food = Food.objects.get(id=id)
    food.delete()

    return redirect('admin_foods')


import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request, order_id):

    order = Order.objects.get(id=order_id)

    session = stripe.checkout.Session.create(

        payment_method_types=['card'],

        line_items=[{
            'price_data':{
                'currency':'inr',
                'product_data':{
                    'name': order.food.name,
                },
                'unit_amount': int(order.total_price * 100),
            },
            'quantity':1,
        }],

        mode='payment',

        success_url=f'{settings.SITE_URL}/payment-success/{order.id}/',

        cancel_url=f'{settings.SITE_URL}/payment-cancel/',

    )

    return redirect(session.url)

def payment_success(request, order_id):

    order = Order.objects.get(id=order_id)

    order.status = "Accepted"
    order.save()

    return render(request,'food/payment_success.html',{
        'order':order
    })

def payment_cancel(request):

    return render(request,'food/payment_cancel.html')