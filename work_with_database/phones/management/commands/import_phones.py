import csv
from django.core.management.base import BaseCommand
from phones.models import Phone
from django.utils.text import slugify
from datetime import datetime


class Command(BaseCommand):
    help = 'Imports phone data from CSV file'

    def handle(self, *args, **options):
        with open('phones.csv', 'r', encoding='utf-8') as csvfile:
            phone_reader = csv.DictReader(csvfile, delimiter=';')
            for row in phone_reader:
                try:
                    phone = Phone(
                        name=row['name'],
                        price=int(row['price']),
                        image=row['image'],
                        release_date=datetime.strptime(row['release_date'], '%Y-%m-%d').date(),
                        lte_exists=bool(row['lte_exists']),
                        slug=slugify(row['name'])
                    )
                    phone.save()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing row: {row} - {e}'))
                    continue
        self.stdout.write(self.style.SUCCESS('Successfully imported phone data'))