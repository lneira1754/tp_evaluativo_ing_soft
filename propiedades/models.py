from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    biografia = models.TextField(blank=True, null=True, verbose_name="Biografía / Presentación")
    es_agente = models.BooleanField(default=False, verbose_name="Es Agente Inmobiliario")

    def __str__(self):
        return f"{self.username} ({'Agente' if self.es_agente or self.is_staff else 'Cliente'})"


class TipoPropiedad(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Tipo de Propiedad"
        verbose_name_plural = "Tipos de Propiedades"

    def __str__(self):
        return self.nombre


class Ubicacion(models.Model):
    barrio = models.CharField(max_length=100, verbose_name="Barrio / Zona")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad")
    provincia = models.CharField(max_length=100, verbose_name="Provincia")

    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"
        unique_together = ('barrio', 'ciudad', 'provincia')

    def __str__(self):
        return f"{self.barrio}, {self.ciudad} ({self.provincia})"


class Servicio(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    icono = models.CharField(max_length=10, blank=True, null=True, help_text="Emoji o clase de icono, ej: 🏊, 🚗, 🛡️, 📶")

    class Meta:
        verbose_name = "Servicio / Comodidad"
        verbose_name_plural = "Servicios / Comodidades"

    def __str__(self):
        return f"{self.icono or ''} {self.nombre}".strip()


class Propiedad(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título de la publicación")
    descripcion = models.TextField(verbose_name="Descripción de la propiedad")
    tipo = models.ForeignKey(TipoPropiedad, on_delete=models.PROTECT, related_name="propiedades", verbose_name="Tipo de Propiedad")
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.PROTECT, related_name="propiedades", verbose_name="Ubicación")
    servicios = models.ManyToManyField(Servicio, blank=True, related_name="propiedades", verbose_name="Servicios / Comodidades")
    
    precio = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio (USD)")
    superficie = models.IntegerField(verbose_name="Superficie Total (m²)")
    habitaciones = models.IntegerField(verbose_name="Cantidad de Habitaciones")
    banos = models.IntegerField(verbose_name="Cantidad de Baños")
    
    imagen = models.ImageField(upload_to='propiedades/', verbose_name="Imagen Principal")
    agente = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="propiedades", verbose_name="Agente asignado")
    activo = models.BooleanField(default=True, verbose_name="Publicación Activa")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Publicación")

    class Meta:
        verbose_name = "Propiedad"
        verbose_name_plural = "Propiedades"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo} - {self.ubicacion.barrio} (${self.precio})"


class Comentario(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name="comentarios", verbose_name="Propiedad")
    autor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="comentarios", verbose_name="Autor")
    contenido = models.TextField(verbose_name="Comentario")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Comentario de {self.autor.username} en {self.propiedad.titulo}"
