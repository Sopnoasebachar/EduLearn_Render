from rest_framework import serializers
from .models import Course, Lesson

# Serializer for the Lesson model
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content','video_url']

# Serializer for the Course model
class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)  # This will include lessons in the course response

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'duration', 'lessons']
