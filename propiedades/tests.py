from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from propiedades.models import TipoPropiedad, Ubicacion, Servicio, Propiedad, Comentario

User = get_user_model()

from django.core.management import call_command

class InmobiliariaTestCase(TestCase):
    def setUp(self):
        # 1. Ejecutar configuraciones iniciales de grupos
        call_command('setup_groups')
        self.agentes_group = Group.objects.get(name='Agentes')
        self.clientes_group = Group.objects.get(name='Clientes')
        
        # 2. Crear usuarios
        self.agente_user = User.objects.create_user(
            username='agente1',
            email='agente1@test.com',
            password='password123',
            es_agente=True,
            first_name='Juan',
            last_name='Agente'
        )
        self.agente_user.groups.add(self.agentes_group)

        self.cliente_user = User.objects.create_user(
            username='cliente1',
            email='cliente1@test.com',
            password='password123',
            es_agente=False,
            first_name='Pedro',
            last_name='Cliente'
        )
        self.cliente_user.groups.add(self.clientes_group)

        # 3. Crear auxiliares de modelos
        self.tipo_casa = TipoPropiedad.objects.create(nombre="Casa", descripcion="Residencial")
        self.ubicacion_rio_cuarto = Ubicacion.objects.create(barrio="Centro", ciudad="Río Cuarto", provincia="Córdoba")
        self.servicio_wifi = Servicio.objects.create(nombre="Wi-Fi", icono="📶")

        # 4. Crear propiedad de prueba
        # Creamos una imagen pequeña en memoria para testear la subida
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00'
            b'\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'
        )
        self.test_image = SimpleUploadedFile("test_house.gif", small_gif, content_type="image/gif")

        self.propiedad = Propiedad.objects.create(
            titulo="Hermosa Casa Centro",
            descripcion="Una casa espectacular con piscina y todos los servicios.",
            tipo=self.tipo_casa,
            ubicacion=self.ubicacion_rio_cuarto,
            precio=150000.00,
            superficie=120,
            habitaciones=3,
            banos=2,
            imagen=self.test_image,
            agente=self.agente_user
        )
        self.propiedad.servicios.add(self.servicio_wifi)

    def test_model_creations(self):
        """Verifica que los modelos se hayan creado correctamente con sus atributos y relaciones."""
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Propiedad.objects.count(), 1)
        self.assertEqual(self.propiedad.tipo.nombre, "Casa")
        self.assertEqual(self.propiedad.ubicacion.barrio, "Centro")
        self.assertIn(self.servicio_wifi, self.propiedad.servicios.all())

    def test_public_views_accessible(self):
        """Verifica que los usuarios sin registrar puedan ver la lista de propiedades y el detalle."""
        # Lista
        response_list = self.client.get(reverse('propiedad_list'))
        self.assertEqual(response_list.status_code, 200)
        self.assertContains(response_list, "Hermosa Casa Centro")

        # Detalle
        response_detail = self.client.get(reverse('propiedad_detail', args=[self.propiedad.pk]))
        self.assertEqual(response_detail.status_code, 200)
        self.assertContains(response_detail, "Una casa espectacular")

    def test_unregistered_user_cannot_comment(self):
        """Verifica que un usuario anónimo sea redirigido al login al intentar comentar."""
        response = self.client.post(reverse('comentario_create', args=[self.propiedad.pk]), {
            'contenido': '¿Sigue disponible?'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_registered_user_can_comment(self):
        """Verifica que un usuario cliente registrado pueda comentar en una propiedad."""
        # Iniciar sesión
        self.client.login(username='cliente1', password='password123')
        
        response = self.client.post(reverse('comentario_create', args=[self.propiedad.pk]), {
            'contenido': 'Me interesa mucho esta casa, ¿cuándo se puede visitar?'
        })
        # Redirige de vuelta al detalle de la propiedad
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comentario.objects.count(), 1)
        
        comentario = Comentario.objects.first()
        self.assertEqual(comentario.autor, self.cliente_user)
        self.assertEqual(comentario.contenido, 'Me interesa mucho esta casa, ¿cuándo se puede visitar?')

    def test_unauthorized_user_cannot_create_property(self):
        """Verifica que un usuario cliente (sin el permiso add_propiedad) no pueda crear una propiedad."""
        self.client.login(username='cliente1', password='password123')
        response = self.client.get(reverse('propiedad_create'))
        # Debería retornar un HTTP 403 Forbidden o redirigir según configuración (LoginRequired/PermissionRequired)
        # En Django, PermissionRequiredMixin retorna 403 por defecto para usuarios logueados sin el permiso.
        self.assertEqual(response.status_code, 403)

    def test_authorized_user_can_create_property(self):
        """Verifica que un agente inmobiliario (con el permiso add_propiedad) pueda ver el formulario de creación."""
        self.client.login(username='agente1', password='password123')
        response = self.client.get(reverse('propiedad_create'))
        self.assertEqual(response.status_code, 200)

    def test_user_registration(self):
        """Verifica que el registro de un nuevo usuario funcione y lo asigne al grupo adecuado."""
        response = self.client.post(reverse('registro'), {
            'username': 'nuevousuario',
            'first_name': 'Carlos',
            'last_name': 'Nuevo',
            'email': 'carlos@nuevo.com',
            'telefono': '12345678',
            'biografia': 'Hola, soy nuevo',
            'es_agente': 'on',
            'password1': 'password123!',
            'password2': 'password123!'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el usuario se haya creado
        user_exists = User.objects.filter(username='nuevousuario').exists()
        self.assertTrue(user_exists)
        
        # Verificar la asignación de grupos
        user = User.objects.get(username='nuevousuario')
        self.assertTrue(user.es_agente)
        self.assertTrue(user.groups.filter(name='Agentes').exists())
