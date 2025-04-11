from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path
from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.index, name='index'),
    path('register/', core_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('dashboard/', core_views.dashboard, name='dashboard'),
    path('create-task/', core_views.create_task, name='create_task'),
    path('accept-task/<int:task_id>/', core_views.accept_task, name='accept_task'),
    path('support-task/<int:task_id>/', core_views.support_task, name='support_task'),
    path('leave-review/', core_views.leave_review, name='leave_review'),
    path('ratings/', core_views.ratings_view, name='ratings'),
    path('edit-review/<int:review_id>/', core_views.edit_review, name='edit_review'),
    path('delete-review/<int:review_id>/', core_views.delete_review, name='delete_review'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)