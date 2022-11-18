from django import forms
from django.forms import DateInput, PasswordInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

#Modelo para registro denuevos usuarios no administradores
class UserRegisterForm(UserCreationForm):
    email=forms.EmailField()
    password1=forms.CharField(label="Contraseña", widget=PasswordInput)
    password2= forms.CharField(label="Confirmar Contraseña", widget=PasswordInput)

    class Meta:
        model = User
        fields = ['username','email','password1','password2']
        help_texts = {k:"" for k in fields}

