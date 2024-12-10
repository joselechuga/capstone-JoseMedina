from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'password', 'rol']
        widgets = {
            'password': forms.PasswordInput(),  #contraseña de tipo password
        }
