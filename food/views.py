from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Food, Order, Review


# HOME PAGE
def home(request):

    foods = Food.objects.all()

    return render(request,'food/home.html',{
        'foods':foods
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

        return redirect('login')

    return render(request,'food/register.html')


# LOGIN
def login_user(request):

    if request.method == "POST":

        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.filter(email=email, password=password).first()

        if user:

            request.session['user_id'] = user.id

            # STAFF USER
            if user.is_staff:
                return redirect('admin_dashboard')

            # NORMAL USER
            else:
                return redirect('dashboard')

        else:
            return render(request,'food/login.html',{
                'error':'Invalid Email or Password'
            })

    return render(request,'food/login.html')


# LOGOUT
def logout_user(request):

    request.session.flush()

    return redirect('login')


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