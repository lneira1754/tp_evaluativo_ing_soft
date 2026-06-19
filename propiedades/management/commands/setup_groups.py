from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from propiedades.models import Propiedad, Comentario, TipoPropiedad, Ubicacion, Servicio

class Command(BaseCommand):
    help = 'Crea los grupos de permisos por defecto (Agentes y Clientes) y les asigna permisos.'

    def handle(self, *args, **options):
        #1. Crear o recuperar grupos
        agentes_group, created_agentes = Group.objects.get_or_create(name='Agentes')
        clientes_group, created_clientes = Group.objects.get_or_create(name='Clientes')

        #Obtener ContentTypes de nuestros modelos
        ct_propiedad = ContentType.objects.get_for_model(Propiedad)
        ct_comentario = ContentType.objects.get_for_model(Comentario)
        ct_tipo = ContentType.objects.get_for_model(TipoPropiedad)
        ct_ubicacion = ContentType.objects.get_for_model(Ubicacion)
        ct_servicio = ContentType.objects.get_for_model(Servicio)

        #2. Permisos para el grupo Agentes (CRUD completo de propiedades, comentarios y auxiliares)
        permissions_agentes = Permission.objects.filter(
            content_type__in=[ct_propiedad, ct_comentario, ct_tipo, ct_ubicacion, ct_servicio]
        )
        agentes_group.permissions.set(permissions_agentes)
        self.stdout.write(self.style.SUCCESS(f'Grupo "Agentes" configurado con {permissions_agentes.count()} permisos.'))

        #3. Permisos para el grupo Clientes (Visualizar propiedades, CRUD comentarios propios y lectura general)
        #NOTA: En Django controlaremos en las vistas que solo puedan editar/borrar comentarios propios.
        #Les damos permisos para añadir comentarios, y ver propiedades y comentarios.
        permissions_clientes = Permission.objects.filter(
            content_type__in=[ct_propiedad, ct_comentario],
            codename__in=[
                'view_propiedad',
                'add_comentario',
                'change_comentario',
                'delete_comentario',
                'view_comentario',
            ]
        )
        clientes_group.permissions.set(permissions_clientes)
        self.stdout.write(self.style.SUCCESS(f'Grupo "Clientes" configurado con {permissions_clientes.count()} permisos.'))

        self.stdout.write(self.style.SUCCESS('¡Grupos y permisos configurados exitosamente!'))
