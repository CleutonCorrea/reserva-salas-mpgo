from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Room, Reservation, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil Estendido'


class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('nm_sala', 'nm_predio', 'qtd_capacidade', 'exige_aprovacao')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nm_sala', 'nm_predio', 'nr_andar', 'end_sala', 'cdg_sala', 'qtd_capacidade', 'obs_sala')
        }),
        ('Recursos Físicos e Configurações da Sala', {
            'fields': ('projetor', 'tela', 'quadro_branco', 'videoconferencia', 'acessibilidade')
        }),
        ('Regras de Reserva', {
            'fields': ('exige_aprovacao', 'aprovador')
        }),
    )

admin.site.register(Reservation)
