from django.shortcuts import render, get_object_or_404
from phones.models import Phone

def catalog(request):
    template = 'catalog.html'
    sort = request.GET.get('sort', 'name')  # Default sorting by name
    if sort == 'name':
        phones = Phone.objects.all().order_by('name')
    elif sort == 'min_price':
        phones = Phone.objects.all().order_by('price')
    elif sort == 'max_price':
        phones = Phone.objects.all().order_by('-price')
    else:
        phones = Phone.objects.all().order_by('name')  # Fallback to name

    context = {'phones': phones, 'sort': sort}
    return render(request, template, context)


def product(request, slug):
    template = 'product.html'
    phone = get_object_or_404(Phone, slug=slug)
    context = {'phone': phone}
    return render(request, template, context)