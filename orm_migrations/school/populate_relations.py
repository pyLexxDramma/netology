import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')  
django.setup()

# -*- coding: utf-8 -*-
import json
from school.models import Student, Teacher

def populate_relations():
    try:
        # Load data from school.json
        with open('school.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: school.json not found.")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON in school.json.")
        return

    teachers_by_name = {}
    for teacher_data in data:
        if teacher_data['model'] == 'school.teacher':
            try:
                teacher = Teacher.objects.get(pk=teacher_data['pk'])
                teachers_by_name[teacher.name] = teacher
            except Teacher.DoesNotExist:
                print(f"Warning: Teacher with pk={teacher_data['pk']} not found in database.")

    for student_data in data:
        if student_data['model'] == 'school.student':
            try:
                student = Student.objects.get(pk=student_data['pk'])
                teacher_name = student_data['fields'].get('teacher_name') 

                if not teacher_name:
                    print(f"Warning: No teacher_name specified for student {student.name}.")
                    continue

                if teacher_name in teachers_by_name:
                    teacher = teachers_by_name[teacher_name]
                    student.teachers.add(teacher)
                    print(f"Relation created: {student.name} <-> {teacher.name}")
                else:
                    print(f"Warning: Teacher '{teacher_name}' not found for student {student.name}")

            except Student.DoesNotExist:
                print(f"Warning: Student with pk={student_data['pk']} not found in database.")
            except Exception as e:
                print(f"Error processing student {student_data['pk']}: {e}")

if __name__ == '__main__':
    populate_relations()