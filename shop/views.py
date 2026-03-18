from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from .models import Pet, Order
from .forms import RegisterForm, LoginForm, PetForm
import json
from decimal import Decimal

def home(request):
    pets = Pet.objects.all()
    return render(request, "shop/home.html", {"pets": pets})

def pet_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    return render(request, "shop/pet_detail.html", {"pet": pet})

def register_view(request):
    if request.user.is_authenticated:
        return redirect("shop:home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data.get("email", ""),
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data.get("first_name", ""),
            )
            messages.success(request, "Registration successful. Please log in.")
            return redirect("shop:login")
    else:
        form = RegisterForm()
    return render(request, "shop/register_login.html", {"form": form, "is_register": True})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("shop:home")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
            if user:
                login(request, user)
                return redirect("shop:home")
            else:
                messages.error(request, "Invalid credentials")
    else:
        form = LoginForm()
    return render(request, "shop/register_login.html", {"form": form, "is_register": False})

def logout_view(request):
    logout(request)
    return redirect("shop:home")

def _get_cart(request):
    return request.session.get("cart", {})

def _save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True

def add_to_cart(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    cart = _get_cart(request)
    str_id = str(pet_id)
    if str_id in cart:
        cart[str_id]["quantity"] += 1
    else:
        cart[str_id] = {
            "name": pet.name,
            "price": str(pet.price),
            "quantity": 1,
        }
    _save_cart(request, cart)
    messages.success(request, f"Added {pet.name} to the cart.")
    return redirect("shop:cart")

def view_cart(request):
    cart = _get_cart(request)
    items = []
    total = Decimal("0.00")
    for pid, info in cart.items():
        qty = info["quantity"]
        price = Decimal(info["price"])
        subtotal = price * qty
        items.append({"pet_id": int(pid), "name": info["name"], "price": price, "quantity": qty, "subtotal": subtotal})
        total += subtotal
    return render(request, "shop/cart.html", {"items": items, "total": total})

def remove_from_cart(request, pet_id):
    cart = _get_cart(request)
    pid = str(pet_id)
    if pid in cart:
        del cart[pid]
        _save_cart(request, cart)
        messages.success(request, "Item removed from cart.")
    return redirect("shop:cart")

def checkout(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please login/register to checkout.")
        return redirect("shop:login")
    cart = _get_cart(request)
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("shop:home")
    items_list = []
    total = Decimal("0.00")
    for pid, info in cart.items():
        quantity = info["quantity"]
        price = Decimal(info["price"])
        total += price * quantity
        items_list.append({"pet_id": pid, "name": info["name"], "price": str(price), "quantity": quantity})
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        address = request.POST.get("address", "").strip()
        if not name or not address:
            messages.error(request, "Please fill shipping name and address.")
            return render(request, "shop/checkout.html", {"items": items_list, "total": total})
        order = Order.objects.create(
            user=request.user,
            total=total,
            items_snapshot=json.dumps(items_list),
            paid=True,
        )
        _save_cart(request, {})
        messages.success(request, "Payment successful and order placed.")
        return redirect("shop:order_success", order_id=order.id)
    return render(request, "shop/checkout.html", {"items": items_list, "total": total})

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    try:
        items = json.loads(order.items_snapshot)
    except:
        items = []
    return render(request, "shop/order_success.html", {"order": order, "items": items})

def admin_login(request):
    if request.session.get("is_admin"):
        return redirect("shop:admin_dashboard")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username == settings.FIXED_ADMIN_USERNAME and password == settings.FIXED_ADMIN_PASSWORD:
            request.session["is_admin"] = True
            return redirect("shop:admin_dashboard")
        else:
            messages.error(request, "Invalid admin credentials.")
    return render(request, "shop/admin_login.html")

def admin_logout(request):
    request.session.pop("is_admin", None)
    return redirect("shop:admin_login")

def _admin_required(fn):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("is_admin"):
            return redirect("shop:admin_login")
        return fn(request, *args, **kwargs)
    return wrapper

@_admin_required
def admin_dashboard(request):
    pets = Pet.objects.all()
    return render(request, "shop/admin_dashboard.html", {"pets": pets})

@_admin_required
def admin_add_edit_pet(request, pet_id=None):
    pet = None
    if pet_id:
        pet = get_object_or_404(Pet, id=pet_id)
    if request.method == "POST":
        form = PetForm(request.POST, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, "Pet saved.")
            return redirect("shop:admin_dashboard")
    else:
        form = PetForm(instance=pet)
    return render(request, "shop/admin_add_edit_pet.html", {"form": form, "pet": pet})

@_admin_required
def admin_delete_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    pet.delete()
    messages.success(request, "Pet deleted.")
    return redirect("shop:admin_dashboard")

@_admin_required
def admin_orders(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "shop/admin_orders.html", {"orders": orders})
