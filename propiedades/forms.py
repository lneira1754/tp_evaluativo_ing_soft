from django import forms
from django.contrib.auth.forms import UserCreationForm
from propiedades.models import CustomUser, Propiedad, Comentario

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")
    email = forms.EmailField(required=True, label="Correo Electrónico")
    telefono = forms.CharField(max_length=20, required=False, label="Teléfono de Contacto")
    biografia = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label="Biografía / Presentación")
    es_agente = forms.BooleanField(required=False, label="Registrarse como Agente Inmobiliario (Permite publicar propiedades)")

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'telefono', 'biografia', 'es_agente')


class PropiedadForm(forms.ModelForm):
    class Meta:
        model = Propiedad
        fields = ['titulo', 'descripcion', 'tipo', 'ubicacion', 'servicios', 'precio', 'superficie', 'habitaciones', 'banos', 'imagen', 'activo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'servicios': forms.CheckboxSelectMultiple(),
        }


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe tu comentario aquí...'}),
        }
