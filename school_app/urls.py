from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('', views.main_menu_view, name='main_menu'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search_view, name='search'),
    path('add_students/', views.add_student, name='add_student'),
    path('student_details/<int:student_id>/', views.student_details, name='student_details'),
    path('all_students/', views.all_students_view, name='all_students'),
    path('search_teachers/', views.search_teachers_view, name='search_teachers'),
    path('all_teachers/', views.all_teachers_view, name='all_teachers'),
    path('make_head_teacher/<int:user_id>/', views.make_head_teacher, name='make_head_teacher'),
    path('make_head_milk/<int:user_id>/', views.make_head_milk, name='make_head_milk'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('all_students_t/', views.all_students_view_t, name='all_students_t'),
    path('user_details/<int:user_id>/', views.user_details, name='user_details'),
    path('change_classroom/', views.change_classroom, name='change_classroom'),
    path('delete_student/<int:user_id>/', views.delete_student, name='delete_student'),
    path('clear_food_milk/', views.clear_food_milk, name='clear_food_milk'),
    path('make_teacher/<int:user_id>/', views.make_teacher, name='make_teacher')


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)