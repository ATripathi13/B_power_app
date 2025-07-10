from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Seller, Buyer, Product, ProductImage, PODCustomization, 
    ProductReview, Order, OrderItem, Transaction, CreditTransaction
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = [
        'business_name', 'owner_name', 'user', 'gstin', 'city', 'state', 
        'business_type', 'approval_status_badge', 'verified', 'turnover', 'created_at'
    ]
    list_filter = ['business_type', 'verified', 'approval_status', 'state']
    search_fields = ['business_name', 'owner_name', 'user__username', 'city', 'gstin']
    ordering = ['-created_at']
    list_editable = ['verified']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'owner_name')
        }),
        ('Business Details', {
            'fields': ('business_name', 'business_type', 'gstin', 'turnover')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address', 'city', 'state', 'pincode')
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'account_number', 'ifsc_code', 'account_holder_name')
        }),
        ('Documents', {
            'fields': ('pan_document', 'gst_certificate')
        }),
        ('Approval Status', {
            'fields': ('approval_status', 'verified', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def approval_status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.approval_status, 'gray'),
            obj.get_approval_status_display()
        )
    approval_status_badge.short_description = 'Status'
    
    actions = ['approve_sellers', 'reject_sellers']
    
    def approve_sellers(self, request, queryset):
        updated = queryset.update(approval_status='approved', verified=True)
        self.message_user(request, f'{updated} sellers approved successfully.')
    approve_sellers.short_description = 'Approve selected sellers'
    
    def reject_sellers(self, request, queryset):
        updated = queryset.update(approval_status='rejected', verified=False)
        self.message_user(request, f'{updated} sellers rejected.')
    reject_sellers.short_description = 'Reject selected sellers'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class PODCustomizationInline(admin.TabularInline):
    model = PODCustomization
    extra = 0


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'business_name', 'user', 'gstin', 'mobile_number', 
        'approval_status_badge', 'verified', 'credit_balance', 'created_at'
    ]
    list_filter = ['verified', 'approval_status', 'created_at']
    search_fields = ['name', 'business_name', 'user__username', 'gstin', 'mobile_number']
    ordering = ['-created_at']
    list_editable = ['verified']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'name', 'business_name')
        }),
        ('Contact Information', {
            'fields': ('address', 'mobile_number', 'gstin')
        }),
        ('Financial Information', {
            'fields': ('credit_balance', 'bank_name', 'account_number', 'ifsc_code')
        }),
        ('Approval Status', {
            'fields': ('approval_status', 'verified', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def approval_status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.approval_status, 'gray'),
            obj.get_approval_status_display()
        )
    approval_status_badge.short_description = 'Status'
    
    actions = ['approve_buyers', 'reject_buyers']
    
    def approve_buyers(self, request, queryset):
        updated = queryset.update(approval_status='approved', verified=True)
        self.message_user(request, f'{updated} buyers approved successfully.')
    approve_buyers.short_description = 'Approve selected buyers'
    
    def reject_buyers(self, request, queryset):
        updated = queryset.update(approval_status='rejected', verified=False)
        self.message_user(request, f'{updated} buyers rejected.')
    reject_buyers.short_description = 'Reject selected buyers'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'seller', 'category', 'mrp', 'selling_price', 'gst_rate', 
        'stock_quantity', 'approval_status_badge', 'is_active', 'is_customizable', 'created_at'
    ]
    list_filter = ['category', 'is_active', 'is_customizable', 'approval_status', 'gst_rate', 'seller__business_type']
    search_fields = ['name', 'description', 'tags', 'seller__business_name']
    ordering = ['-created_at']
    list_editable = ['is_active']
    inlines = [ProductImageInline, PODCustomizationInline]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('seller', 'category', 'name', 'description')
        }),
        ('Pricing & GST', {
            'fields': ('mrp', 'selling_price', 'gst_rate')
        }),
        ('Stock Management', {
            'fields': ('stock_quantity', 'minimum_order_quantity')
        }),
        ('Approval & Settings', {
            'fields': ('approval_status', 'is_active', 'is_customizable', 'rejection_reason', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def approval_status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.approval_status, 'gray'),
            obj.get_approval_status_display()
        )
    approval_status_badge.short_description = 'Status'
    
    actions = ['approve_products', 'reject_products']
    
    def approve_products(self, request, queryset):
        updated = queryset.update(approval_status='approved', is_active=True)
        self.message_user(request, f'{updated} products approved successfully.')
    approve_products.short_description = 'Approve selected products'
    
    def reject_products(self, request, queryset):
        updated = queryset.update(approval_status='rejected', is_active=False)
        self.message_user(request, f'{updated} products rejected.')
    reject_products.short_description = 'Reject selected products'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text']


@admin.register(PODCustomization)
class PODCustomizationAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'customization_type', 'additional_cost', 'is_required']
    list_filter = ['customization_type', 'is_required']
    search_fields = ['product__name', 'name']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    ordering = ['-created_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'buyer', 'seller', 'total_amount', 'status', 
        'payment_method', 'payment_status', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'payment_status', 'created_at']
    search_fields = ['order_number', 'buyer__name', 'seller__business_name']
    ordering = ['-created_at']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'buyer', 'seller')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'gst_amount', 'total_amount')
        }),
        ('Payment & Status', {
            'fields': ('payment_method', 'payment_status', 'status', 'po_document')
        }),
        ('Shipping', {
            'fields': ('shipping_address',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'transaction_type', 'buyer', 'seller', 'amount', 
        'status', 'created_at'
    ]
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['transaction_id', 'buyer__name', 'seller__business_name', 'reference_number']
    ordering = ['-created_at']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('transaction_id', 'transaction_type', 'amount', 'status')
        }),
        ('Parties', {
            'fields': ('buyer', 'seller', 'order')
        }),
        ('Additional Information', {
            'fields': ('description', 'reference_number')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'transaction_type', 'amount', 'balance_after', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['buyer__name', 'reference', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('buyer', 'transaction_type', 'amount', 'balance_after')
        }),
        ('Additional Information', {
            'fields': ('reference', 'description')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
