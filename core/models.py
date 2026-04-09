from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Room(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    nm_sala = models.CharField(max_length=150, db_column='nm_sala')
    qtd_capacidade = models.IntegerField(db_column='qtd_capacidade')
    projetor = models.BooleanField(default=False, db_column='projetor')
    tela = models.BooleanField(default=False, db_column='tela')
    obs_sala = models.CharField(max_length=255, blank=True, null=True, db_column='obs_sala')

    class Meta:
        db_table = 'tb_sala'

    def __str__(self):
        return self.nm_sala


class UserProfile(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        db_column='usuario_id',
        related_name='perfil',
    )
    nr_ramal = models.CharField(max_length=20, blank=True, null=True, db_column='nr_ramal')
    nm_setor = models.CharField(max_length=100, blank=True, null=True, db_column='nm_setor')

    class Meta:
        db_table = 'tb_perfil_usuario'

    def __str__(self):
        return f"Perfil de {self.usuario.get_full_name() or self.usuario.username}"


class Reservation(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    sala = models.ForeignKey(Room, on_delete=models.CASCADE, db_column='sala_id')
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='usuario_id',
        related_name='reservas',
    )
    dth_inicio = models.DateTimeField(db_column='dth_inicio')
    dth_fim = models.DateTimeField(db_column='dth_fim')
    obs_reserva = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        db_column='obs_reserva',
    )

    class Meta:
        db_table = 'tb_reserva'

    def clean(self):
        if self.dth_inicio and self.dth_fim:
            if self.dth_inicio >= self.dth_fim:
                raise ValidationError("Data/Hora de fim deve ser posterior à de início.")

            overlapping = Reservation.objects.filter(
                sala_id=self.sala_id,
                dth_inicio__lt=self.dth_fim,
                dth_fim__gt=self.dth_inicio,
            )
            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError("Já existe uma reserva para esta sala neste horário.")

    def __str__(self):
        nome = self.usuario.get_full_name() or self.usuario.email
        return f"{nome} — {self.sala.nm_sala}"
