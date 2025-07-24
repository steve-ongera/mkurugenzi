import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from faker import Faker
from ecommerce.models import Category, SubCategory, Brand, Color, Size

class Command(BaseCommand):
    help = 'Generate sample data for SubCategories, Brands, Colors, and Sizes'

    def handle(self, *args, **options):
        fake = Faker()
        
        # Ensure we have at least one category
        if not Category.objects.exists():
            self.stdout.write(self.style.ERROR('No categories found. Please create categories first.'))
            return

        # Generate SubCategories
        subcategory_data = {
            'Clothing': ['T-Shirts', 'Jeans', 'Dresses', 'Jackets', 'Sweaters'],
            'Shoes': ['Sneakers', 'Boots', 'Sandals', 'Loafers', 'Heels'],
            'Accessories': ['Watches', 'Belts', 'Hats', 'Sunglasses', 'Scarves'],
            'Bags': ['Backpacks', 'Handbags', 'Wallets', 'Luggage', 'Clutches'],
        }
        
        subcategories_created = 0
        for category in Category.objects.all():
            if category.name in subcategory_data:
                for sub_name in subcategory_data[category.name]:
                    if not SubCategory.objects.filter(category=category, name=sub_name).exists():
                        SubCategory.objects.create(
                            category=category,
                            name=sub_name,
                            description=fake.text(max_nb_chars=200),
                            is_active=random.choice([True, False])
                        )
                        subcategories_created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {subcategories_created} subcategories'))

        # Generate Brands
        brand_names = [
            'Nike', 'Adidas', 'Zara', 'H&M', 'Gucci',
            'Puma', 'Levi\'s', 'Tommy Hilfiger', 'Calvin Klein', 'Under Armour'
        ]
        brands_created = 0
        for name in brand_names:
            if not Brand.objects.filter(name=name).exists():
                Brand.objects.create(
                    name=name,
                    description=fake.text(max_nb_chars=300),
                    website=fake.url(),
                    is_active=random.choice([True, False])
                )
                brands_created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {brands_created} brands'))

        # Generate Colors
        color_data = [
            ('Red', '#FF0000'), ('Blue', '#0000FF'), ('Green', '#008000'),
            ('Black', '#000000'), ('White', '#FFFFFF'), ('Yellow', '#FFFF00'),
            ('Purple', '#800080'), ('Pink', '#FFC0CB'), ('Orange', '#FFA500'),
            ('Gray', '#808080'), ('Brown', '#A52A2A'), ('Navy', '#000080')
        ]
        colors_created = 0
        for name, hex_code in color_data:
            if not Color.objects.filter(name=name).exists():
                Color.objects.create(
                    name=name,
                    hex_code=hex_code
                )
                colors_created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {colors_created} colors'))

        # Generate Sizes
        shoe_sizes = [
            ('36', 36, 'EU'), ('37', 37, 'EU'), ('38', 38, 'EU'), 
            ('39', 39, 'EU'), ('40', 40, 'EU'), ('41', 41, 'EU'),
            ('42', 42, 'EU'), ('43', 43, 'EU'), ('44', 44, 'EU'),
            ('7', 7, 'US'), ('8', 8, 'US'), ('9', 9, 'US'), 
            ('10', 10, 'US'), ('11', 11, 'US'), ('12', 12, 'US'),
            ('5', 5, 'UK'), ('6', 6, 'UK'), ('7', 7, 'UK'),
            ('8', 8, 'UK'), ('9', 9, 'UK'), ('10', 10, 'UK')
        ]
        
        clothing_sizes = [
            ('XS', None, 'INT'), ('S', None, 'INT'), ('M', None, 'INT'),
            ('L', None, 'INT'), ('XL', None, 'INT'), ('XXL', None, 'INT'),
            ('XXXL', None, 'INT'), ('28', 28, 'US'), ('30', 30, 'US'),
            ('32', 32, 'US'), ('34', 34, 'US'), ('36', 36, 'US')
        ]
        
        sizes_created = 0
        for name, numeric_value, region in shoe_sizes:
            if not Size.objects.filter(name=name, size_type='shoe', region=region).exists():
                Size.objects.create(
                    name=name,
                    size_type='shoe',
                    numeric_value=numeric_value,
                    region=region
                )
                sizes_created += 1
                
        for name, numeric_value, region in clothing_sizes:
            if not Size.objects.filter(name=name, size_type='clothing', region=region).exists():
                Size.objects.create(
                    name=name,
                    size_type='clothing',
                    numeric_value=numeric_value,
                    region=region
                )
                sizes_created += 1
                
        self.stdout.write(self.style.SUCCESS(f'Created {sizes_created} sizes'))
        self.stdout.write(self.style.SUCCESS('Successfully generated all sample data!'))