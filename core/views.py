from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime
from .models import Reservation, Room, UserProfile
import json

PASTEL_COLORS = [
    '#AEC6CF', '#FFB347', '#77DD77', '#FF6961',
    '#CFCFC4', '#F49AC2', '#CB99C9', '#FFD1DC'
]

def get_color_for_room(room_id):
    index = (room_id - 1) % len(PASTEL_COLORS)
    return PASTEL_COLORS[index]


class HomeView(TemplateView):
    template_name = 'calendario_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rooms = list(Room.objects.all())
        for room in rooms:
            room.color = get_color_for_room(room.id)
        context['rooms'] = rooms
        return context


# ── Events ────────────────────────────────────────────────────────────────────

class EventsJSONView(View):
    def get(self, request, *args, **kwargs):
        sala_id = request.GET.get('sala_id')
        reservations = Reservation.objects.select_related(
            'sala', 'usuario', 'usuario__perfil'
        ).all()

        if sala_id:
            reservations = reservations.filter(sala_id=sala_id)

        events = []
        for r in reservations:
            perfil = getattr(r.usuario, 'perfil', None)
            nm_completo = r.usuario.get_full_name() or r.usuario.username

            # Tooltip aprimorado
            tooltip_parts = [
                f"<b>{r.sala.nm_sala}</b>",
                f"Assunto: {r.obs_reserva or '<i>Sem observações</i>'}",
                f"De: {nm_completo}",
                f"E-mail: {r.usuario.email}"
            ]
            if perfil and perfil.nr_ramal:
                tooltip_parts.append(f'Ramal: {perfil.nr_ramal}')
            if perfil and perfil.nm_setor:
                tooltip_parts.append(f'Setor: {perfil.nm_setor}')

            can_cancel = (
                request.user.is_authenticated and (
                    r.usuario_id == request.user.id or request.user.is_staff
                )
            )

            color = get_color_for_room(r.sala.id)

            events.append({
                'id': r.id,
                'title': f'{r.sala.nm_sala} — {nm_completo}',
                'start': r.dth_inicio.isoformat(),
                'end': r.dth_fim.isoformat(),
                'can_cancel': can_cancel,
                'tooltip_info': '<br>'.join(tooltip_parts),
                'backgroundColor': color,
                'borderColor': color,
                'obs_reserva': r.obs_reserva or '',
                'sala_id': r.sala.id,
            })

        return JsonResponse(events, safe=False)


class ReservationCreateView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'status': 'error', 'errors': ['Login obrigatório para criar reservas.']},
                status=401,
            )
        try:
            data = json.loads(request.body)
            sala = Room.objects.get(pk=data.get('sala_id'))
            reserva = Reservation(
                sala=sala,
                usuario=request.user,
                dth_inicio=parse_datetime(data.get('start')),
                dth_fim=parse_datetime(data.get('end')),
                obs_reserva=data.get('obs_reserva', '').strip() or None,
            )
            reserva.clean()
            reserva.save()
            return JsonResponse({'status': 'success'})
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'errors': e.messages}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'errors': [str(e)]}, status=400)


class ReservationCancelView(View):
    def post(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'status': 'error', 'errors': ['Autenticação necessária.']},
                status=401,
            )
        try:
            reserva = Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            return JsonResponse(
                {'status': 'error', 'errors': ['Reserva não encontrada.']},
                status=404,
            )

        eh_dono = reserva.usuario_id == request.user.id
        eh_admin = request.user.is_staff

        if not (eh_dono or eh_admin):
            return JsonResponse(
                {'status': 'error', 'errors': ['Sem permissão para cancelar esta reserva.']},
                status=403,
            )

        reserva.delete()
        return JsonResponse({'status': 'success'})


class ReservationEditView(View):
    def post(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'errors': ['Autenticação necessária.']}, status=401)
        try:
            reserva = Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            return JsonResponse({'status': 'error', 'errors': ['Reserva não encontrada.']}, status=404)

        eh_dono = reserva.usuario_id == request.user.id
        eh_admin = request.user.is_staff

        if not (eh_dono or eh_admin):
            return JsonResponse({'status': 'error', 'errors': ['Sem permissão para editar esta reserva.']}, status=403)

        try:
            data = json.loads(request.body)
            sala = Room.objects.get(pk=data.get('sala_id'))
            
            reserva.sala = sala
            reserva.dth_inicio = parse_datetime(data.get('start'))
            reserva.dth_fim = parse_datetime(data.get('end'))
            reserva.obs_reserva = data.get('obs_reserva', '').strip() or None
            
            reserva.clean()
            reserva.save()
            return JsonResponse({'status': 'success'})
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'errors': e.messages}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'errors': [str(e)]}, status=400)


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserRegisterView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            nm_completo = data.get('nm_completo', '').strip()
            desc_email = data.get('desc_email', '').strip()
            senha = data.get('senha', '')
            senha_confirmacao = data.get('senha_confirmacao', '')
            nr_ramal = data.get('nr_ramal', '').strip()
            nm_setor = data.get('nm_setor', '').strip()

            erros = []
            if not nm_completo:
                erros.append('Nome completo é obrigatório.')
            if not desc_email:
                erros.append('E-mail é obrigatório.')
            elif User.objects.filter(email=desc_email).exists():
                erros.append('Este e-mail já está cadastrado.')
            if not senha:
                erros.append('Senha é obrigatória.')
            elif len(senha) < 8:
                erros.append('A senha deve ter no mínimo 8 caracteres.')
            if senha != senha_confirmacao:
                erros.append('As senhas não coincidem.')

            if erros:
                return JsonResponse({'status': 'error', 'errors': erros}, status=400)

            partes = nm_completo.split(' ', 1)
            usuario = User.objects.create_user(
                username=desc_email,
                email=desc_email,
                password=senha,
                first_name=partes[0],
                last_name=partes[1] if len(partes) > 1 else '',
            )
            UserProfile.objects.create(
                usuario=usuario,
                nr_ramal=nr_ramal or None,
                nm_setor=nm_setor or None,
            )
            login(request, usuario)
            return JsonResponse({
                'status': 'success',
                'usuario': {
                    'nm_completo': usuario.get_full_name(),
                    'desc_email': usuario.email,
                    'is_staff': usuario.is_staff,
                },
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'errors': [str(e)]}, status=500)


class UserLoginView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            desc_email = data.get('desc_email', '').strip()
            senha = data.get('senha', '')
            usuario = authenticate(request, username=desc_email, password=senha)
            if usuario is not None:
                login(request, usuario)
                return JsonResponse({
                    'status': 'success',
                    'usuario': {
                        'nm_completo': usuario.get_full_name(),
                        'desc_email': usuario.email,
                        'is_staff': usuario.is_staff,
                    },
                })
            return JsonResponse(
                {'status': 'error', 'errors': ['E-mail ou senha inválidos.']},
                status=400,
            )
        except Exception as e:
            return JsonResponse({'status': 'error', 'errors': [str(e)]}, status=500)


class UserLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return JsonResponse({'status': 'success'})


class UserSessionView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            perfil = getattr(request.user, 'perfil', None)
            return JsonResponse({
                'autenticado': True,
                'usuario': {
                    'nm_completo': request.user.get_full_name(),
                    'desc_email': request.user.email,
                    'is_staff': request.user.is_staff,
                    'nr_ramal': perfil.nr_ramal if perfil else '',
                    'nm_setor': perfil.nm_setor if perfil else '',
                },
            })
        return JsonResponse({'autenticado': False})


from django.contrib.auth import update_session_auth_hash

class UserProfileEditView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'errors': ['Autenticação necessária.']}, status=401)
            
        try:
            data = json.loads(request.body)
            nm_completo = data.get('nm_completo', '').strip()
            nr_ramal = data.get('nr_ramal', '').strip()
            nm_setor = data.get('nm_setor', '').strip()
            
            senha_antiga = data.get('senha_antiga', '')
            senha_nova = data.get('senha_nova', '')
            senha_confirmacao = data.get('senha_nova_confirmacao', '')
            
            erros = []
            if not nm_completo:
                erros.append('Nome completo é obrigatório.')
                
            if senha_nova:
                if not senha_antiga:
                    erros.append('A senha antiga é obrigatória para realizar a troca.')
                elif not request.user.check_password(senha_antiga):
                    erros.append('A senha antiga está incorreta.')
                    
                if len(senha_nova) < 8:
                    erros.append('A nova senha deve ter no mínimo 8 caracteres.')
                if senha_nova != senha_confirmacao:
                    erros.append('A confirmação da nova senha não coincide.')
                    
            if erros:
                return JsonResponse({'status': 'error', 'errors': erros}, status=400)
                
            # Atualiza info principal
            partes = nm_completo.split(' ', 1)
            request.user.first_name = partes[0]
            request.user.last_name = partes[1] if len(partes) > 1 else ''
            
            if senha_nova:
                request.user.set_password(senha_nova)
                
            request.user.save()
            
            if senha_nova:
                update_session_auth_hash(request, request.user)
                
            perfil, created = UserProfile.objects.get_or_create(usuario=request.user)
            perfil.nr_ramal = nr_ramal or None
            perfil.nm_setor = nm_setor or None
            perfil.save()
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'errors': [str(e)]}, status=500)
