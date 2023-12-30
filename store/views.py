import datetime
import json
 
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
import requests

from store.models import Order, OrderItem, Product, ShippingAddress
from .forms import CustomUserCreationForm
from .utils import cookieCart, cartData, guestOrder
import http.client
import json
import os
from dotenv import load_dotenv
import uuid
import datetime

load_dotenv()  # Load environment variables from .env file
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
from django.contrib.auth.decorators import user_passes_test

def superuser_required(function=None, redirect_field_name=None, login_url='login'):
    """
    Decorator for views that checks that the user is a superuser.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def Home(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.all()
    context = {'title_variable': 'Home','products':products,'cartItems':cartItems,'items':items, 'order':order}
    return render(request,'Home.html',context)

def store(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.all()
    
    context = {'title_variable': 'Store','products':products,'cartItems':cartItems,'items':items, 'order':order}
    return render(request, 'store.html', context)

def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'checkout.html', context)

@superuser_required(login_url='home')
def dashboard(request):
	orders = Order.objects.filter(complete=True)
	context = {'orders':orders}
	return render(request,'dashboard.html',context)
@superuser_required(login_url='home')
def orderdetail(request,id):
	order = Order.objects.get(complete=True,id=id)
	customer = order.customer
	items = order.orderitem_set.all()
	cartItems = order.get_cart_items
	context = {'dashboardorder':order,'items':items,'cartItems':cartItems,'customer':customer}
	return render(request,'orderdetail.html',context)

def updateItem(request):
	data = json.loads(request.body)
      
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	data = json.loads(request.body)
	total = float(data['form']['total'])
	email = data['form']['email']
	first_name = data['form']['first_name']
	last_name = data['form']['last_name']
	phone = data['form']['phone']
	address=data['shipping']['address'],
	city=data['shipping']['city'],
	unique_uuid = uuid.uuid4()  # Generate a random UUID
	timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")  # Get a formatted timestamp
	unique_transaction_number = f"{unique_uuid}{timestamp}" 
	payload = {
		"amount": total,
		"currency": "ETB",
		"email": email,
		"first_name": first_name,
		"last_name": last_name,
		"phone_number": phone,
		"tx_ref": f"{unique_transaction_number}",
		"callback_url": "http://127.0.0.1:8000/callback/",
		"return_url": "http://127.0.0.1:8000/checkout/",
		"customization": {
			"title": "Payment ",
			"description": "I love payment"
		}
	}
    
	headers = {
	'Authorization': f'Bearer {PRIVATE_KEY}',
	'Content-Type': 'application/json'
	}
    
	response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)

	# Check if the request was successful
	if response.status_code == 200:
		# Parse the JSON response into a Python object
		data = response.json()
		checkout_url = data['data']['checkout_url']
		print(data)  # This will print the Python object
		print('response url:',checkout_url)
		if request.user.is_authenticated:
			customer = request.user.customer
			customer.phone = phone
			customer.save()
			order, created = Order.objects.get_or_create(customer=customer, complete=False)
		else:
			customer, order = guestOrder(request, first_name,email,phone)

		order.transaction_id = unique_transaction_number
		order.save()
		if order.shipping == True:
			ShippingAddress.objects.create(
			customer=customer,
			order=order,
			address=address,
			city=city,
			)
		return JsonResponse(checkout_url,safe=False)
	else:
		print(f"Failed to fetch data. Status code: {response.status_code}. Response: {response.text}")
     
		return JsonResponse({"error": "Failed to initialize payment"}, status=400)

     
	



	# if total == order.get_cart_total:
	# 	order.complete = True
	# order.save()


def chapa_callback(request):
	# transaction_id ='464b2c77-c713-4b78-803e-d613b34d4ed520231228195651110662'
	
	transaction_id = request.GET.get('trx_ref')
	print('this is request',request)
    
	print('this is transaction number',transaction_id)
      
	payload = ''
	headers = {
		'Authorization': f'Bearer {PRIVATE_KEY}',
	}
	response = requests.get(f"https://api.chapa.co/v1/transaction/verify/{transaction_id}", headers=headers)
	data = response.json()
	print('this is the callback response:',response.json())
	print('this is the status:',data['status'])
      

	if data['status'] == "success":
		# Retrieve order data (adjust retrieval logic if needed)
		order = Order.objects.get(transaction_id=transaction_id)

		# Process order completion and order status
		order.complete = True
		order.order_status = 'fulfilled'
		order.save()

		messages.success(request, "Payment successful! Your order has been processed.")
		return redirect("/checkout")
	else:
		messages.error(request, "Payment verification failed.")
		return redirect("/checkout")  # Or redirect to error page	 

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
