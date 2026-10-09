from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from .models import Product, CartItem, Order, OrderItem
from django.contrib.auth.decorators import login_required


def home(request):
    products = Product.objects.all()

    search_query = request.GET.get("q")

    if search_query:
        products = products.filter(
            name__icontains=search_query
        )

    if request.user.is_authenticated:
        cart_count = sum(
            item.quantity
            for item in CartItem.objects.filter(
                user=request.user
            )
        )
    else:
        cart_count = 0

    return render(request, "shop/home.html", {
        "products": products,
        "cart_count": cart_count,
    })


def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)

    return render(request, "shop/product_detail.html", {
        "product": product
    })


@login_required(login_url="login")
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    # Stock available नहीं है
    if product.stock <= 0:
        return redirect("home")

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    # Stock से ज्यादा quantity नहीं होने देंगे
    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()

    return redirect("home")


@login_required(login_url="login")
def cart(request):
    cart_items = CartItem.objects.filter(
        user=request.user
    )

    total = sum(
        item.total_price()
        for item in cart_items
    )

    return render(request, "shop/cart.html", {
        "cart_items": cart_items,
        "total": total,
    })


@login_required(login_url="login")
def remove_from_cart(request, item_id):
    cart_item = CartItem.objects.get(
        id=item_id,
        user=request.user
    )

    cart_item.delete()

    return redirect("cart")


@login_required(login_url="login")
def update_cart(request, item_id, action):
    cart_item = CartItem.objects.filter(
        id=item_id,
        user=request.user
    ).first()

    if not cart_item:
        return redirect("cart")

    if action == "increase":

        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()

    elif action == "decrease":

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    return redirect("cart")


@login_required(login_url="login")
def checkout(request):
    cart_items = CartItem.objects.filter(
        user=request.user
    )

    if not cart_items.exists():
        return redirect("cart")

    total = sum(
        item.total_price()
        for item in cart_items
    )

    if request.method == "POST":
        name = request.POST.get("name")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        city = request.POST.get("city")
        pincode = request.POST.get("pincode")

        # Check stock again before placing order
        for item in cart_items:
            if item.quantity > item.product.stock:
                return redirect("cart")

        # Create Order
        order = Order.objects.create(
            user=request.user,
            name=name,
            mobile=mobile,
            address=address,
            city=city,
            pincode=pincode,
            total_amount=total,
        )

        # Save products inside the order
        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

            # Reduce product stock
            item.product.stock -= item.quantity
            item.product.save()

        # Empty only current user's cart
        cart_items.delete()

        return redirect("home")

    return render(request, "shop/checkout.html", {
        "cart_items": cart_items,
        "total": total,
    })


@login_required(login_url="login")
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request, "shop/my_orders.html", {
        "orders": orders
    })


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "shop/register.html", {
                "error": "Username already exists."
            })

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect("login")

    return render(request, "shop/register.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("home")

        return render(request, "shop/login.html", {
            "error": "Invalid username or password."
        })

    return render(request, "shop/login.html")


def user_logout(request):
    logout(request)

    return redirect("home")