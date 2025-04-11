from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from courses.views import CourseListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('courses.urls')),  # Include app URLs including the API
    path('', CourseListView.as_view(), name='course_list'),  # Root URL will show the course list
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
