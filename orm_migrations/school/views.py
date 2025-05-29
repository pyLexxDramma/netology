from django.shortcuts import render
from .models import Student

def students_list(request):
    students = Student.objects.all()
    context = {'students': students}
    return render(request, 'school/students_list.html', context)