from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from propiedades.models import TipoPropiedad, Ubicacion, Servicio

from django.core.management import call_command

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea datos de prueba iniciales (Tipos, Ubicaciones, Servicios) y un administrador por defecto.'

    def handle(self, *args, **options):
        #0. Crear grupos y permisos por defecto
        call_command('setup_groups')

        #1. Crear Superusuario por defecto si no existe
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='inmobiliaria.donlucas@donlucas.com.ar',
                password='adminpassword123',
                first_name='Admin',
                last_name='Don Lucas',
                telefono='+54 358 2548367',
                biografia='Administrador general de la plataforma de Inmobiliaria Don Lucas.'
            )
            self.stdout.write(self.style.SUCCESS('Superusuario "admin" creado con contraseña "adminpassword123".'))
        else:
            self.stdout.write(self.style.WARNING('El superusuario "admin" ya existe.'))

        #2. Crear Tipos de Propiedades
        tipos = [
            ("Casa", "Propiedades residenciales unifamiliares con patio o jardín."),
            ("Departamento", "Unidades residenciales en edificios multifamiliares."),
            ("PH", "Propiedad Horizontal. Unidades sin expensas con acceso compartido."),
            ("Oficina", "Espacios comerciales para empresas y profesionales."),
            ("Terreno / Lote", "Lotes de tierra listos para desarrollo inmobiliario.")
        ]
        for nombre, desc in tipos:
            tipo, created = TipoPropiedad.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Tipo creado: {nombre}'))

        #3. Crear Ubicaciones de prueba
        ubicaciones = [
            ("Centro", "Río Cuarto", "Córdoba"),
            ("Banda Norte", "Río Cuarto", "Córdoba"),
            ("Alberdi", "Río Cuarto", "Córdoba"),
            ("Higueras", "Río Cuarto", "Córdoba"),
            ("Zona Sur", "Río Cuarto", "Córdoba"),
            ("Zona Este", "Río Cuarto", "Córdoba"),
            ("Zona Oeste", "Río Cuarto", "Córdoba"),
            ("Barrio Universidad", "Río Cuarto", "Córdoba"),
            ("Villa Dalcar", "Río Cuarto", "Córdoba")
        ]
        for barrio, ciudad, provincia in ubicaciones:
            loc, created = Ubicacion.objects.get_or_create(barrio=barrio, ciudad=ciudad, provincia=provincia)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Ubicación creada: {barrio}, {ciudad}'))

        #4. Crear Servicios / Amenities con iconos emoji
        servicios = [
            ("Piscina", "🏊"),
            ("Cochera", "🚗"),
            ("Seguridad 24hs", "🛡️"),
            ("Wi-Fi", "📶"),
            ("Parrilla / Quincho", "🍖"),
            ("Gimnasio", "🏋️"),
            ("Calefacción Central", "🔥"),
            ("Aire Acondicionado", "❄️"),
            ("Permite Mascotas", "🐾")
        ]
        for nombre, icono in servicios:
            serv, created = Servicio.objects.get_or_create(nombre=nombre, defaults={'icono': icono})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Servicio/Comodidad creado: {nombre} ({icono})'))

        self.stdout.write(self.style.SUCCESS('¡Poblado inicial de datos finalizado con éxito!'))
