from rest_framework import serializers
from django.conf import settings
from students.models import Course, Student

class CourseSerializer(serializers.ModelSerializer):
    students = serializers.PrimaryKeyRelatedField(many=True, queryset=Student.objects.all())
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ('id', 'name', 'students', 'students_count')

    def get_students_count(self, obj):
        return obj.students.count()

    def validate(self, data):
        if self.instance:
            students_count = self.instance.students.count()
        else:
            students_count = 0

        if 'students' in data:
            students_count += len(data['students'])

        if students_count > settings.MAX_STUDENTS_PER_COURSE:
            raise serializers.ValidationError(
                f"The maximum number of students per course has been exceeded ({settings.MAX_STUDENTS_PER_COURSE})"
            )
        return data