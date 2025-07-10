from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from PIL import Image
import os
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    # GSTIN validation
    gstin_validator = RegexValidator(
        regex=r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$',
        message='Enter a valid GSTIN number (15 characters)'
    )
    gstin = models.CharField(max_length=15, validators=[gstin_validator], unique=True)
    
    # Turnover in Crores
    turnover = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(2), MaxValueValidator(50)],
        help_text='Annual turnover in Crores (₹2-50 Cr)'
    )
    
    # Bank Details
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11)
    account_holder_name = models.CharField(max_length=100)
    
    business_type = models.CharField(max_length=100, choices=[
        ('manufacturer', 'Manufacturer'),
        ('wholesaler', 'Wholesaler'),
        ('retailer', 'Retailer'),
        ('service_provider', 'Service Provider'),
    ])
    
    # Document uploads
    pan_document = models.FileField(upload_to='seller_documents/pan/', null=True, blank=True)
    gst_certificate = models.FileField(upload_to='seller_documents/gst/', null=True, blank=True)
    
    # Approval status
    APPROVAL_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending')
    verified = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.business_name
    
    @property
    def location(self):
        return f"{self.city}, {self.state}"


class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    business_name = models.CharField(max_length=200, blank=True)
    address = models.TextField()
    mobile_number = models.CharField(max_length=15)
    
    # GSTIN validation - mandatory for buyers
    gstin_validator = RegexValidator(
        regex=r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$',
        message='Enter a valid GSTIN number (15 characters)'
    )
    gstin = models.CharField(max_length=15, validators=[gstin_validator], unique=True)
    
    # Credit balance
    credit_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Bank details for credit
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=20, blank=True)
    ifsc_code = models.CharField(max_length=11, blank=True)
    
    # Approval status
    APPROVAL_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending')
    verified = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.business_name if self.business_name else 'Individual'})"
    
    def can_purchase(self, amount):
        return self.credit_balance >= amount


class Product(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Enhanced pricing structure
    mrp = models.DecimalField(max_digits=10, decimal_places=2, help_text='Maximum Retail Price')
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Actual Selling Price')
    
    # GST Rate
    GST_RATES = [
        (0, '0%'),
        (5, '5%'),
        (12, '12%'),
        (18, '18%'),
        (28, '28%'),
    ]
    gst_rate = models.IntegerField(choices=GST_RATES, default=18)
    
    stock_quantity = models.PositiveIntegerField(default=0)
    minimum_order_quantity = models.PositiveIntegerField(default=1)
    
    # Product approval
    APPROVAL_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending')
    is_active = models.BooleanField(default=True)
    is_customizable = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # For search functionality
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags for search")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('marketplace:product_detail', kwargs={'pk': self.pk})
    
    @property
    def main_image(self):
        image = self.images.first()
        return image.image if image else None
    
    @property
    def in_stock(self):
        return self.stock_quantity > 0
    
    @property
    def price(self):
        """For backward compatibility"""
        return self.selling_price
    
    @property
    def discount_percentage(self):
        if self.mrp > 0:
            return round(((self.mrp - self.selling_price) / self.mrp) * 100, 1)
        return 0
    
    @property
    def price_with_gst(self):
        gst_amount = (self.selling_price * self.gst_rate) / 100
        return self.selling_price + gst_amount
    
    @property
    def gst_amount(self):
        return (self.selling_price * self.gst_rate) / 100


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'created_at']
    
    def __str__(self):
        return f"{self.product.name} - Image"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Resize image if too large
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 800 or img.width > 800:
                img.thumbnail((800, 800))
                img.save(self.image.path)


class PODCustomization(models.Model):
    """Print on Demand customization options"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='customizations')
    customization_type = models.CharField(max_length=50, choices=[
        ('text', 'Text Customization'),
        ('logo', 'Logo/Image Upload'),
        ('color', 'Color Selection'),
        ('size', 'Size Selection'),
        ('material', 'Material Selection'),
    ])
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    options = models.JSONField(default=dict, help_text="JSON field for customization options")
    additional_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"{self.product.name} - {self.rating} stars"


class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD = [
        ('credit', 'Credit Balance'),
        ('online', 'Online Payment'),
        ('po', 'Purchase Order'),
    ]
    
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    
    # Order totals
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    payment_status = models.BooleanField(default=False)
    
    # Purchase Order upload
    po_document = models.FileField(upload_to='purchase_orders/', null=True, blank=True)
    
    # Shipping details
    shipping_address = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.order_number} - {self.buyer.name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            import uuid
            self.order_number = f"ORD{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.IntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Customization details (JSON field for flexibility)
    customizations = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class Transaction(models.Model):
    TRANSACTION_TYPE = [
        ('purchase', 'Purchase'),
        ('credit_add', 'Credit Added'),
        ('credit_deduct', 'Credit Deducted'),
        ('refund', 'Refund'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    
    transaction_id = models.CharField(max_length=30, unique=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    
    description = models.TextField(blank=True)
    reference_number = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.transaction_id} - ₹{self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            import uuid
            self.transaction_id = f"TXN{str(uuid.uuid4())[:10].upper()}"
        super().save(*args, **kwargs)


class CreditTransaction(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='credit_transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=[
        ('credit', 'Credit Added'),
        ('debit', 'Credit Used'),
    ])
    reference = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.buyer.name} - {self.transaction_type} - ₹{self.amount}"
