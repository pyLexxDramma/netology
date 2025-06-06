# -*- coding: utf-8 -*-
import pytest
from rest_framework.test import APIClient
from model_bakery import baker
from django.urls import reverse
from students.models import Course, Student
from rest_framework import status
from django.conf import settings
from pytest import mark

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def course_factory():
    def factory(**kwargs):
        return baker.make(Course, **kwargs)
    return factory

@pytest.fixture
def student_factory():
    def factory(**kwargs):
        return baker.make(Student, **kwargs)
    return factory


@pytest.mark.django_db
def test_retrieve_course(api_client, course_factory):
    course = course_factory()
    url = reverse("courses-detail", args=[course.id])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == course.id

@pytest.mark.django_db
def test_list_courses(api_client, course_factory):
    courses = course_factory(_quantity=3)
    url = reverse("courses-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == len(courses)
    for course in courses:
        assert any(c["id"] == course.id for c in data)

@pytest.mark.django_db
def test_filter_courses_by_id(api_client, course_factory):
    courses = course_factory(_quantity=3)
    course_to_filter = courses[1]
    url = reverse("courses-list")
    response = api_client.get(url, data={"id": course_to_filter.id})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == course_to_filter.id

@pytest.mark.django_db
def test_filter_courses_by_name(api_client, course_factory):
    course_name = "Test Course"
    courses = course_factory(_quantity=3)
    course_to_filter = course_factory(name=course_name)
    url = reverse("courses-list")
    response = api_client.get(url, data={"name": course_name})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == course_name

@pytest.mark.django_db
def test_create_course(api_client, student_factory):
    student = student_factory()
    course_data = {
        "name": "New Course",
        "students": [student.id],
    }
    url = reverse("courses-list")
    response = api_client.post(url, course_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == course_data["name"]
    assert data["students"] == [student.id]

@pytest.mark.django_db
def test_update_course(api_client, course_factory, student_factory):
    course = course_factory()
    student = student_factory()
    updated_data = {
        "name": "Updated Course Name",
        "students": [student.id],
    }
    url = reverse("courses-detail", args=[course.id])
    response = api_client.put(url, updated_data, format="json")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == updated_data["name"]
    assert data["students"] == [student.id]

@pytest.mark.django_db
def test_delete_course(api_client, course_factory):
    course = course_factory()
    url = reverse("courses-detail", args=[course.id])
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(Course.DoesNotExist):
        Course.objects.get(id=course.id)

@pytest.mark.django_db
@pytest.mark.parametrize(
    "num_students, expected_status",
    [
        (settings.MAX_STUDENTS_PER_COURSE - 1, status.HTTP_201_CREATED),
        (settings.MAX_STUDENTS_PER_COURSE, status.HTTP_201_CREATED),
        (settings.MAX_STUDENTS_PER_COURSE + 1, status.HTTP_400_BAD_REQUEST),
    ],
)
def test_create_course_with_student_limit(
    settings, api_client, student_factory, num_students, expected_status
):
    settings.MAX_STUDENTS_PER_COURSE = 20

    students = student_factory(_quantity=num_students)

    course_data = {
        "name": "New Course",
        "students": [student.id for student in students],
    }

    url = reverse("courses-list")
    response = api_client.post(url, course_data, format="json")

    assert response.status_code == expected_status

    if expected_status == status.HTTP_201_CREATED:
        assert Course.objects.filter(name=course_data["name"]).exists()
    elif expected_status == status.HTTP_400_BAD_REQUEST:
        assert not Course.objects.filter(name=course_data["name"]).exists()


@pytest.mark.django_db
def test_update_course_with_student_limit(api_client, course_factory, student_factory):
    course = course_factory()

    students = student_factory(_quantity=settings.MAX_STUDENTS_PER_COURSE - 1)

    student_ids = [student.id for student in students]

    course.students.set(student_ids)

    new_student = student_factory()

    updated_data = {
        "name": course.name,
        "students": student_ids + [new_student.id],
    }

    url = reverse("courses-detail", args=[course.id])
    response = api_client.put(url, updated_data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST