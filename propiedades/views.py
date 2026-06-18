from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q
from propiedades.models import Propiedad, Comentario, TipoPropiedad, Ubicacion, Servicio
from propiedades.forms import CustomUserCreationForm, PropiedadForm, ComentarioForm

#VISTAS DE AUTENTICACIÓN Y USUARIO

def registro(request):
    """
    Vista para registrar un nuevo usuario desde los templates.
    """
    if request.user.is_authenticated:
        return redirect('propiedad_list')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            #Asignar grupo según el rol seleccionado
            if user.es_agente:
                group_name = 'Agentes'
            else:
                group_name = 'Clientes'
            
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass #Si el comando setup_groups no se ha corrido, se manejará después
                
            #Loguear automáticamente
            login(request, user)
            messages.success(request, f"¡Registro exitoso! Bienvenido/a, {user.first_name or user.username}.")
            return redirect('propiedad_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Panel de control del usuario logueado.
    No requiere permisos específicos (solo estar logueado).
    Satisface: 'Otras vistas deben estar protegidas con login, sin necesidad de dar permisos específicos (read)'
    """
    template_name = 'propiedades/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.es_agente or user.is_staff:
            context['mis_propiedades'] = Propiedad.objects.filter(agente=user)
        else:
            context['mis_comentarios'] = Comentario.objects.filter(autor=user)
        return context


#VISTAS DE PROPIEDADES

class PropiedadListView(ListView):
    """
    Vista pública para listar y buscar propiedades.
    Accesible para usuarios no registrados.
    """
    model = Propiedad
    template_name = 'propiedades/propiedad_list.html'
    context_object_name = 'propiedades'
    paginate_by = 6

    def get_queryset(self):
        queryset = Propiedad.objects.filter(activo=True)
        
        #Filtros de búsqueda no es automatico, denle enter para confirmar la busqueda
        query = self.request.GET.get('q')
        tipo_id = self.request.GET.get('tipo')
        ubicacion_id = self.request.GET.get('ubicacion')
        precio_min = self.request.GET.get('precio_min')
        precio_max = self.request.GET.get('precio_max')

        if query:
            queryset = queryset.filter(
                Q(titulo__icontains=query) |
                Q(descripcion__icontains=query) |
                Q(ubicacion__barrio__icontains=query) |
                Q(ubicacion__ciudad__icontains=query)
            )
        if tipo_id:
            queryset = queryset.filter(tipo_id=tipo_id)
        if ubicacion_id:
            queryset = queryset.filter(ubicacion_id=ubicacion_id)
        if precio_min:
            queryset = queryset.filter(precio__gte=precio_min)
        if precio_max:
            queryset = queryset.filter(precio__lte=precio_max)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Mantener los parámetros de búsqueda en la paginación
        context['q'] = self.request.GET.get('q', '')
        context['tipo_selected'] = self.request.GET.get('tipo', '')
        context['ubicacion_selected'] = self.request.GET.get('ubicacion', '')
        context['precio_min'] = self.request.GET.get('precio_min', '')
        context['precio_max'] = self.request.GET.get('precio_max', '')
        return context


class PropiedadDetailView(DetailView):
    """
    Vista pública para el detalle de la propiedad.
    Muestra los comentarios. Permite agregar comentarios a usuarios autenticados.
    """
    model = Propiedad
    template_name = 'propiedades/propiedad_detail.html'
    context_object_name = 'propiedad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comentarios'] = self.object.comentarios.all()
        if self.request.user.is_authenticated:
            context['comentario_form'] = ComentarioForm()
        return context


class PropiedadCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Creación de propiedades. Protegido por permisos (Agentes y Administradores).
    """
    model = Propiedad
    form_class = PropiedadForm
    template_name = 'propiedades/propiedad_form.html'
    permission_required = 'propiedades.add_propiedad'
    success_url = reverse_lazy('propiedad_list')

    def form_valid(self, form):
        form.instance.agente = self.request.user
        messages.success(self.request, "¡Propiedad publicada exitosamente!")
        return super().form_valid(form)


class PropiedadUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Edición de propiedades. Solo el agente asignado o administradores pueden editar.
    """
    model = Propiedad
    form_class = PropiedadForm
    template_name = 'propiedades/propiedad_form.html'

    def test_func(self):
        propiedad = self.get_object()
        #Tiene permiso o es el agente asignado
        return self.request.user.has_perm('propiedades.change_propiedad') or propiedad.agente == self.request.user

    def get_success_url(self):
        messages.success(self.request, "Propiedad actualizada correctamente.")
        return reverse('propiedad_detail', kwargs={'pk': self.object.pk})


class PropiedadDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Eliminación de propiedades. Solo el agente asignado o administradores pueden borrar.
    """
    model = Propiedad
    template_name = 'propiedades/propiedad_confirm_delete.html'
    success_url = reverse_lazy('propiedad_list')

    def test_func(self):
        propiedad = self.get_object()
        return self.request.user.has_perm('propiedades.delete_propiedad') or propiedad.agente == self.request.user

    def post(self, request, *args, **kwargs):
        messages.success(self.request, "Propiedad eliminada con éxito.")
        return super().post(request, *args, **kwargs)


#VISTAS DE COMENTARIOS

def comentario_create(request, propiedad_id):
    """
    Crea un comentario. Protegido por login (debe estar autenticado en la pagina).
    """
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesión para dejar un comentario.")
        return redirect('login')
        
    propiedad = get_object_or_404(Propiedad, pk=propiedad_id)
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.propiedad = propiedad
            comentario.autor = request.user
            comentario.save()
            messages.success(request, "Comentario añadido con éxito.")
        else:
            messages.error(request, "Error al publicar el comentario.")
    return redirect('propiedad_detail', pk=propiedad_id)


class ComentarioUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Edición de comentario. Autor del comentario, Agentes o Administradores pueden editar.
    """
    model = Comentario
    form_class = ComentarioForm
    template_name = 'propiedades/comentario_form.html'

    def test_func(self):
        comentario = self.get_object()
        return self.request.user.has_perm('propiedades.change_comentario') or comentario.autor == self.request.user

    def get_success_url(self):
        messages.success(self.request, "Comentario editado con éxito.")
        return reverse('propiedad_detail', kwargs={'pk': self.object.propiedad.pk})


class ComentarioDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Eliminación de comentarios. Autor, Agentes o Administradores pueden borrar.
    """
    model = Comentario
    template_name = 'propiedades/comentario_confirm_delete.html'

    def test_func(self):
        comentario = self.get_object()
        return self.request.user.has_perm('propiedades.delete_comentario') or comentario.autor == self.request.user

    def get_success_url(self):
        messages.success(self.request, "Comentario eliminado con éxito.")
        return reverse('propiedad_detail', kwargs={'pk': self.object.propiedad.pk})
