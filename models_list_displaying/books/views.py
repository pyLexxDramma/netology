from django.shortcuts import render, get_object_or_404
from .models import Book
from datetime import date, timedelta

def books_by_date(request, pub_date):
    print(f"pub_date received: {pub_date}")
    pub_date = date.fromisoformat(pub_date)
    print(f"pub_date converted: {pub_date}")
    books = Book.objects.filter(pub_date=pub_date)
    print(f"Books for this date: {books}")

    # Найти предыдущую дату с книгами
    previous_date = Book.objects.filter(pub_date__lt=pub_date).order_by('-pub_date').values_list('pub_date', flat=True).first()
    print(f"previous_date: {previous_date}")

    # Найти следующую дату с книгами
    next_date = Book.objects.filter(pub_date__gt=pub_date).order_by('pub_date').values_list('pub_date', flat=True).first()
    print(f"next_date: {next_date}")

    return render(request, 'books/books_list.html', {
        'books': books,
        'previous_date': previous_date,
        'next_date': next_date,
    })