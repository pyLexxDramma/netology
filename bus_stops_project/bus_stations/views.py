import csv
from django.shortcuts import render
from django.core.paginator import Paginator
from django.conf import settings

def bus_stations(request):
    page_number = request.GET.get('page', 1)
    with open(settings.BUS_STATION_CSV, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';') # используем csv.reader
        header = next(reader) # читаем строку заголовков
        reader = csv.DictReader(f, delimiter=';', fieldnames=header) # передаем заголовки в DictReader
        bus_stations_list = list(reader)

    paginator = Paginator(bus_stations_list, 10)
    page = paginator.get_page(page_number)

    context = {
        'page': page,
    }
    return render(request, 'bus_stations/bus_stations.html', context)