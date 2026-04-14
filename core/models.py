from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Room(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    nm_sala = models.CharField(max_length=150, db_column='nm_sala', verbose_name='Nome da Sala')
    qtd_capacidade = models.IntegerField(db_column='qtd_capacidade', verbose_name='Capacidade (Qtd)')
    projetor = models.BooleanField(default=False, db_column='projetor', verbose_name='Possui Projetor')
    tela = models.BooleanField(default=False, db_column='tela', verbose_name='Possui Tela')
    obs_sala = models.CharField(max_length=255, blank=True, null=True, db_column='obs_sala', verbose_name='Observações da Sala')

    nm_predio = models.CharField(max_length=150, blank=True, null=True, db_column='nm_predio', verbose_name='Nome do Prédio')
    end_sala = models.CharField(max_length=255, blank=True, null=True, db_column='end_sala', verbose_name='Endereço Completo')
    nr_andar = models.CharField(max_length=50, blank=True, null=True, db_column='nr_andar', verbose_name='Número do Andar')
    cdg_sala = models.CharField(max_length=50, blank=True, null=True, db_column='cdg_sala', verbose_name='Identificação (Código)')

    quadro_branco = models.BooleanField(default=False, db_column='quadro_branco', verbose_name='Possui Quadro Branco')
    videoconferencia = models.BooleanField(default=False, db_column='videoconferencia', verbose_name='Possui Videoconferência')
    acessibilidade = models.BooleanField(default=False, db_column='acessibilidade', verbose_name='Possui Acessibilidade')

    exige_aprovacao = models.BooleanField(default=False, db_column='exige_aprovacao', verbose_name='Exige Aprovação')
    aprovador = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='salas_aprovacao',
        db_column='aprovador_id',
        verbose_name='Aprovador Responsável'
    )

    class Meta:
        db_table = 'tb_sala'

    def clean(self):
        if self.exige_aprovacao and not self.aprovador:
            raise ValidationError("Uma sala que exige aprovação precisa ter um Aprovador designado.")

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
    
    STATUS_CHOICES = (
        ('P', 'Pendente'),
        ('A', 'Aprovada'),
        ('R', 'Recusada'),
    )
    tp_status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A', db_column='tp_status')

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
                tp_status='A',
            )
            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError("Já existe uma reserva aprovada para esta sala neste horário.")

    def save(self, *args, **kwargs):
        if not self.pk and self.sala and self.sala.exige_aprovacao:
            self.tp_status = 'P'
        super().save(*args, **kwargs)

    def __str__(self):
        nome = self.usuario.get_full_name() or self.usuario.email
        return f"[{self.get_tp_status_display()}] {nome} — {self.sala.nm_sala}"


class Notification(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, db_column='usuario_id', related_name='notificacoes')
    mensagem = models.CharField(max_length=255, db_column='mensagem')
    lido = models.BooleanField(default=False, db_column='lido')
    dth_criacao = models.DateTimeField(auto_now_add=True, db_column='dth_criacao')

    class Meta:
        db_table = 'tb_notificacao'
