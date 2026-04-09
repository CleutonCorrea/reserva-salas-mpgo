from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models import Room, Reservation

class ReservationOverlapTest(TestCase):
    def setUp(self):
        self.room = Room.objects.create(
            nm_sala="Sala de Reuniões 1",
            qtd_capacidade=10,
            projetor=True,
            tela=True,
            obs_sala="Sala principal"
        )
        self.now = timezone.now()
        
    def test_double_booking_raises_error(self):
        # Primeira reserva
        start_time1 = self.now.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time1 = start_time1 + timedelta(hours=1)
        
        Reservation.objects.create(
            sala=self.room,
            desc_email="teste1@mpgo.mp.br",
            dth_inicio=start_time1,
            dth_fim=end_time1
        )
        
        # Segunda reserva no mesmo horário (overlaping)
        start_time2 = start_time1 + timedelta(minutes=30)
        end_time2 = start_time2 + timedelta(hours=1)
        
        reservation2 = Reservation(
            sala=self.room,
            desc_email="teste2@mpgo.mp.br",
            dth_inicio=start_time2,
            dth_fim=end_time2
        )
        
        with self.assertRaises(ValidationError):
            reservation2.clean()

    def test_valid_reservations(self):
        start_time1 = self.now.replace(hour=8, minute=0, second=0, microsecond=0)
        end_time1 = start_time1 + timedelta(hours=1)
        
        Reservation.objects.create(
            sala=self.room,
            desc_email="teste1@mpgo.mp.br",
            dth_inicio=start_time1,
            dth_fim=end_time1
        )
        
        start_time2 = end_time1
        end_time2 = start_time2 + timedelta(hours=1)
        
        reservation2 = Reservation(
            sala=self.room,
            desc_email="teste2@mpgo.mp.br",
            dth_inicio=start_time2,
            dth_fim=end_time2
        )
        # Não deve levantar erro
        reservation2.clean()
        reservation2.save()
        self.assertEqual(Reservation.objects.count(), 2)

    def test_invalid_time_range(self):
        start_time = self.now
        end_time = start_time - timedelta(hours=1)
        
        reservation = Reservation(
            sala=self.room,
            desc_email="erro@mpgo.mp.br",
            dth_inicio=start_time,
            dth_fim=end_time
        )
        
        with self.assertRaises(ValidationError):
            reservation.clean()

