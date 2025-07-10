from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Seller, Buyer, Product, ProductImage, Order, PODCustomization
import re


class SellerRegistrationForm(UserCreationForm):
    # User fields
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label="Owner First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Owner Last Name")
    
    # Seller specific fields
    business_name = forms.CharField(max_length=200, required=True)
    owner_name = forms.CharField(max_length=100, required=True, label="Full Owner Name")
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    pincode = forms.CharField(max_length=10, required=True)
    
    # GSTIN with validation
    gstin = forms.CharField(max_length=15, required=True, label="GSTIN Number")
    
    # Turnover
    turnover = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=True,
        label="Annual Turnover (in Crores)",
        help_text="Enter value between ₹2-50 Crores"
    )
    
    # Bank details
    bank_name = forms.CharField(max_length=100, required=True)
    account_number = forms.CharField(max_length=20, required=True)
    ifsc_code = forms.CharField(max_length=11, required=True, label="IFSC Code")
    account_holder_name = forms.CharField(max_length=100, required=True)
    
    # Business type
    business_type = forms.ChoiceField(
        choices=Seller._meta.get_field('business_type').choices,
        required=True
    )
    
    # Document uploads
    pan_document = forms.FileField(required=True, label="PAN Card Document")
    gst_certificate = forms.FileField(required=False, label="GST Certificate")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']
    
    def clean_gstin(self):
        gstin = self.cleaned_data.get('gstin', '').upper()
        # GSTIN validation pattern
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(pattern, gstin):
            raise ValidationError("Enter a valid GSTIN number (15 characters)")
        
        # Check if GSTIN already exists
        if Seller.objects.filter(gstin=gstin).exists():
            raise ValidationError("This GSTIN is already registered")
        
        return gstin
    
    def clean_turnover(self):
        turnover = self.cleaned_data.get('turnover')
        if turnover and (turnover < 2 or turnover > 50):
            raise ValidationError("Turnover must be between ₹2-50 Crores")
        return turnover
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered")
        return email


class BuyerRegistrationForm(UserCreationForm):
    # User fields
    email = forms.EmailField(required=True)
    
    # Buyer specific fields
    name = forms.CharField(max_length=100, required=True, label="Full Name")
    business_name = forms.CharField(max_length=200, required=False, label="Business Name (Optional)")
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
    mobile_number = forms.CharField(max_length=15, required=True)
    
    # GSTIN - mandatory for buyers
    gstin = forms.CharField(max_length=15, required=True, label="GSTIN Number")
    
    # Bank details for credit
    bank_name = forms.CharField(max_length=100, required=False, label="Bank Name (Optional)")
    account_number = forms.CharField(max_length=20, required=False, label="Account Number (Optional)")
    ifsc_code = forms.CharField(max_length=11, required=False, label="IFSC Code (Optional)")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_gstin(self):
        gstin = self.cleaned_data.get('gstin', '').upper()
        # GSTIN validation pattern
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(pattern, gstin):
            raise ValidationError("Enter a valid GSTIN number (15 characters)")
        
        # Check if GSTIN already exists
        if Buyer.objects.filter(gstin=gstin).exists() or Seller.objects.filter(gstin=gstin).exists():
            raise ValidationError("This GSTIN is already registered")
        
        return gstin
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered")
        return email


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'description', 'mrp', 'selling_price', 
            'gst_rate', 'stock_quantity', 'minimum_order_quantity',
            'is_customizable', 'tags'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.TextInput(attrs={'placeholder': 'Enter comma-separated tags'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        mrp = cleaned_data.get('mrp')
        selling_price = cleaned_data.get('selling_price')
        
        if mrp and selling_price and selling_price > mrp:
            raise ValidationError("Selling price cannot be greater than MRP")
        
        return cleaned_data


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['payment_method', 'po_document', 'shipping_address']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3}),
            'po_document': forms.FileInput(attrs={'accept': '.pdf,.doc,.docx,.jpg,.png'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make PO document required only for PO payment method
        self.fields['po_document'].required = False


class AddCreditForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        min_value=100,
        label="Amount to Add (₹)",
        widget=forms.NumberInput(attrs={'placeholder': 'Enter amount'})
    )
    reference = forms.CharField(
        max_length=100, 
        required=False,
        label="Reference Number (Optional)",
        widget=forms.TextInput(attrs={'placeholder': 'Bank transfer reference'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        label="Description",
        initial="Credit balance top-up"
    )


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    user_type = forms.ChoiceField(choices=[
        ('seller', 'Seller'),
        ('buyer', 'Buyer'),
        ('admin', 'Admin')
    ])


class AdminApprovalForm(forms.Form):
    action = forms.ChoiceField(choices=[
        ('approve', 'Approve'),
        ('reject', 'Reject')
    ])
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Rejection Reason (if rejecting)"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if action == 'reject' and not rejection_reason:
            raise ValidationError("Rejection reason is required when rejecting")
        
        return cleaned_data
