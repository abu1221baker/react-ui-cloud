from django.urls import path
from .views import *

urlpatterns = [
    path('register/', registration_view, name='register'),
    path('login/', login_view, name='login'),
    
    path('products/', product_list_create_view, name='product-list-create'),
    path('products/<uuid:pk>/', product_detail_view, name='product-detail'),
    
    path('orders/', order_list_create_view, name='order-list-create'),
    path('orders/<uuid:pk>/', order_detail_view, name='order-detail'),
    path('orders/<uuid:pk>/status/', order_status_update_view, name='order-status-update'),

    path('wishlist/', wishlist_list_create_view, name='wishlist-list-create'),
    path('wishlist/<uuid:pk>/', wishlist_delete_view, name='wishlist-delete'),

    path('profile/', profile_view, name='profile'),
]
