from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q, Min, Max, Count, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.urls import reverse
from django.db import transaction
from .models import (
    Product, Category, Seller, Buyer, PODCustomization, ProductReview,
    Order, OrderItem, Transaction, CreditTransaction
)
from .forms import (
    SellerRegistrationForm, BuyerRegistrationForm, ProductForm, 
    ProductImageForm, OrderForm, AddCreditForm, LoginForm, AdminApprovalForm
)


# Authentication Views
def custom_login(request):
    """Custom login view with user type selection"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user_type = form.cleaned_data['user_type']
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Check user type and verification status
                if user_type == 'seller':
                    try:
                        seller = user.seller
                        if seller.approval_status != 'approved':
                            messages.error(request, 'Your seller account is not approved yet.')
                            return render(request, 'registration/login.html', {'form': form})
                    except Seller.DoesNotExist:
                        messages.error(request, 'No seller account found for this user.')
                        return render(request, 'registration/login.html', {'form': form})
                elif user_type == 'buyer':
                    try:
                        buyer = user.buyer
                        if buyer.approval_status != 'approved':
                            messages.error(request, 'Your buyer account is not approved yet.')
                            return render(request, 'registration/login.html', {'form': form})
                    except Buyer.DoesNotExist:
                        messages.error(request, 'No buyer account found for this user.')
                        return render(request, 'registration/login.html', {'form': form})
                elif user_type == 'admin':
                    if not user.is_staff:
                        messages.error(request, 'Admin access required.')
                        return render(request, 'registration/login.html', {'form': form})
                
                login(request, user)
                
                # Redirect based on user type
                if user_type == 'seller':
                    return redirect('marketplace:seller_dashboard')
                elif user_type == 'buyer':
                    return redirect('marketplace:buyer_dashboard')
                elif user_type == 'admin':
                    return redirect('admin:index')
                else:
                    return redirect('marketplace:home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'registration/login.html', {'form': form})


def seller_register(request):
    """Seller registration view"""
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                # Create user
                user = form.save()
                
                # Create seller profile
                seller = Seller.objects.create(
                    user=user,
                    business_name=form.cleaned_data['business_name'],
                    owner_name=form.cleaned_data['owner_name'],
                    phone=form.cleaned_data['phone'],
                    address=form.cleaned_data['address'],
                    city=form.cleaned_data['city'],
                    state=form.cleaned_data['state'],
                    pincode=form.cleaned_data['pincode'],
                    gstin=form.cleaned_data['gstin'],
                    turnover=form.cleaned_data['turnover'],
                    bank_name=form.cleaned_data['bank_name'],
                    account_number=form.cleaned_data['account_number'],
                    ifsc_code=form.cleaned_data['ifsc_code'],
                    account_holder_name=form.cleaned_data['account_holder_name'],
                    business_type=form.cleaned_data['business_type'],
                    pan_document=form.cleaned_data['pan_document'],
                    gst_certificate=form.cleaned_data.get('gst_certificate'),
                )
                
            messages.success(request, 'Registration successful! Your account is pending approval.')
            return redirect('marketplace:login')
    else:
        form = SellerRegistrationForm()
    
    return render(request, 'registration/seller_register.html', {'form': form})


def buyer_register(request):
    """Buyer registration view"""
    if request.method == 'POST':
        form = BuyerRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create user
                user = form.save()
                
                # Create buyer profile
                buyer = Buyer.objects.create(
                    user=user,
                    name=form.cleaned_data['name'],
                    business_name=form.cleaned_data.get('business_name', ''),
                    address=form.cleaned_data['address'],
                    mobile_number=form.cleaned_data['mobile_number'],
                    gstin=form.cleaned_data['gstin'],
                    bank_name=form.cleaned_data.get('bank_name', ''),
                    account_number=form.cleaned_data.get('account_number', ''),
                    ifsc_code=form.cleaned_data.get('ifsc_code', ''),
                )
            
            messages.success(request, 'Registration successful! Your account is pending approval.')
            return redirect('marketplace:login')
    else:
        form = BuyerRegistrationForm()
    
    return render(request, 'registration/buyer_register.html', {'form': form})


@login_required
def custom_logout(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('marketplace:home')


# Dashboard Views
@login_required
def seller_dashboard(request):
    """Seller dashboard with products and orders"""
    try:
        seller = request.user.seller
    except Seller.DoesNotExist:
        messages.error(request, 'Seller profile not found.')
        return redirect('marketplace:home')
    
    products = Product.objects.filter(seller=seller).order_by('-created_at')[:10]
    orders = Order.objects.filter(seller=seller).order_by('-created_at')[:10]
    
    context = {
        'seller': seller,
        'products': products,
        'orders': orders,
        'total_products': Product.objects.filter(seller=seller).count(),
        'pending_orders': Order.objects.filter(seller=seller, status='pending').count(),
    }
    
    return render(request, 'marketplace/seller_dashboard.html', context)


@login_required
def buyer_dashboard(request):
    """Buyer dashboard with orders and credit balance"""
    try:
        buyer = request.user.buyer
    except Buyer.DoesNotExist:
        messages.error(request, 'Buyer profile not found.')
        return redirect('marketplace:home')
    
    orders = Order.objects.filter(buyer=buyer).order_by('-created_at')[:10]
    credit_transactions = CreditTransaction.objects.filter(buyer=buyer)[:10]
    
    context = {
        'buyer': buyer,
        'orders': orders,
        'credit_transactions': credit_transactions,
        'total_orders': Order.objects.filter(buyer=buyer).count(),
        'pending_orders': Order.objects.filter(buyer=buyer, status='pending').count(),
    }
    
    return render(request, 'marketplace/buyer_dashboard.html', context)


def marketplace_home(request):
    """Main marketplace page with products grid, filters, and search"""
    products = Product.objects.filter(is_active=True).select_related('seller', 'category')
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    location = request.GET.get('location', '')
    business_type = request.GET.get('business_type', '')
    customizable = request.GET.get('customizable', '')
    sort_by = request.GET.get('sort', 'newest')
    
    # Apply filters
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query) |
            Q(seller__business_name__icontains=search_query)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if min_price:
        products = products.filter(selling_price__gte=min_price)
    
    if max_price:
        products = products.filter(selling_price__lte=max_price)
    
    if location:
        products = products.filter(
            Q(seller__city__icontains=location) |
            Q(seller__state__icontains=location)
        )
    
    if business_type:
        products = products.filter(seller__business_type=business_type)
    
    if customizable == 'true':
        products = products.filter(is_customizable=True)
    
    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('selling_price')
    elif sort_by == 'price_high':
        products = products.order_by('-selling_price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    categories = Category.objects.all()
    price_range = Product.objects.filter(is_active=True).aggregate(
        min_price=Min('selling_price'),
        max_price=Max('selling_price')
    )
    
    business_types = Seller.objects.values_list('business_type', flat=True).distinct()
    locations = Seller.objects.values('city', 'state').distinct()[:20]
    
    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': categories,
        'price_range': price_range,
        'business_types': business_types,
        'locations': locations,
        'search_query': search_query,
        'selected_category': category_id,
        'min_price': min_price,
        'max_price': max_price,
        'selected_location': location,
        'selected_business_type': business_type,
        'customizable': customizable,
        'sort_by': sort_by,
        'total_products': paginator.count,
    }
    
    return render(request, 'marketplace/home.html', context)


def product_detail(request, pk):
    """Product detail page with customization options"""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    
    # Get customization options
    customizations = PODCustomization.objects.filter(product=product)
    
    # Get reviews
    reviews = ProductReview.objects.filter(product=product).select_related('user')
    avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    
    # Related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(pk=product.pk)[:6]
    
    context = {
        'product': product,
        'customizations': customizations,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'related_products': related_products,
    }
    
    return render(request, 'marketplace/product_detail.html', context)


def ajax_filter_products(request):
    """AJAX endpoint for filtering products"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # This would contain the same filtering logic as marketplace_home
        # but return JSON response for AJAX requests
        pass
    
    return JsonResponse({'status': 'error'})


def seller_products(request, seller_id):
    """View all products from a specific seller"""
    seller = get_object_or_404(Seller, pk=seller_id)
    products = Product.objects.filter(seller=seller, is_active=True)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'seller': seller,
        'page_obj': page_obj,
        'products': page_obj.object_list,
    }
    
    return render(request, 'marketplace/seller_products.html', context)


def category_products(request, category_id):
    """View all products in a specific category"""
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'products': page_obj.object_list,
    }
    
    return render(request, 'marketplace/category_products.html', context)


# Product Management Views
@login_required
def add_product(request):
    """Add new product (seller only)"""
    try:
        seller = request.user.seller
    except Seller.DoesNotExist:
        messages.error(request, 'Only sellers can add products.')
        return redirect('marketplace:home')
    
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = seller
            product.save()
            
            messages.success(request, 'Product added successfully! It will be visible after admin approval.')
            return redirect('marketplace:seller_dashboard')
    else:
        form = ProductForm()
    
    return render(request, 'marketplace/add_product.html', {'form': form})


@login_required
def add_credit(request):
    """Add credit to buyer account"""
    try:
        buyer = request.user.buyer
    except Buyer.DoesNotExist:
        messages.error(request, 'Only buyers can add credit.')
        return redirect('marketplace:home')
    
    if request.method == 'POST':
        form = AddCreditForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            reference = form.cleaned_data['reference']
            description = form.cleaned_data['description']
            
            # Add credit to buyer account
            buyer.credit_balance += amount
            buyer.save()
            
            # Create credit transaction record
            CreditTransaction.objects.create(
                buyer=buyer,
                amount=amount,
                transaction_type='credit',
                reference=reference,
                description=description,
                balance_after=buyer.credit_balance
            )
            
            messages.success(request, f'₹{amount} credit added successfully!')
            return redirect('marketplace:buyer_dashboard')
    else:
        form = AddCreditForm()
    
    return render(request, 'marketplace/add_credit.html', {'form': form, 'buyer': request.user.buyer})


@login_required
def place_order(request, product_id):
    """Place an order for a product"""
    try:
        buyer = request.user.buyer
    except Buyer.DoesNotExist:
        messages.error(request, 'Only approved buyers can place orders.')
        return redirect('marketplace:login')
    
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, request.FILES)
        quantity = int(request.POST.get('quantity', 1))
        
        if form.is_valid():
            # Calculate order totals
            unit_price = product.selling_price
            subtotal = unit_price * quantity
            gst_amount = (subtotal * product.gst_rate) / 100
            total_amount = subtotal + gst_amount
            
            # Check credit balance for credit payments
            if form.cleaned_data['payment_method'] == 'credit':
                if not buyer.can_purchase(total_amount):
                    messages.error(request, 'Insufficient credit balance.')
                    return render(request, 'marketplace/place_order.html', {
                        'form': form, 'product': product, 'buyer': buyer
                    })
            
            with transaction.atomic():
                # Create order
                order = form.save(commit=False)
                order.buyer = buyer
                order.seller = product.seller
                order.subtotal = subtotal
                order.gst_amount = gst_amount
                order.total_amount = total_amount
                order.save()
                
                # Create order item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    gst_rate=product.gst_rate,
                    total_price=subtotal
                )
                
                # Process payment
                if order.payment_method == 'credit':
                    # Deduct from credit balance
                    buyer.credit_balance -= total_amount
                    buyer.save()
                    
                    # Create credit transaction
                    CreditTransaction.objects.create(
                        buyer=buyer,
                        amount=total_amount,
                        transaction_type='debit',
                        reference=order.order_number,
                        description=f'Purchase: {product.name}',
                        balance_after=buyer.credit_balance
                    )
                    
                    order.payment_status = True
                    order.status = 'confirmed'
                    order.save()
                
                # Create transaction record
                Transaction.objects.create(
                    buyer=buyer,
                    seller=product.seller,
                    order=order,
                    transaction_type='purchase',
                    amount=total_amount,
                    status='completed' if order.payment_status else 'pending',
                    description=f'Purchase of {product.name}'
                )
                
                # Update product stock
                product.stock_quantity -= quantity
                product.save()
            
            messages.success(request, f'Order {order.order_number} placed successfully!')
            return redirect('marketplace:buyer_dashboard')
    else:
        form = OrderForm()
    
    context = {
        'form': form,
        'product': product,
        'buyer': buyer
    }
    
    return render(request, 'marketplace/place_order.html', context)


# Admin Views
@staff_member_required
def admin_transactions(request):
    """Admin view for all transactions"""
    transactions = Transaction.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(transactions, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'transactions': page_obj.object_list,
    }
    
    return render(request, 'admin/transactions.html', context)


@staff_member_required
def admin_approve_seller(request, seller_id):
    """Admin view to approve/reject sellers"""
    seller = get_object_or_404(Seller, pk=seller_id)
    
    if request.method == 'POST':
        form = AdminApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            rejection_reason = form.cleaned_data.get('rejection_reason', '')
            
            if action == 'approve':
                seller.approval_status = 'approved'
                seller.verified = True
                seller.rejection_reason = ''
                messages.success(request, f'Seller {seller.business_name} approved successfully.')
            else:
                seller.approval_status = 'rejected'
                seller.verified = False
                seller.rejection_reason = rejection_reason
                messages.success(request, f'Seller {seller.business_name} rejected.')
            
            seller.save()
            return redirect('admin:marketplace_seller_changelist')
    else:
        form = AdminApprovalForm()
    
    context = {
        'seller': seller,
        'form': form
    }
    
    return render(request, 'admin/approve_seller.html', context)


@staff_member_required
def admin_approve_buyer(request, buyer_id):
    """Admin view to approve/reject buyers"""
    buyer = get_object_or_404(Buyer, pk=buyer_id)
    
    if request.method == 'POST':
        form = AdminApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            rejection_reason = form.cleaned_data.get('rejection_reason', '')
            
            if action == 'approve':
                buyer.approval_status = 'approved'
                buyer.verified = True
                buyer.rejection_reason = ''
                messages.success(request, f'Buyer {buyer.name} approved successfully.')
            else:
                buyer.approval_status = 'rejected'
                buyer.verified = False
                buyer.rejection_reason = rejection_reason
                messages.success(request, f'Buyer {buyer.name} rejected.')
            
            buyer.save()
            return redirect('admin:marketplace_buyer_changelist')
    else:
        form = AdminApprovalForm()
    
    context = {
        'buyer': buyer,
        'form': form
    }
    
    return render(request, 'admin/approve_buyer.html', context)


@staff_member_required
def admin_approve_product(request, product_id):
    """Admin view to approve/reject products"""
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        form = AdminApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            rejection_reason = form.cleaned_data.get('rejection_reason', '')
            
            if action == 'approve':
                product.approval_status = 'approved'
                product.is_active = True
                product.rejection_reason = ''
                messages.success(request, f'Product {product.name} approved successfully.')
            else:
                product.approval_status = 'rejected'
                product.is_active = False
                product.rejection_reason = rejection_reason
                messages.success(request, f'Product {product.name} rejected.')
            
            product.save()
            return redirect('admin:marketplace_product_changelist')
    else:
        form = AdminApprovalForm()
    
    context = {
        'product': product,
        'form': form
    }
    
    return render(request, 'admin/approve_product.html', context)
