from courses.models import Course, Student
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Course
from .serializers import CourseSerializer

class CourseListAPI(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

class CourseDetailAPI(APIView):
    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    
class EnrollStudentAPI(APIView):
    def post(self, request):
        student_email = request.data.get('email')
        course_id = request.data.get('course_id')

        if not student_email or not course_id:
            return Response({'error': 'Email and course_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        student, created = Student.objects.get_or_create(email=student_email)

        # Optional: Add name if passed (enhancement)
        student_name = request.data.get('name')
        if student_name:
            student.name = student_name
            student.save()

        if course in student.enrolled_courses.all():
            return Response({'message': f'{student.email} is already enrolled in {course.title}'})
        else:
            student.enrolled_courses.add(course)
            return Response({'message': f'{student.email} has been enrolled in {course.title}'})