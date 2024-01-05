import random

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView, FormView

from users.tasks import send_verification_code, send_new_password
from users.forms import UserRegisterForm, UserForm
from users.models import User


class RegisterView(CreateView):
    """Контроллер для регистрации пользователя"""

    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')
    template_name = 'users/register.html'

    def form_valid(self, form):
        """
        Создает пароль для подтверждения email, сохраняет его в объекте пользователя
        и отправляет на email указанный при регистрации.
        Сохраняет пользователя в группе user.
        """

        user = form.save()
        key = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        user.key = key
        user.save()
        send_verification_code.delay(email=user.email, key=key)
        return super().form_valid(form)


class LoginView(BaseLoginView):
    """Контроллер для входа пользователя"""

    template_name = 'users/login.html'

    def get_success_url(self):
        """
        Если email пользователя верифицирован, перенаправляет на главную страницу,
        иначе перенаправляет на страницу верификации email.
        """

        user = self.request.user
        if user.is_verified:
            return reverse('study:home')
        return reverse('users:verification')


class LogoutView(BaseLogoutView):
    """Контроллер для выхода пользователя"""

    pass


class UserDitailView(LoginRequiredMixin, DetailView):
    """Контроллер для вывода информации о пользователе"""

    model = User

    def get_context_data(self, **kwargs):
        """Сохраняет в context_data текущего авторизованного пользователя"""

        context_data = super().get_context_data(**kwargs)
        context_data['user'] = self.request.user
        return context_data


class UserProfile(LoginRequiredMixin, UpdateView):
    """Контроллер для редактирования своего профиля текущим пользователем"""

    model = User
    form_class = UserForm

    def get_object(self, queryset=None):
        """Возвращает объект текущего пользователя"""

        return self.request.user

    def get_success_url(self):
        """Возвращает на страницу вывода информации о пользователе"""

        return reverse('users:user', args=[self.object.id])


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Контроллер для редактирования пользователя"""

    model = User
    form_class = UserForm
    success_url = reverse_lazy('users:users_list')

    def test_func(self):
        """Задает доступ к редактированию пользователя только для суперпользователя"""

        return self.request.user.is_superuser


class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Контроллер для удаления пользователя"""

    model = User
    success_url = reverse_lazy('users:users_list')

    def test_func(self):
        """Задает доступ к удалению пользователя только для суперпользователя"""

        return self.request.user.is_superuser


@login_required
def email_verification(request):
    """
    Верифицирует email пользователя. Если введенный пользователем код не верный, перенаправляет на
    страницу где сообщается что код не верный. Если код верный, перенаправляет на страницу где сообщается
    что код верный и устанавливает True в поле 'is_verified' пользователя.
    """

    if request.method == 'POST':
        input_key = request.POST.get('key')
        try:
            user = User.objects.get(key=input_key)
            user.is_verified = True
            user.save()
        except User.DoesNotExist:
            send_verification_code.delay(email=request.user.email, key=request.user.key)
            return render(request, 'users/unsuccessful_verification.html')
        return render(request, 'users/successful_verification.html')
    return render(request, 'users/verification.html')


def password_recovery(request):
    """
    Формирует новый пароль и пытается выслать его на email введенный пользователем.
    Если пользователь с таким email не зарегистрирован, перенаправляет на страницу где об этом сообщается.
    Если пользователь найден, высылает на его email новый пароль.
    """

    if request.method == 'POST':
        new_password = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        input_email = request.POST.get('email')
        try:
            user = User.objects.get(email=input_email)
            user.set_password(new_password)
            user.save()
            send_new_password.delay(email=user.email, new_password=new_password)
        except User.DoesNotExist:
            return render(request, 'users/unsuccessful_recovery.html')
        return render(request, 'users/successful_recovery.html')
    return render(request, 'users/password_recovery.html')


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Контроллер для вывода списка пользователей"""

    model = User

    def test_func(self):
        """Задает доступ к списку пользователей только для персонала"""

        user = self.request.user
        is_staff = user.is_staff
        return is_staff


class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = 'users/change_password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('study:home')

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


@login_required
@permission_required('users.set_is_active_user')
def user_toggle_activity(request, pk):
    """Блокирует/активирует пользователя"""

    user = User.objects.get(pk=pk)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()
    return redirect('users:users_list')

