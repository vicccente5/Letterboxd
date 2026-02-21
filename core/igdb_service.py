import requests
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache

class IGDBService:
    def __init__(self):
        self.client_id = getattr(settings, 'TWITCH_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'TWITCH_CLIENT_SECRET', '')
        self.access_token = None
        self.base_url = 'https://api.igdb.com/v4'
    
    def get_access_token(self):
        """
        Obtiene un token de acceso de la API de Twitch
        El token dura aproximadamente 30 días
        """
        # Intentar obtener desde cache primero
        cached_token = cache.get('igdb_access_token')
        if cached_token:
            return cached_token
        
        url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            token_data = response.json()
            
            access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)  # Default 1 hora
            
            # Guardar en cache por un poco menos del tiempo de expiración
            cache.set('igdb_access_token', access_token, expires_in - 300)
            
            return access_token
            
        except requests.exceptions.RequestException as e:
            print(f"Error obteniendo token de acceso: {e}")
            return None
    
    def make_request(self, endpoint, data):
        """
        Realiza una petición a la API de IGDB
        """
        token = self.get_access_token()
        if not token:
            return None
        
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(f'{self.base_url}/{endpoint}', headers=headers, data=data)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error en petición a IGDB: {e}")
            return None
    
    def search_games(self, query, limit=10):
        """
        Busca juegos por nombre
        """
        search_data = f'''
        search "{query}";
        fields name, cover.url, genres.name, first_release_date, rating, summary;
        limit {limit};
        where cover != null;
        '''
        
        return self.make_request('games', search_data)
    
    def get_game_details(self, game_id):
        """
        Obtiene detalles completos de un juego específico
        """
        details_data = f'''
        fields name, cover.url, genres.name, first_release_date, rating, 
               summary, storyline, platforms.name, involved_companies.company.name,
               involved_companies.developer, involved_companies.publisher,
               screenshots.url, videos.name, videos.video_id;
        where id = {game_id};
        '''
        
        return self.make_request('games', details_data)
    
    def get_popular_games(self, limit=20):
        """
        Obtiene juegos populares (ordenados por rating)
        """
        popular_data = f'''
        fields name, cover.url, genres.name, first_release_date, rating;
        sort rating desc;
        limit {limit};
        where cover != null & rating > 70;
        '''
        
        return self.make_request('games', popular_data)
    
    def get_trending_games(self, limit=20):
        """
        Obtiene juegos en tendencia (más populares actualmente)
        """
        trending_data = f'''
        fields name, cover.url, genres.name, first_release_date, rating, aggregated_rating, total_rating_count;
        sort total_rating_count desc;
        limit {limit};
        where cover != null & total_rating_count > 100;
        '''
        
        return self.make_request('games', trending_data)
    
    def get_recent_games(self, limit=10):
        """
        Obtiene juegos recientes
        """
        recent_data = f'''
        fields name, cover.url, genres.name, first_release_date, rating;
        sort first_release_date desc;
        limit {limit};
        where cover != null & first_release_date > {int((datetime.now() - timedelta(days=90)).timestamp())};
        '''
        
        return self.make_request('games', recent_data)

# Instancia global del servicio
igdb_service = IGDBService()
