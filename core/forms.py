from django import forms
from .models import GameLog

class GameLogForm(forms.ModelForm):
    class Meta:
        model = GameLog
        fields = ['estado', 'nota', 'resena']
        widgets = {
            'estado': forms.Select(attrs={
                'class': 'form-control',
                'style': 'width: 100%; padding: 0.75rem; border-radius: 8px; border: 1px solid #444; background: #333; color: #fff;'
            }),
            'nota': forms.Select(attrs={
                'class': 'form-control',
                'style': 'width: 100%; padding: 0.75rem; border-radius: 8px; border: 1px solid #444; background: #333; color: #fff;'
            }),
            'resena': forms.Textarea(attrs={
                'class': 'form-control',
                'style': 'width: 100%; padding: 0.75rem; border-radius: 8px; border: 1px solid #444; background: #333; color: #fff; min-height: 100px; resize: vertical;',
                'placeholder': '¿Qué te pareció el juego?'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nota'].choices = [('', 'Sin nota')] + [(i, f'{"⭐" * i}') for i in range(1, 6)]
        self.fields['estado'].label = 'Estado del juego'
        self.fields['nota'].label = 'Nota (1-5 estrellas)'
        self.fields['resena'].label = 'Reseña (opcional)'
