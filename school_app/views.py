from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Classroom, Student, Profile, Code, Food_milk
from .forms import RegistrationForm, ProfileForm, CreateCodeForm, MainMenuForm, AvatarForm, StudentForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.utils import IntegrityError
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect, JsonResponse
from random import randint
from fuzzywuzzy import fuzz
from datetime import date
import time
from PIL import Image
import pytesseract
import cv2
import numpy as np


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():

            get_code = form.cleaned_data['code']
            print(get_code)
            if Code.objects.filter(code=get_code).exists():
                try:
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        password=form.cleaned_data['password']
                    )

                    code = Code.objects.get(code=get_code)
                    whoami = None
                    if code.code_priority == 4:
                        classroom = Classroom(user=user, class_number=form.cleaned_data['classroom'],
                                              class_letter=form.cleaned_data['classroom_letter'])
                        classroom.save()
                        whoami = 3
                    elif code.code_priority == 3 or code.code_priority == 1:
                        classroom1 = Classroom.objects.get(user_id=code.user)
                        classroom = Classroom(user=user, class_number=classroom1.class_number,
                                              class_letter=classroom1.class_letter)
                        classroom.save()
                        whoami = 2
                    profile = Profile(user=user, full_name=form.cleaned_data['full_name'],
                                      whoami=whoami)
                    profile.save()
                    return redirect('main_menu')
                except IntegrityError:
                    messages.error(request, 'Пользователь с таким именем уже существует.')
                    print('Пользователь с таким именем уже существует.')
                except Exception as e:
                    messages.error(request, f'An error occurred: {str(e)}')
                    print(e)
            else:
                messages.error(request, 'Код неверный')
                print('код неверный')
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def main_menu_view(request):
    usr = request.user
    classroom = None
    form = MainMenuForm()
    try:
        classroom = Classroom.objects.get(user_id=usr)
    except Exception as e:
        print(str(e))
    profile = get_object_or_404(Profile, user_id=usr)
    if request.method == 'POST':
        form = MainMenuForm(request.POST)
        if form.is_valid():
            class_number = classroom.class_number
            class_letter = classroom.class_letter
            num_paid = form.cleaned_data['num_paid']
            num_discount = form.cleaned_data['num_discount']
            num_milk = form.cleaned_data['milk']
            current_date = date.today()

            data = Food_milk(class_number=class_number, class_letter=class_letter, num_paid=num_paid,
                             num_discount=num_discount, num_milk=num_milk, date=current_date)
            data.save()
        else:
            form = MainMenuForm()

    context = {
        'form': form,
        'classroom': classroom,
        'profile': profile
    }
    return render(request, 'main_menu.html', context)


@login_required
def search_view(request):
    user_profile = get_object_or_404(Profile, user=request.user)
    if user_profile.whoami == 4:
        return redirect('search_teachers')

    else:
        if request.method == 'POST':
            search_query = request.POST.get('search_query', '')
            students = Student.objects.all()
            search_results = []

            for student in students:
                similarity = fuzz.token_sort_ratio(search_query, student.full_name)
                print(student, similarity)
                if similarity >= 80:
                    search_results.append(student)

            user_profile = get_object_or_404(Profile, user=request.user)

            if user_profile.whoami != 4:
                classroom = get_object_or_404(Classroom, user_id=request.user)
                class_letter = classroom.class_letter
                class_num = classroom.class_number

                search_results = [student for student in search_results if
                                  student.class_number == class_num and student.class_letter == class_letter]

            return render(request, 'search.html', {'students': search_results, 'student_query': search_query})
        else:
            return render(request, 'search.html')


@login_required
def search_teachers_view(request):
    if request.method == 'POST':
        search_query = request.POST.get('search_query', '')
        print(search_query)
        teacher_profiles = Profile.objects.all()
        student_profiles = Student.objects.all()

        teacher_search_results = []
        student_search_results = []

        for teacher_profile in teacher_profiles:
            similarity = fuzz.token_sort_ratio(search_query, teacher_profile.full_name)
            if similarity >= 80:
                teacher_search_results.append(teacher_profile)

        for student_profile in student_profiles:
            similarity = fuzz.token_sort_ratio(search_query, student_profile.full_name)
            if similarity >= 80:
                student_search_results.append(student_profile)

        return render(request, 'search_teachers.html',
                      {'teachers': teacher_search_results, 'students': student_search_results,
                       'search_query': search_query})
    else:
        return render(request, 'search_teachers.html', {})


@login_required
def make_head_teacher(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    profile.whoami = 4
    profile.save()
    return redirect('search_teachers')


@login_required
def make_head_milk(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    profile.whoami = 1
    profile.save()
    return redirect('search_teachers')


@login_required
def make_teacher(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    profile.whoami = 3
    profile.sav()

@login_required
def change_classroom(request):
    if request.method == 'POST':
        class_number = request.POST.get('class_number')
        class_letter = request.POST.get('class_letter')
        new_class_number = request.POST.get('new_class_number')
        new_class_letter = request.POST.get('new_class_letter')
        students = Student.objects.filter(class_letter=class_letter, class_number=class_number)

        for student in students:
            student.class_letter = new_class_letter
            student.class_number = new_class_number
            student.save()

    referring_page = request.META.get('HTTP_REFERER', '/')
    return HttpResponseRedirect(referring_page)


@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('search_teachers')


@login_required
def delete_student(request, user_id):
    user = get_object_or_404(Student, id=user_id)
    user.delete()
    return redirect('search_teachers')


@login_required
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('search')
    else:
        form = StudentForm()

    return render(request, 'add_student.html', {'form': form})


def get_best_rotation(image):
    rotations = [0, 90, 180, 270]
    max_text_count = 0
    best_rotation = 0

    for rotation in rotations:
        rotated_image = image.rotate(rotation)
        text = pytesseract.image_to_string(rotated_image)
        text_count = len(text)

        if text_count > max_text_count:
            max_text_count = text_count
            best_rotation = rotation

    return best_rotation

@login_required
def student_details(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        new_full_name = request.POST.get('new_full_name')
        new_class_number = request.POST.get('new_class_number')
        new_class_letter = request.POST.get('new_class_letter')

        new_passport_scan = request.FILES.get('new_passport_scan')
        new_registration_scan = request.FILES.get('new_registration_scan')
        new_birth_certificate_scan = request.FILES.get('new_birth_certificate_scan')

        if new_full_name:
            student.full_name = new_full_name
            student.save()

        if new_passport_scan:
            image = Image.open(new_passport_scan)
            best_rotation = get_best_rotation(image)
            new_passport_scan = image.rotate(best_rotation)

            student.passport_scan = new_passport_scan
            student.save()

        if new_registration_scan:
            image = Image.open(new_registration_scan)
            best_rotation = get_best_rotation(image)
            new_registration_scan = image.rotate(best_rotation)

            student.registration_scan = new_registration_scan
            student.save()

        if new_birth_certificate_scan:
            image = Image.open(new_birth_certificate_scan)
            best_rotation = get_best_rotation(image)
            new_birth_certificate_scan = image.rotate(best_rotation)

            student.birth_certificate_scan = new_birth_certificate_scan
            student.save()

        if new_class_number:
            student.class_number = new_class_number
            student.save()

        if new_class_letter:
            student.class_letter = new_class_letter
            student.save()

    return render(request, 'student_details.html', {'student': student})


@login_required
def all_students_view(request):
    students = Student.objects.all()

    user_profile = get_object_or_404(Profile, user=request.user)

    if user_profile.whoami != 4:
        classroom = get_object_or_404(Classroom, user_id=request.user)
        class_letter = classroom.class_letter
        class_num = classroom.class_number
        students = students.filter(class_number=class_num, class_letter=class_letter)

    return render(request, 'search.html', {'students': students})


@login_required
def all_teachers_view(request):
    teachers = Profile.objects.all()
    return render(request, 'search_teachers.html', {'teachers': teachers})


@login_required
def all_students_view_t(request):
    students = Student.objects.all()
    return render(request, 'search_teachers.html', {'students': students})


@login_required
def user_details(request, user_id):
    profile = get_object_or_404(Profile, id=user_id)
    if request.method == 'POST':
        new_full_name = request.POST.get('new_full_name')
        new_class_number = request.POST.get('new_class_number')
        new_class_letter = request.POST.get('new_class_letter')

        if new_full_name:
            profile.full_name = new_full_name
            profile.save()

        if new_class_number:
            profile.class_number = new_class_number
            profile.save()

        if new_class_letter:
            profile.class_letter = new_class_letter
            profile.save()

    return render(request, 'user_details.html', {'profile': profile})


@login_required
def profile_view(request):
    user = request.user

    food_milk_data = None
    profile = get_object_or_404(Profile, user=user)
    if profile.whoami == 1:
        food_milk_data = Food_milk.objects.all()

    avatar_form = AvatarForm()
    code_form = CreateCodeForm()
    classroom = None
    try:
        classroom = Classroom.objects.get(user=user)
    except Exception as e:
        print(str(e))
    try:
        existing_code = Code.objects.filter(user=user).first()
        if (existing_code.code_end_h * 60 + existing_code.code_end_m) * 60 < existing_code.code_end_time_in_sec < time.time():
            existing_code.delete()
    except Exception as e:
        print(f'An error occurred: {str(e)}')
    if request.method == 'POST':
        avatar_form = AvatarForm(request.POST, request.FILES)
        create_code_form = CreateCodeForm(request.POST)
        new_full_name = request.POST.get('new_full_name')
        new_class_number = request.POST.get('new_class_number')
        new_class_letter = request.POST.get('new_class_letter')

        if avatar_form.is_valid():
            if 'avatar' in request.FILES:
                profile.avatar = avatar_form.cleaned_data['avatar']
                profile.save()
            elif 'delete_avatar' in request.POST:
                default_storage.delete(profile.avatar.path)
                profile.avatar = None
                profile.save()

        if new_full_name:
            profile.full_name = new_full_name

        if new_class_number:
            classroom.class_number = new_class_number

        if new_class_letter:
            classroom.class_letter = new_class_letter

        if new_full_name or new_class_number or new_class_letter:
            profile.save()
            classroom.save()

        if create_code_form.is_valid():
            expiration_hours = create_code_form.cleaned_data['expiration_hours']

            if expiration_hours:
                if expiration_hours > 24:
                    messages.error(request, "Срок действия кода не может быть больше 24 часов.")
                else:
                    try:
                        existing_code = Code.objects.filter(user=user).first()
                        existing_code.delete()

                    except Exception as e:
                        print(f'An error occurred: {str(e)}')

                    code = randint(100000, 999999)

                    if time.localtime().tm_hour + expiration_hours >= 24:
                        time_h = time.localtime().tm_hour + expiration_hours - 24
                    else:
                        time_h = time.localtime().tm_hour + expiration_hours

                    code_priority = profile.whoami

                    Code.objects.create(user=user, code=code, code_end_h=time_h, code_end_m=time.localtime().tm_min,
                                        code_end_time_in_sec=time.time() + expiration_hours * 3600,
                                        code_priority=code_priority)

    existing_code = Code.objects.filter(user=user).first()

    return render(request, 'profile.html', {
        'user': user,
        'profile_form': ProfileForm,
        'code_form': code_form,
        'classroom': classroom,
        'profile': profile,
        'avatar_form': avatar_form,
        'existing_code': existing_code,
        'food_milk_data': food_milk_data,

    })


def login_view(request):
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main_menu')

    return render(request, 'registration/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('main_menu')

@login_required
def clear_food_milk(request):
    if request.user.profile.whoami == 1:
        Food_milk.objects.all().delete()
        return JsonResponse({'message': 'Список успешно очищен.'})
    return JsonResponse({'message': 'Недостаточно прав для выполнения операции.'})