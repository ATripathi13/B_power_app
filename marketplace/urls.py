from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Main marketplace
    path('', views.marketplace_home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('seller/<int:seller_id>/', views.seller_products, name='seller_products'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    path('ajax/filter/', views.ajax_filter_products, name='ajax_filter'),
    
    # Authentication
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/seller/', views.seller_register, name='seller_register'),
    path('register/buyer/', views.buyer_register, name='buyer_register'),
    
    # Dashboards
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    
    # Product Management
    path('product/add/', views.add_product, name='add_product'),
    
    # Financial
    path('credit/add/', views.add_credit, name='add_credit'),
    path('order/place/<int:product_id>/', views.place_order, name='place_order'),
    
    # Admin Views
    path('admin/transactions/', views.admin_transactions, name='admin_transactions'),
    path('admin/approve/seller/<int:seller_id>/', views.admin_approve_seller, name='admin_approve_seller'),
    path('admin/approve/buyer/<int:buyer_id>/', views.admin_approve_buyer, name='admin_approve_buyer'),
    path('admin/approve/product/<int:product_id>/', views.admin_approve_product, name='admin_approve_product'),
]
