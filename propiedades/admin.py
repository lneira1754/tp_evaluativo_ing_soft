from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from propiedades.models import CustomUser, TipoPropiedad, Ubicacion, Servicio, Propiedad, Comentario

#Registro del modelo de usuario personalizado en el admin de Django
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'telefono', 'es_agente', 'is_staff', 'is_active')
    list_filter = ('es_agente', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Perfil', {'fields': ('telefono', 'biografia', 'es_agente')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Perfil', {'fields': ('telefono', 'biografia', 'es_agente')}),
    )
    search_fields = ('username', 'email', 'telefono')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)


#Registro de Tipo de Propiedad
@admin.register(TipoPropiedad)
class TipoPropiedadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre', 'descripcion')


#Registro de Ubicacion
@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ('barrio', 'ciudad', 'provincia')
    list_filter = ('ciudad', 'provincia')
    search_fields = ('barrio', 'ciudad', 'provincia')
    ordering = ('provincia', 'ciudad', 'barrio')


#Registro de Servicio
@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'icono')
    search_fields = ('nombre',)


#Registro de Propiedad
@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'ubicacion', 'precio', 'superficie', 'habitaciones', 'banos', 'agente', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'tipo', 'ubicacion', 'fecha_creacion', 'agente')
    search_fields = ('titulo', 'descripcion', 'ubicacion__barrio', 'ubicacion__ciudad', 'agente__username')
    ordering = ('-fecha_creacion', 'precio')
    filter_horizontal = ('servicios',)  #Para una mejor selección de comodidades (Relacion muchos a muchos)


#Registro de Comentario
@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('autor', 'propiedad', 'fecha_creacion', 'short_content')
    list_filter = ('fecha_creacion', 'autor')
    search_fields = ('contenido', 'autor__username', 'propiedad__titulo')
    ordering = ('-fecha_creacion',)

    def short_content(self, obj):
        if len(obj.contenido) > 50:
            return obj.contenido[:47] + "..."
        return obj.contenido
    short_content.short_description = 'Contenido'
