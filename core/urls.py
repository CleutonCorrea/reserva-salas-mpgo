from django.urls import path
from .views import (
    HomeView,
    EventsJSONView,
    ReservationCreateView,
    ReservationCancelView,
    ReservationEditView,
    UserRegisterView,
    UserLoginView,
    UserLogoutView,
    UserSessionView,
    UserProfileEditView,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    # Eventos / Reservas
    path('api/events/', EventsJSONView.as_view(), name='api_events'),
    path('api/events/create/', ReservationCreateView.as_view(), name='api_events_create'),
    path('api/events/<int:pk>/cancel/', ReservationCancelView.as_view(), name='api_events_cancel'),
    path('api/events/<int:pk>/edit/', ReservationEditView.as_view(), name='api_events_edit'),

    # Autenticação
    path('api/auth/register/', UserRegisterView.as_view(), name='api_auth_register'),
    path('api/auth/login/', UserLoginView.as_view(), name='api_auth_login'),
    path('api/auth/logout/', UserLogoutView.as_view(), name='api_auth_logout'),
    path('api/auth/session/', UserSessionView.as_view(), name='api_auth_session'),
    path('api/auth/profile/edit/', UserProfileEditView.as_view(), name='api_auth_profile_edit'),
]
