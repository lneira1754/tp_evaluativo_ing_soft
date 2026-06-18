from propiedades.models import TipoPropiedad, Ubicacion

def inmobiliaria_globals(request):
    """
    Context processor que retorna datos globales accesibles en todos los templates.
    """
    return {
        'global_tipos': TipoPropiedad.objects.all(),
        'global_ubicaciones': Ubicacion.objects.all(),
        'inmobiliaria_contacto': {
            'nombre': 'Inmobiliaria Don Lucas',
            'telefono': '+54 358 2548367',
            'email': 'inmobiliaria.donlucas@donlucas.com.ar',
            'direccion': 'Constitución 600, Río Cuarto, Córdoba',
            'horario': 'Lunes a Viernes de 9:00 a 18:00 hs'
        }
    }
