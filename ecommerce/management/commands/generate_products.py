import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from ecommerce.models import (
    Category, SubCategory, Brand, Color, Size,
    Product, ProductVariant
)

class Command(BaseCommand):
    help = 'Generate sample products and variants for eCommerce site'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of products to create (default: 50)'
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete all existing products before creation'
        )

    def handle(self, *args, **options):
        product_count = options['count']
        
        if options['delete']:
            deleted, _ = Product.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} existing products.'))
        
        # Check required models exist
        if not all([Category.objects.exists(), Brand.objects.exists(), 
                   Color.objects.exists(), Size.objects.exists()]):
            self.stdout.write(self.style.ERROR(
                'Required models (Category, Brand, Color, Size) not found. '
                'Please run generate_sample_data first.'))
            return

        # Real product data
        clothing_items = {
            'T-Shirt': ['Basic Cotton Tee', 'Graphic Print Shirt', 'V-Neck Tee', 'Pocket T-Shirt', 'Long Sleeve Shirt'],
            'Jeans': ['Slim Fit Jeans', 'Skinny Jeans', 'Bootcut Jeans', 'Relaxed Fit Jeans', 'Ripped Jeans'],
            'Dress': ['Summer Sundress', 'Wrap Dress', 'Maxi Dress', 'Cocktail Dress', 'Shirt Dress'],
            'Jacket': ['Bomber Jacket', 'Denim Jacket', 'Leather Jacket', 'Parka', 'Blazer'],
            'Sweater': ['Crewneck Sweater', 'V-Neck Sweater', 'Turtleneck', 'Cardigan', 'Hoodie']
        }
        
        shoes_items = {
            'Sneakers': ['Classic White Sneakers', 'Running Shoes', 'High-Top Sneakers', 'Slip-Ons', 'Retro Sneakers'],
            'Boots': ['Chelsea Boots', 'Combat Boots', 'Ankle Boots', 'Hiking Boots', 'Snow Boots'],
            'Sandals': ['Flip Flops', 'Slide Sandals', 'Sport Sandals', 'Gladiator Sandals', 'Wedge Sandals'],
            'Loafers': ['Penny Loafers', 'Tassel Loafers', 'Driving Loafers', 'Slip-On Loafers', 'Horsebit Loafers']
        }
        
        accessories_items = {
            'Watch': ['Chronograph Watch', 'Dive Watch', 'Smartwatch', 'Dress Watch', 'Pilot Watch'],
            'Belt': ['Leather Belt', 'Reversible Belt', 'Canvas Belt', 'Formal Belt', 'Braided Belt'],
            'Hat': ['Baseball Cap', 'Beanie', 'Fedora', 'Bucket Hat', 'Sun Hat'],
            'Sunglasses': ['Aviators', 'Wayfarers', 'Round Frames', 'Cat-Eye Sunglasses', 'Sport Sunglasses']
        }
        
        bags_items = {
            'Backpack': ['Laptop Backpack', 'Hiking Backpack', 'Mini Backpack', 'Rolling Backpack', 'Drawstring Bag'],
            'Handbag': ['Tote Bag', 'Crossbody Bag', 'Clutch', 'Satchel', 'Hobo Bag'],
            'Wallet': ['Bifold Wallet', 'Trifold Wallet', 'Cardholder', 'Money Clip', 'Travel Wallet'],
            'Luggage': ['Carry-On Suitcase', 'Checked Luggage', 'Duffel Bag', 'Garment Bag', 'Weekender Bag']
        }
        
        # Material and care instruction samples
        materials = [
            'Cotton', 'Polyester', 'Leather', 'Denim', 'Silk',
            'Wool', 'Linen', 'Nylon', 'Spandex', 'Cashmere'
        ]
        
        care_instructions = [
            'Machine wash cold', 'Hand wash only', 'Dry clean only',
            'Do not bleach', 'Tumble dry low', 'Iron low heat',
            'Line dry', 'Do not wring', 'Wash inside out'
        ]
        
        descriptions = [
            "High-quality materials ensure durability and comfort.",
            "Designed for both style and functionality.",
            "Perfect for everyday wear or special occasions.",
            "Classic design with modern details.",
            "Comfortable fit that doesn't sacrifice style.",
            "Versatile piece that works with multiple outfits.",
            "Premium craftsmanship for long-lasting wear.",
            "Trend-forward design that stands out.",
            "Eco-friendly materials used in production.",
            "Attention to detail in every stitch."
        ]
        
        # Generate products
        products_created = 0
        for i in range(product_count):
            category = random.choice(Category.objects.all())
            subcategory = random.choice(category.subcategories.all()) if category.subcategories.exists() else None
            brand = random.choice(Brand.objects.all())
            gender = random.choice(['men', 'women', 'unisex', 'kids'])
            
            # Get appropriate product type based on category
            if category.name == 'Clothing':
                product_type, product_models = random.choice(list(clothing_items.items()))
                model_name = random.choice(product_models)
            elif category.name == 'Shoes':
                product_type, product_models = random.choice(list(shoes_items.items()))
                model_name = random.choice(product_models)
            elif category.name == 'Accessories':
                product_type, product_models = random.choice(list(accessories_items.items()))
                model_name = random.choice(product_models)
            elif category.name == 'Bags':
                product_type, product_models = random.choice(list(bags_items.items()))
                model_name = random.choice(product_models)
            else:
                product_type = 'Product'
                model_name = 'Standard Model'
            
            # Construct product name
            name = f"{brand.name} {model_name}"
            if gender == 'women':
                name = f"Women's {name}"
            elif gender == 'men':
                name = f"Men's {name}"
            elif gender == 'kids':
                name = f"Kids' {name}"
            
            # Generate unique SKU
            sku = f"{brand.name[:3].upper()}-{category.name[:3].upper()}-{random.randint(100, 999)}{random.choice('ABCDE')}"
            
            # Create product
            product = Product.objects.create(
                name=name,
                description=f"{random.choice(descriptions)} {random.choice(descriptions)}",
                short_description=random.choice(descriptions),
                category=category,
                subcategory=subcategory,
                brand=brand,
                sku=sku,
                base_price=Decimal(random.randint(2000, 20000) / 100),  # $20.00 - $200.00
                discount_price=Decimal(random.randint(1000, 15000) / 100) if random.random() > 0.7 else None,
                gender=gender,
                material=random.choice(materials),
                care_instructions=", ".join(random.sample(care_instructions, 3)),
                weight=random.randint(50, 2000),
                is_featured=random.random() > 0.8,
                is_active=random.random() > 0.1,
                meta_title=f"Buy {name} | {brand.name} {category.name}",
                meta_description=f"Shop the {name} from {brand.name}. {random.choice(descriptions)}"
            )
            products_created += 1
            
            # Generate variants (2-5 per product)
            colors = random.sample(list(Color.objects.all()), random.randint(1, 3))
            sizes = list(Size.objects.filter(
                size_type='shoe' if category.name == 'Shoes' else 'clothing'
            ))
            
            variant_count = 0
            for color in colors:
                for size in random.sample(sizes, random.randint(1, min(3, len(sizes)))):
                    variant_sku = f"{product.sku}-{color.name[:3].upper()}-{size.name.upper()}"
                    ProductVariant.objects.create(
                        product=product,
                        color=color,
                        size=size,
                        sku=variant_sku,
                        stock_quantity=random.randint(0, 100),
                        price_adjustment=Decimal(random.randint(-500, 500) / 100),  # -$5.00 to +$5.00
                        is_active=random.random() > 0.1
                    )
                    variant_count += 1
            
            self.stdout.write(self.style.SUCCESS(
                f'Created product: {product.name} with {variant_count} variants'))

        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully created {products_created} products with variants'))