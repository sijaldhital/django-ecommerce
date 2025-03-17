from django.shortcuts import render, redirect
from . models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django.db.models import Q
import json
from cart.cart import Cart



def search(request):
    # Determine if they filled out the form
    if request.method == "POST":
        searched = request.POST['searched']
        # Query the Products DB Model
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        # Test for null
        if not searched:
            messages.error(request, ("Sorry, That Product Doesn't Exist!"))
            return render(request, 'store/search.html')
        else:
            return render(request, 'store/search.html', {'searched': searched})
    
    else: 
        return render(request, 'store/search.html')



def update_info(request):
    if request.user.is_authenticated:
         # Get Current User
         current_user = Profile.objects.get(user__id=request.user.id)
         # Get Current User's Shipping Address
         shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
         # Get original User Info Form
         form = UserInfoForm(request.POST or None, instance=current_user)
         # Get User's Shipping Form
         shipping_form = ShippingForm(request.POST or None, instance=shipping_user)


         if form.is_valid() or shipping_form.is_valid():
             # Save original form
             form.save()
             # Save shipping form
             shipping_form.save()
             messages.success(request, ("Your Info has been updated!"))
             return redirect('home')
         return render(request, 'store/update_info.html', {'form': form, 'shipping_form': shipping_form })
     
    else:
         messages.error(request, ("You must be logged in to update your account!"))
         return redirect('login')         


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill out the form
        if request.method == 'POST':
            # Do stuff
            form = ChangePasswordForm(current_user, request.POST)
            # Is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, ("Your Password Has Been Updated."))
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')

        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'store/update_password.html', {'form':form})
    else:
         messages.error(request, ("You must first Logged In to change the password!"))
         return redirect('home')
     

     
def update_user(request):
     if request.user.is_authenticated:
         current_user = User.objects.get(id=request.user.id)
         user_form = UpdateUserForm(request.POST or None, instance=current_user)

         if user_form.is_valid():
             user_form.save()

             login(request, current_user)
             messages.success(request, ("Your account has been updated!"))
             return redirect('home')
         return render(request, 'store/update_user.html', {'user_form': user_form})
     
     else:
         messages.error(request, ("You must be logged in to update your account!"))
         return redirect('login')
         
     

def category_summary(request):
     categories = Category.objects.all()
     return render(request, 'store/category_summary.html', {'categories': categories})

def category(request, foo):
    # Replace hyphens with spaces
    foo = foo.replace('-', ' ')
    # Get the category
    try:
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'store/category.html',{'products':products, 'category':category})

    except:
        messages.error(request, "That Category Doesn't Exist")
        return redirect('home')


def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'store/product.html', {'product':product})


def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products':products})

def about(request):
    return render(request, 'store/about.html')

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            # Get their save cart from the DB
            saved_cart = current_user.old_cart
            # Convert DB string to python dictionary
            if saved_cart:
                # Convert to dictionary using JSON
                converted_cart = json.loads(saved_cart)
                # Add the loaded cart dictionary to our session
                # Get the cart
                cart = Cart(request)
                # Loop through the cart and add items from the DB
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, "You are logged in")
            return redirect('home')
        else:
            messages.error(request, "There was an error logging in")
            return redirect('login')

    else:
        return render(request, 'store/login.html', )


def logout_user(request):
    logout(request)
    messages.success(request, "You are logged out")
    return redirect('home')


def register_user(request):
     form = SignUpForm()
     if request.method == "POST":
         form = SignUpForm(request.POST)
         if form.is_valid():
             form.save()
             username = form.cleaned_data['username']
             password = form.cleaned_data['password1']
             #login user
             user = authenticate(username=username, password=password)
             login(request, user)
             messages.success(request, "Username Created - Please Fill Out Your Additional Info Below..")
             return redirect ('update_info')
         else:
             messages.error(request, "There was an error registering your account. Please try again.")
             return redirect ('register')
     else:
         return render(request, 'store/register.html', {'form':form})
         
     
     