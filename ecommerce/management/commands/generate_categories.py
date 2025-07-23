from django.core.management.base import BaseCommand
from ecommerce.models import Category
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Generate fake categories for eCommerce app'

    def handle(self, *args, **kwargs):
        fake = Faker()
        category_names = [
            'Shoes', 'Clothing', 'Accessories', 'Watches',
            'Bags', 'Jewelry', 'Sportswear', 'Kids Wear'
        ]
        created = 0

        for name in category_names:
            if not Category.objects.filter(name=name).exists():
                Category.objects.create(
                    name=name,
                    description=fake.text(max_nb_chars=100),
                    is_active=True
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created} categories.'))
