from django.db.models import Avg, Count, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import User, Food, Order, Review, Address
from .utils import require_session_user


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

    if 'user_id' in request.session:
        return redirect('dashboard')

    if request.method == "POST":

        name = request.POST.get('name', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        errors = []

        if not name:
            errors.append('Full name is required.')
        if not mobile:
            errors.append('Mobile number is required.')
        elif not mobile.isdigit() or len(mobile) < 10:
            errors.append('Enter a valid 10-digit mobile number.')
        if not email:
            errors.append('Email address is required.')
        if not password:
            errors.append('Password is required.')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters.')

        if email and User.objects.filter(email=email).exists():
            errors.append('An account with this email already exists. Please log in.')

        if errors:
            return render(request, 'food/register.html', {
                'errors': errors,
                'name': name,
                'mobile': mobile,
                'email': email,
            })

        User.objects.create(
            name=name,
            mobile_number=mobile,
            email=email,
            password=password,
        )

        return redirect(f'{reverse("login")}?registered=1')

    return render(request, 'food/register.html')


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

    user = require_session_user(request)
    if not user:
        return redirect('login')

    orders = Order.objects.filter(user=user)
    reviews = Review.objects.filter(user=user)

    foods = Food.objects.annotate(
        avg_rating=Avg('review__rating'),
    ).order_by('-created_at')[:6]

    recent_orders = orders.select_related('food').order_by('-order_date')[:5]

    return render(request, 'food/dashboard.html', {
        'user': user,
        'active_nav': 'dashboard',
        'foods': foods,
        'orders': orders,
        'reviews': reviews,
        'recent_orders': recent_orders,
        'pending_orders': orders.filter(status='Pending').count(),
        'delivered_orders': orders.filter(status='Delivered').count(),
        'total_spent': orders.aggregate(total=Sum('total_price'))['total'] or 0,
    })


# FOOD LIST
def food_list(request):

    user = require_session_user(request)
    if not user:
        return redirect('login')

    foods = Food.objects.annotate(
        avg_rating=Avg('review__rating'),
    ).order_by('name')

    return render(request, 'food/food_list.html', {
        'user': user,
        'active_nav': 'menu',
        'foods': foods,
    })


# FOOD DETAIL
def food_detail(request, id):

    user = require_session_user(request)
    if not user:
        return redirect('login')

    food = get_object_or_404(
        Food.objects.annotate(avg_rating=Avg('review__rating')),
        id=id,
    )

    reviews = Review.objects.filter(food=food).select_related('user')

    return render(request, 'food/food_detail.html', {
        'user': user,
        'active_nav': 'menu',
        'food': food,
        'reviews': reviews,
    })


# PLACE ORDER
def place_order(request, food_id):

    user = require_session_user(request)
    if not user:
        return redirect('login')

    food = get_object_or_404(Food, id=food_id)
    addresses = Address.objects.filter(user=user)

    if request.method == "POST":

        quantity = int(request.POST.get('quantity'))
        address_id = request.POST.get('address_id')
        total_price = quantity * food.price

        delivery_text = ''
        if address_id:
            address = Address.objects.filter(id=address_id, user=user).first()
            if address:
                delivery_text = address.formatted()

        order = Order.objects.create(
            user=user,
            food=food,
            quantity=quantity,
            total_price=total_price,
            delivery_address=delivery_text,
        )

        return redirect('pay', order_id=order.id)

    return render(request, 'food/place_order.html', {
        'user': user,
        'active_nav': 'menu',
        'food': food,
        'addresses': addresses,
    })


# PROFILE
def profile(request):

    user = require_session_user(request)
    if not user:
        return redirect('login')

    errors = []

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'photo':
            photo = request.FILES.get('profile_photo')
            if photo:
                user.profile_photo = photo
                user.save()
            else:
                errors.append('Please select a photo to upload.')
        elif action == 'add_address':
            label = request.POST.get('label', '').strip() or 'Home'
            address_line = request.POST.get('address_line', '').strip()
            city = request.POST.get('city', '').strip()
            state = request.POST.get('state', '').strip()
            pincode = request.POST.get('pincode', '').strip()
            landmark = request.POST.get('landmark', '').strip()
            is_default = request.POST.get('is_default') == 'on'

            if not address_line:
                errors.append('Address line is required.')
            if not city:
                errors.append('City is required.')
            if not state:
                errors.append('State is required.')
            if not pincode:
                errors.append('Pincode is required.')

            if not errors:
                if is_default:
                    Address.objects.filter(user=user).update(is_default=False)

                Address.objects.create(
                    user=user,
                    label=label,
                    address_line=address_line,
                    city=city,
                    state=state,
                    pincode=pincode,
                    landmark=landmark,
                    is_default=is_default or not Address.objects.filter(user=user).exists(),
                )

        if not errors:
            return redirect('profile')

    addresses = Address.objects.filter(user=user)

    return render(request, 'food/profile.html', {
        'user': user,
        'active_nav': 'profile',
        'addresses': addresses,
        'errors': errors,
    })


def delete_address(request, address_id):

    user = require_session_user(request)
    if not user:
        return redirect('login')

    if request.method != 'POST':
        return redirect('profile')

    address = get_object_or_404(Address, id=address_id, user=user)
    was_default = address.is_default
    address.delete()

    if was_default:
        next_address = Address.objects.filter(user=user).first()
        if next_address:
            next_address.is_default = True
            next_address.save()

    return redirect('profile')


def set_default_address(request, address_id):

    user = require_session_user(request)
    if not user:
        return redirect('login')

    if request.method != 'POST':
        return redirect('profile')

    address = get_object_or_404(Address, id=address_id, user=user)
    Address.objects.filter(user=user).update(is_default=False)
    address.is_default = True
    address.save()

    return redirect('profile')


# MY ORDERS
def my_orders(request):

    user = require_session_user(request)
    if not user:
        return redirect('login')

    orders = Order.objects.filter(user=user).select_related('food').order_by('-order_date')

    return render(request, 'food/my_orders.html', {
        'user': user,
        'active_nav': 'orders',
        'orders': orders,
        'pending_orders': orders.filter(status='Pending').count(),
        'accepted_orders': orders.filter(status='Accepted').count(),
        'delivered_orders': orders.filter(status='Delivered').count(),
        'total_spent': orders.aggregate(total=Sum('total_price'))['total'] or 0,
    })


# ADD REVIEW
def add_review(request, food_id):

    user = require_session_user(request)
    if not user:
        return redirect('login')

    food = get_object_or_404(Food, id=food_id)

    if request.method == "POST":

        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Review.objects.create(
            user=user,
            food=food,
            rating=rating,
            comment=comment
        )

        return redirect('food_detail', id=food_id)

    return render(request, 'food/add_review.html', {
        'user': user,
        'active_nav': 'menu',
        'food': food,
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

    user = require_session_user(request)
    if not user:
        return redirect('login')

    order = get_object_or_404(Order, id=order_id, user=user)

    order.status = "Accepted"
    order.save()

    return render(request, 'food/payment_success.html', {
        'user': user,
        'active_nav': 'orders',
        'order': order,
    })

def payment_cancel(request):

    user = require_session_user(request)
    if not user:
        return redirect('login')

    return render(request, 'food/payment_cancel.html', {
        'user': user,
        'active_nav': 'orders',
    })