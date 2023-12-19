from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User

from store.models import Product
from .forms import CustomUserCreationForm


def Home(request):
    context = {
        'title_variable': 'Home',
        
    }
    return render(request,'Home.html',context)

def store(request):

	products = Product.objects.all()
    
	context = {'products':products,'title_variable': 'Store'}
	return render(request, 'store.html', context)

def cart(request):


	context = {}
	return render(request, 'cart.html', context)
def checkout(request):

	context = {}
	return render(request, 'checkout.html', context)

def loginUser(request):
    title_variable = 'login'
    

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'home')

        else:
            messages.error(request, 'Username OR password is incorrect')

    return render(request, 'login_register.html',{'title_variable':title_variable})


def logoutUser(request):
    logout(request)
    messages.info(request, 'User was logged out!')
    return redirect('login')


def registerUser(request):
    title_variable = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(request, 'User account was created!')

            login(request, user)
            return redirect('home')

        else:
            messages.success(
                request, 'An error has occurred during registration')

    context = {'title_variable':title_variable, 'form': form}
    return render(request, 'login_register.html', context)
