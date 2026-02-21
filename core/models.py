from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class GameLog(models.Model):
    ESTADO_CHOICES = [
        ('JUGANDO', 'Jugando'),
        ('TERMINADO', 'Terminado'),
        ('ABANDONADO', 'Abandonado'),
        ('PENDIENTE', 'Pendiente (Backlog)'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    game_id = models.IntegerField(verbose_name="ID del Juego (IGDB)")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE', verbose_name="Estado")
    nota = models.IntegerField(null=True, blank=True, verbose_name="Nota (1-5)")
    resena = models.TextField(blank=True, null=True, verbose_name="Reseña")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Modificación")
    
    class Meta:
        verbose_name = "Registro de Juego"
        verbose_name_plural = "Registros de Juegos"
        ordering = ['-fecha_modificacion']
    
    def __str__(self):
        return f"{self.usuario.username} - Juego {self.game_id} ({self.estado})"
