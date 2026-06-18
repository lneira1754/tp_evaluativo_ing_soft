from django.urls import path
from propiedades import views

urlpatterns = [
    # Propiedades
    path('', views.PropiedadListView.as_view(), name='propiedad_list'),
    path('propiedad/<int:pk>/', views.PropiedadDetailView.as_view(), name='propiedad_detail'),
    path('propiedad/crear/', views.PropiedadCreateView.as_view(), name='propiedad_create'),
    path('propiedad/<int:pk>/editar/', views.PropiedadUpdateView.as_view(), name='propiedad_update'),
    path('propiedad/<int:pk>/eliminar/', views.PropiedadDeleteView.as_view(), name='propiedad_delete'),
    
    # Comentarios
    path('propiedad/<int:propiedad_id>/comentar/', views.comentario_create, name='comentario_create'),
    path('comentario/<int:pk>/editar/', views.ComentarioUpdateView.as_view(), name='comentario_update'),
    path('comentario/<int:pk>/eliminar/', views.ComentarioDeleteView.as_view(), name='comentario_delete'),
    
    # Autenticación y Panel de Control
    path('registro/', views.registro, name='registro'),
    path('panel/', views.DashboardView.as_view(), name='dashboard'),
]
