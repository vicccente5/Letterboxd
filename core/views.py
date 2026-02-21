from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import GameLog
from .igdb_service import igdb_service
from .forms import GameLogForm

# Create your views here.

def home(request):
    """
    Pantalla principal con buscador, tendencias y actividad reciente
    """
    # Obtener juegos en tendencia de IGDB (más vistos/discutidos)
    trending_games = igdb_service.get_trending_games(limit=8)
    
    # Obtener actividad reciente de usuarios
    recent_activity = GameLog.objects.select_related('usuario').order_by('-fecha_modificacion')[:6]
    
    context = {
        'title': 'Backlog Gamer - Tu Biblioteca de Juegos',
        'trending_games': trending_games,
        'recent_activity': recent_activity
    }
    return render(request, 'core/home.html', context)

def game_detail(request, game_id):
    """
    Ficha del juego con información de la API y reseñas de usuarios
    """
    # Obtener detalles del juego desde IGDB
    game_details = igdb_service.get_game_details(game_id)
    
    # Obtener reseñas de usuarios para este juego
    game_reviews = GameLog.objects.filter(game_id=game_id).select_related('usuario').order_by('-fecha_modificacion')
    
    context = {
        'title': f'Detalles del Juego {game_id}',
        'game_id': game_id,
        'game_details': game_details,
        'game_reviews': game_reviews
    }
    return render(request, 'core/game_detail.html', context)

@login_required
def profile(request):
    """
    Perfil del usuario con su backlog personal
    """
    # Obtener todos los registros del usuario
    juegos_usuario = GameLog.objects.filter(usuario=request.user)
    
    # Obtener detalles de los juegos desde IGDB
    games_details = {}
    game_ids = list(juegos_usuario.values_list('game_id', flat=True))
    
    if game_ids:
        for game_id in game_ids:
            details = igdb_service.get_game_details(game_id)
            if details and len(details) > 0:
                games_details[game_id] = details[0]
    
    # Estadísticas
    stats = {
        'terminados': juegos_usuario.filter(estado='TERMINADO').count(),
        'jugando': juegos_usuario.filter(estado='JUGANDO').count(),
        'abandonados': juegos_usuario.filter(estado='ABANDONADO').count(),
        'pendientes': juegos_usuario.filter(estado='PENDIENTE').count(),
        'total': juegos_usuario.count()
    }
    
    context = {
        'title': f'Mi Backlog - {request.user.username}',
        'stats': stats,
        'juegos_usuario': juegos_usuario,
        'games_details': games_details
    }
    return render(request, 'core/profile.html', context)

@login_required
def profile_terminados(request):
    """Página de juegos terminados"""
    juegos_terminados = GameLog.objects.filter(usuario=request.user, estado='TERMINADO')
    
    # Obtener detalles de IGDB y crear lista de tuplas (juego, detalles)
    juegos_con_detalles = []
    for juego in juegos_terminados:
        details = igdb_service.get_game_details(juego.game_id)
        game_detail = details[0] if details and len(details) > 0 else None
        juegos_con_detalles.append((juego, game_detail))
    
    return render(request, 'core/profile_terminados.html', {
        'title': f'Juegos Terminados - {request.user.username}',
        'juegos_con_detalles': juegos_con_detalles
    })

@login_required
def profile_jugando(request):
    """Página de juegos en juego"""
    juegos_jugando = GameLog.objects.filter(usuario=request.user, estado='JUGANDO')
    
    # Obtener detalles de IGDB
    juegos_con_detalles = []
    for juego in juegos_jugando:
        details = igdb_service.get_game_details(juego.game_id)
        game_detail = details[0] if details and len(details) > 0 else None
        juegos_con_detalles.append((juego, game_detail))
    
    return render(request, 'core/profile_jugando.html', {
        'title': f'Jugando Actualmente - {request.user.username}',
        'juegos_con_detalles': juegos_con_detalles
    })

@login_required
def profile_abandonados(request):
    """Página de juegos abandonados"""
    juegos_abandonados = GameLog.objects.filter(usuario=request.user, estado='ABANDONADO')
    
    # Obtener detalles de IGDB
    juegos_con_detalles = []
    for juego in juegos_abandonados:
        details = igdb_service.get_game_details(juego.game_id)
        game_detail = details[0] if details and len(details) > 0 else None
        juegos_con_detalles.append((juego, game_detail))
    
    return render(request, 'core/profile_abandonados.html', {
        'title': f'Juegos Abandonados - {request.user.username}',
        'juegos_con_detalles': juegos_con_detalles
    })

@login_required
def profile_pendientes(request):
    """Página de juegos pendientes"""
    juegos_pendientes = GameLog.objects.filter(usuario=request.user, estado='PENDIENTE')
    
    # Obtener detalles de IGDB
    juegos_con_detalles = []
    for juego in juegos_pendientes:
        details = igdb_service.get_game_details(juego.game_id)
        game_detail = details[0] if details and len(details) > 0 else None
        juegos_con_detalles.append((juego, game_detail))
    
    return render(request, 'core/profile_pendientes.html', {
        'title': f'Mi Backlog - {request.user.username}',
        'juegos_con_detalles': juegos_con_detalles
    })

def search_games(request):
    """
    Vista AJAX para buscar juegos
    """
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'error': 'No se proporcionó término de búsqueda'}, status=400)
    
    # Buscar juegos en IGDB
    games = igdb_service.search_games(query, limit=20)
    
    return JsonResponse({'games': games})

@login_required
def add_game_to_backlog(request, game_id):
    """
    Agrega un juego al backlog del usuario
    """
    if request.method == 'POST':
        # Verificar si el juego ya está en el backlog del usuario
        existing_game = GameLog.objects.filter(usuario=request.user, game_id=game_id).first()
        
        if existing_game:
            messages.warning(request, 'Este juego ya está en tu backlog.')
            return redirect('game_detail', game_id=game_id)
        
        form = GameLogForm(request.POST)
        if form.is_valid():
            game_log = form.save(commit=False)
            game_log.usuario = request.user
            game_log.game_id = game_id
            game_log.save()
            
            messages.success(request, '¡Juego agregado a tu backlog exitosamente!')
            return redirect('game_detail', game_id=game_id)
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    
    # Si es GET o hay errores, redirigir a la página de detalles del juego
    return redirect('game_detail', game_id=game_id)
