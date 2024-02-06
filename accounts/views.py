
from django.shortcuts import render, redirect
from django.views.generic import FormView
from .forms import UserRegistrationForm, UserUpdateForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
# Create your views here.

def send_authenticate_email(user, subject, template):
    message = render_to_string(template, {
        'user': user,
    })
    to_email = user.email
    send_eamil = EmailMultiAlternatives(subject, ' ', to=[to_email])
    send_eamil.attach_alternative(message, 'text/html')
    send_eamil.send()

class UserRegistrationView(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f'Your Account Registration Successfully!')
        login(self.request, user)
        send_authenticate_email(self.request.user, 'Registration Complete', 'accounts/register_send_email.html')
        return super().form_valid(form)
    
class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    def get_success_url(self):
        messages.success(self.request, f'Your Account Login Successfully!')
        return reverse_lazy('profile')
    
class UserLogoutView(LogoutView):   
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Logout Successfully!')
        return super().dispatch(request, *args, **kwargs)
    
class UserBankAccountUpdateView(LoginRequiredMixin,View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Profile Updated successfully!')
            send_authenticate_email(self.request.user, 'Profile Updated', 'accounts/profileupdate_send_email.html')
            return redirect('profile')  # Redirect to the user's profile page
        return render(request, self.template_name, {'form': form})

    
class PassWordChangeForm(LoginRequiredMixin, View):
    template_name = 'accounts/pass_change.html'

    def get(self, request,*args, **kwargs):
        form = PasswordChangeForm(request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request,*args, **kwargs):
        form = PasswordChangeForm(request.user,data = request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Password changed successfully!')
            # mail_subject = 'Password Change'
            # message = render_to_string('accounts/passchange_send_email.html',{
            #     'user' : self.request.user,
            # })
            # to_email = self.request.user.email
            # send_email = EmailMultiAlternatives(mail_subject, ' ', to=[to_email])
            # send_email.attach_alternative(message, 'text/html')
            # send_email.send()

            send_authenticate_email(self.request.user, 'Password Change', 'accounts/passchange_send_email.html')
            update_session_auth_hash(request, form.user)
            return redirect('profile')
        else:
            form = PasswordChangeForm(request.user)
        return render(request, self.template_name, {'form': form})