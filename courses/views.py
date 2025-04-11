from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy,reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Course, Lesson, Student
from .forms import CourseForm, LessonForm, CourseEnrollmentForm, UserUpdateForm


@method_decorator(login_required, name='dispatch')
class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        context['lessons'] = course.lessons.all()

        try:
            student = Student.objects.get(email=self.request.user.email)
            context['student'] = student
            # Filter completed lessons by current course only
            context['completed_lessons'] = student.completed_lessons.filter(course=course)
        except Student.DoesNotExist:
            context['student'] = None
            context['completed_lessons'] = []

        # Count lessons for current course only
        total_lessons = course.lessons.count()
        completed_lessons_count = context['completed_lessons'].count()

        # Debugging: Print the counts to the console or log
        print(f"Total Lessons: {total_lessons}, Completed Lessons: {completed_lessons_count}")

        progress = 0
        if total_lessons > 0:
            progress = (completed_lessons_count / total_lessons) * 100

        context['progress'] = round(progress, 2)  # Calculate the progress percentage

        return context


@method_decorator(login_required, name='dispatch')
class CourseCreateView(CreateView):
    model = Course
    fields = ['title', 'description', 'duration', 'thumbnail']
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')

    def form_valid(self, form):
        messages.success(self.request, "Course created successfully!")
        return super().form_valid(form)


from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_staff)
def course_update(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    form = CourseForm(request.POST or None, request.FILES or None, instance=course)
    if form.is_valid():
        form.save()
        messages.success(request, "Course updated successfully!")
        return redirect('course_list')
    return render(request, 'courses/course_form.html', {'form': form})


@user_passes_test(lambda u: u.is_staff)
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted successfully!")
        return redirect('course_list')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})


@user_passes_test(lambda u: u.is_staff)
def lesson_create(request):
    form = LessonForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Lesson created successfully!")
        return redirect('course_list')
    return render(request, 'courses/lesson_form.html', {'form': form})


@user_passes_test(lambda u: u.is_staff)
def lesson_update(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    form = LessonForm(request.POST or None, instance=lesson)
    if form.is_valid():
        form.save()
        messages.success(request, "Lesson updated successfully!")
        return redirect('course_list')
    return render(request, 'courses/lesson_form.html', {'form': form})


@user_passes_test(lambda u: u.is_staff)
def lesson_delete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == "POST":
        lesson.delete()
        messages.success(request, "Lesson deleted successfully!")
        return redirect('course_list')
    return render(request, 'courses/lesson_confirm_delete.html', {'lesson': lesson})


def enroll_student(request):
    form = CourseEnrollmentForm(request.POST or None)
    if form.is_valid():
        student_name = form.cleaned_data['student_name']
        student_email = form.cleaned_data['student_email']
        course = form.cleaned_data['course']
        student, created = Student.objects.get_or_create(email=student_email)
        if created:
            student.name = student_name
            student.save()
        if course in student.enrolled_courses.all():
            messages.error(request, 'You are already enrolled in this course.')
        else:
            student.enrolled_courses.add(course)
            messages.success(request, 'Successfully enrolled!')
            return render(request, 'courses/enrollment_success.html', {'student': student, 'course': course})
    return render(request, 'courses/enroll_student.html', {'form': form})


def course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = course.students.all()
    return render(request, 'courses/course_students.html', {'course': course, 'students': students})


def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Registration successful!")
        return redirect('/')
    return render(request, 'courses/register.html', {'form': form})


def user_login(request):
    form = AuthenticationForm(data=request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Login successful!")
        return redirect('/')
    elif request.method == 'POST':
        messages.error(request, "Invalid username or password.")
    return render(request, 'courses/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('/')


@login_required
def profile(request):
    form = UserUpdateForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    return render(request, 'courses/profile.html', {'form': form})


@login_required
def mark_completed(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    student = get_object_or_404(Student, email=request.user.email)
    student.completed_lessons.add(lesson)
    lesson.completion_status = True
    lesson.save()
    return redirect('course_detail', pk=lesson.course.id)
