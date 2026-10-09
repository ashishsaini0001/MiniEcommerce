from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path(
        "add-to-cart/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),
    path("cart/",views.cart,name="cart"),
    path(
        "remove-from-cart/<int:item_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),
    path(
    "update-cart/<int:item_id>/<str:action>/",
    views.update_cart,
    name="update_cart"
),
path("checkout/", views.checkout, name="checkout"),
path(
    "product/<int:product_id>/",
    views.product_detail,
    name="product_detail"
),
path("register/", views.register, name="register"),
path("login/", views.user_login, name="login"),
path("logout/", views.user_logout, name="logout"),
path("my-orders/", views.my_orders, name="my_orders"),
]