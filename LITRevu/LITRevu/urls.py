from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
import blog.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(
        template_name='authentication/login.html',
        redirect_authenticated_user=True),
        name='login'),
    path('home', blog.views.home, name='home')
]
