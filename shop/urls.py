from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("pet/<int:pet_id>/", views.pet_detail, name="pet_detail"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("cart/add/<int:pet_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="cart"),
    path("cart/remove/<int:pet_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("order/success/<int:order_id>/", views.order_success, name="order_success"),
    path("admin-login/", views.admin_login, name="admin_login"),
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/pet/add/", views.admin_add_edit_pet, name="admin_add_pet"),
    path("admin/pet/edit/<int:pet_id>/", views.admin_add_edit_pet, name="admin_edit_pet"),
    path("admin/pet/delete/<int:pet_id>/", views.admin_delete_pet, name="admin_delete_pet"),
    path("admin/orders/", views.admin_orders, name="admin_orders"),
]
