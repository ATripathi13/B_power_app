from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from marketplace.models import Category, Seller, Product, PODCustomization
import random


class Command(BaseCommand):
    help = 'Load sample data for the marketplace'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample data...')

        # Create categories
        categories_data = [
            {'name': 'Textiles & Apparel', 'description': 'Clothing, fabrics, and textile products'},
            {'name': 'Handicrafts', 'description': 'Traditional and handmade crafts'},
            {'name': 'Electronics', 'description': 'Electronic components and devices'},
            {'name': 'Food Products', 'description': 'Processed and packaged food items'},
            {'name': 'Jewelry', 'description': 'Traditional and modern jewelry'},
            {'name': 'Home Decor', 'description': 'Interior decoration items'},
            {'name': 'Automotive Parts', 'description': 'Vehicle components and accessories'},
            {'name': 'Beauty Products', 'description': 'Cosmetics and personal care items'},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create sample users and sellers
        sellers_data = [
            {
                'username': 'textile_hub',
                'email': 'contact@textilehub.com',
                'business_name': 'Mumbai Textile Hub',
                'owner_name': 'Rajesh Kumar',
                'phone': '+91-9876543210',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'gstin': '27AABCT1332L1ZA',
                'turnover': 15.5,
                'bank_name': 'State Bank of India',
                'account_number': '1234567890123456',
                'ifsc_code': 'SBIN0001234',
                'account_holder_name': 'Mumbai Textile Hub',
                'business_type': 'manufacturer',
                'verified': True
            },
            {
                'username': 'craft_corner',
                'email': 'info@craftcorner.com',
                'business_name': 'Rajasthan Craft Corner',
                'owner_name': 'Anita Sharma',
                'phone': '+91-9876543211',
                'city': 'Jaipur',
                'state': 'Rajasthan',
                'gstin': '08AABCT1332L1ZB',
                'turnover': 25.0,
                'bank_name': 'ICICI Bank',
                'account_number': '6543210987654321',
                'ifsc_code': 'ICIC0001235',
                'account_holder_name': 'Rajasthan Craft Corner',
                'business_type': 'retailer',
                'verified': True
            },
            {
                'username': 'tech_solutions',
                'email': 'sales@techsolutions.com',
                'business_name': 'Bangalore Tech Solutions',
                'owner_name': 'Vikas Mehta',
                'phone': '+91-9876543212',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'gstin': '29AABCT1332L1ZC',
                'turnover': 18.9,
                'bank_name': 'HDFC Bank',
                'account_number': '9876543210123456',
                'ifsc_code': 'HDFC0001236',
                'account_holder_name': 'Bangalore Tech Solutions',
                'business_type': 'manufacturer',
                'verified': False
            },
            {
                'username': 'food_factory',
                'email': 'orders@foodfactory.com',
                'business_name': 'Delhi Food Factory',
                'owner_name': 'Sumit Tandon',
                'phone': '+91-9876543213',
                'city': 'Delhi',
                'state': 'Delhi',
                'gstin': '07AABCT1332L1ZD',
                'turnover': 22.0,
                'bank_name': 'AXIS Bank',
                'account_number': '3210987654321098',
                'ifsc_code': 'UTIB0001237',
                'account_holder_name': 'Delhi Food Factory',
                'business_type': 'manufacturer',
                'verified': True
            },
            {
                'username': 'jewelry_works',
                'email': 'info@jewelryworks.com',
                'business_name': 'Kolkata Jewelry Works',
                'owner_name': 'Rina Desai',
                'phone': '+91-9876543214',
                'city': 'Kolkata',
                'state': 'West Bengal',
                'gstin': '19AABCT1332L1ZE',
                'turnover': 30.0,
                'bank_name': 'Kotak Mahindra Bank',
                'account_number': '2109876543210987',
                'ifsc_code': 'KKBK0001238',
                'account_holder_name': 'Kolkata Jewelry Works',
                'business_type': 'wholesaler',
                'verified': True
            }
        ]

        sellers = []
        for seller_data in sellers_data:
            user, created = User.objects.get_or_create(
                username=seller_data['username'],
                defaults={
                    'email': seller_data['email'],
                    'first_name': seller_data['business_name'].split()[0],
                    'last_name': 'Owner'
                }
            )
            if created:
                user.set_password('password123')
                user.save()

            seller, created = Seller.objects.get_or_create(
                user=user,
                defaults={
                    'business_name': seller_data['business_name'],
                    'owner_name': seller_data['owner_name'],
                    'phone': seller_data['phone'],
                    'address': f"123 Business Street, {seller_data['city']}",
                    'city': seller_data['city'],
                    'state': seller_data['state'],
                    'pincode': f"{random.randint(100000, 999999)}",
                    'gstin': seller_data['gstin'],
                    'turnover': seller_data['turnover'],
                    'bank_name': seller_data['bank_name'],
                    'account_number': seller_data['account_number'],
                    'ifsc_code': seller_data['ifsc_code'],
                    'account_holder_name': seller_data['account_holder_name'],
                    'business_type': seller_data['business_type'],
                    'approval_status': 'approved',
                    'verified': seller_data['verified']
                }
            )
            sellers.append(seller)
            if created:
                self.stdout.write(f'Created seller: {seller.business_name}')

        # Create sample products
        products_data = [
            {
                'name': 'Cotton T-Shirts (Pack of 10)',
                'description': 'High-quality cotton t-shirts suitable for printing and customization. Available in various sizes and colors.',
                'mrp': 30.00,
                'selling_price': 25.00,
                'gst_rate': 12,
                'stock_quantity': 500,
                'minimum_order_quantity': 10,
                'is_customizable': True,
                'tags': 'cotton, t-shirt, apparel, customizable, printing',
                'category_name': 'Textiles & Apparel'
            },
            {
                'name': 'Handwoven Carpets',
                'description': 'Traditional handwoven carpets made with natural materials. Perfect for home decoration.',
                'mrp': 180.00,
                'selling_price': 150.00,
                'gst_rate': 5,
                'stock_quantity': 50,
                'minimum_order_quantity': 1,
                'is_customizable': True,
                'tags': 'carpet, handwoven, traditional, home decor',
                'category_name': 'Handicrafts'
            },
            {
                'name': 'LED Light Strips (5m)',
                'description': 'Flexible LED light strips with remote control. Suitable for various lighting applications.',
                'mrp': 15.00,
                'selling_price': 12.50,
                'gst_rate': 18,
                'stock_quantity': 200,
                'minimum_order_quantity': 5,
                'is_customizable': False,
                'tags': 'LED, lights, electronics, remote control',
                'category_name': 'Electronics'
            },
            {
                'name': 'Organic Spice Mix',
                'description': 'Premium organic spice blend made from locally sourced ingredients.',
                'mrp': 10.00,
                'selling_price': 8.00,
                'gst_rate': 0,
                'stock_quantity': 1000,
                'minimum_order_quantity': 50,
                'is_customizable': True,
                'tags': 'spices, organic, food, blend, natural',
                'category_name': 'Food Products'
            },
            {
                'name': 'Silver Earrings',
                'description': 'Handcrafted silver earrings with traditional Indian designs.',
                'mrp': 55.00,
                'selling_price': 45.00,
                'gst_rate': 3,
                'stock_quantity': 100,
                'minimum_order_quantity': 2,
                'is_customizable': True,
                'tags': 'silver, earrings, jewelry, handcrafted, traditional',
                'category_name': 'Jewelry'
            },
            {
                'name': 'Wooden Wall Art',
                'description': 'Decorative wooden wall art pieces with intricate carvings.',
                'mrp': 90.00,
                'selling_price': 75.00,
                'gst_rate': 12,
                'stock_quantity': 30,
                'minimum_order_quantity': 1,
                'is_customizable': True,
                'tags': 'wood, wall art, decoration, carved, handmade',
                'category_name': 'Home Decor'
            },
            {
                'name': 'Car Floor Mats',
                'description': 'Universal car floor mats made from durable materials.',
                'mrp': 25.00,
                'selling_price': 20.00,
                'gst_rate': 28,
                'stock_quantity': 150,
                'minimum_order_quantity': 4,
                'is_customizable': False,
                'tags': 'car, floor mats, automotive, durable',
                'category_name': 'Automotive Parts'
            },
            {
                'name': 'Natural Face Cream',
                'description': 'Organic face cream made with natural ingredients and essential oils.',
                'mrp': 18.00,
                'selling_price': 15.00,
                'gst_rate': 18,
                'stock_quantity': 300,
                'minimum_order_quantity': 12,
                'is_customizable': True,
                'tags': 'face cream, natural, organic, beauty, skincare',
                'category_name': 'Beauty Products'
            }
        ]

        products = []
        for product_data in products_data:
            category = Category.objects.get(name=product_data['category_name'])
            seller = random.choice(sellers)
            
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                seller=seller,
                defaults={
                    'category': category,
                    'description': product_data['description'],
                    'mrp': product_data['mrp'],
                    'selling_price': product_data['selling_price'],
                    'gst_rate': product_data['gst_rate'],
                    'stock_quantity': product_data['stock_quantity'],
                    'minimum_order_quantity': product_data['minimum_order_quantity'],
                    'is_customizable': product_data['is_customizable'],
                    'tags': product_data['tags'],
                    'approval_status': 'approved',
                    'is_active': True
                }
            )
            products.append(product)
            if created:
                self.stdout.write(f'Created product: {product.name}')

        # Create POD customization options for customizable products
        customization_options = [
            {
                'type': 'text',
                'name': 'Custom Text',
                'description': 'Add your custom text to the product',
                'additional_cost': 2.00,
                'is_required': False
            },
            {
                'type': 'color',
                'name': 'Color Selection',
                'description': 'Choose your preferred color',
                'options': {'colors': ['Red', 'Blue', 'Green', 'Black', 'White', 'Yellow']},
                'additional_cost': 0.00,
                'is_required': True
            },
            {
                'type': 'size',
                'name': 'Size Selection',
                'description': 'Select the size',
                'options': {'sizes': ['XS', 'S', 'M', 'L', 'XL', 'XXL']},
                'additional_cost': 0.00,
                'is_required': True
            },
            {
                'type': 'logo',
                'name': 'Logo Upload',
                'description': 'Upload your logo for printing',
                'additional_cost': 5.00,
                'is_required': False
            }
        ]

        for product in products:
            if product.is_customizable:
                # Add 2-3 random customization options to each customizable product
                selected_options = random.sample(customization_options, random.randint(2, 3))
                for option in selected_options:
                    PODCustomization.objects.get_or_create(
                        product=product,
                        name=option['name'],
                        defaults={
                            'customization_type': option['type'],
                            'description': option['description'],
                            'options': option.get('options', {}),
                            'additional_cost': option['additional_cost'],
                            'is_required': option['is_required']
                        }
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded sample data:\n'
                f'- {len(categories)} categories\n'
                f'- {len(sellers)} sellers\n'
                f'- {len(products)} products\n'
                f'- POD customizations for customizable products'
            )
        )
