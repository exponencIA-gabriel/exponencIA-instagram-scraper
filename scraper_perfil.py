import requests
import json
import time
import random
from typing import List, Dict, Optional
from login import get_instagram_session
from database import InstagramDatabase
from config import SCRAPING_CONFIG, OUTPUT_CONFIG

# ==============================================================================
# INSTAGRAM SCRAPER DE PERFILES - CON POSTS E HIGHLIGHTS
# ==============================================================================

class ScraperPerfil:
    def __init__(self, db_path: str = None, debug_mode: bool = False):
        """
        Inicializa el scraper de perfiles con base de datos
        
        Args:
            db_path (str, optional): Ruta a la base de datos
            debug_mode (bool): Si activar el modo debug
        """
        self.db_path = db_path or OUTPUT_CONFIG['database_file']
        self.db = InstagramDatabase(self.db_path)
        self.debug_mode = debug_mode
        self.session = None
        self.tokens = None
        self.username = None
        
        # Doc IDs hardcodeados (actualizados)
        self.DOC_IDS = {
            'user': '24059491867034637',
            'highlights': '9814547265267853', 
            'posts': '24312092678414792'
        }
    
    def debug_log(self, message: str, data=None):
        """Log de debug si está activado el modo debug"""
        if self.debug_mode:
            timestamp = time.strftime("%H:%M:%S")
            print(f"🔍 [{timestamp}] DEBUG: {message}")
            if data:
                print(f"    Data: {json.dumps(data, indent=2, ensure_ascii=False, default=str)[:300]}...")
    
    def format_number(self, value) -> str:
        """
        Formatea un número de forma legible
        
        Args:
            value: Valor a formatear
            
        Returns:
            str: Número formateado o "N/A" si es None
        """
        if value is None:
            return "N/A"
        if isinstance(value, (int, float)):
            return f"{value:,}"
        return str(value)
    
    def autenticar(self, headless: bool = True) -> bool:
        """
        Realiza la autenticación con Instagram
        
        Args:
            headless (bool): Si ejecutar en modo headless
            
        Returns:
            bool: True si la autenticación fue exitosa
        """
        print("[*] Iniciando proceso de autenticación...")
        session, tokens, username = get_instagram_session(headless=headless)
        
        if not session or not tokens:
            print("[!] No se pudo obtener la sesión autenticada")
            return False
        
        self.session = session
        self.tokens = tokens
        self.username = username
        
        print(f"[+] Autenticado como: {username}")
        return True
    
    def get_user_id_from_username(self, username: str) -> Optional[str]:
        """
        Obtiene el user_id de un username usando requests
        
        Args:
            username (str): Username del usuario
            
        Returns:
            Optional[str]: User ID si se encuentra, None si no
        """
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            user_id = data.get('data', {}).get('user', {}).get('id')
            
            if user_id:
                self.debug_log(f"User ID obtenido para @{username}: {user_id}")
                return user_id
            else:
                print(f"❌ No se pudo encontrar el user_id para '{username}'")
                return None
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"[!] Perfil '{username}' no encontrado (404)")
            elif e.response.status_code == 429:
                print(f"[!] Error HTTP 429 para '{username}' - Rate limit alcanzado. Esperando...")
                time.sleep(60)  # Esperar 1 minuto antes de continuar
            else:
                print(f"[!] Error HTTP {e.response.status_code} para '{username}'")
            return None
        except Exception as e:
            print(f"[!] Error obteniendo ID para '{username}': {e}")
            return None
    
    def make_graphql_request(self, user_id: str, req_type: int, doc_id: str, query_type: str = "user", username: str = None) -> requests.Response:
        """
        Hace una solicitud GraphQL con los parámetros específicos para cada tipo de consulta
        
        Args:
            user_id (str): ID del usuario
            req_type (int): Tipo de request (__req)
            doc_id (str): Document ID
            query_type (str): Tipo de consulta ("user", "highlights", "posts")
            username (str): Username (necesario para posts)
            
        Returns:
            requests.Response: Respuesta de la solicitud
        """
        headers = {
            'accept': '*/*',
            'accept-language': 'es-419,es;q=0.9,es-ES;q=0.8,en;q=0.7,en-GB;q=0.6,en-US;q=0.5',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.instagram.com',
            'priority': 'u=1, i',
            'referer': 'https://www.instagram.com/',
            'sec-ch-prefers-color-scheme': 'dark',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'sec-ch-ua-full-version-list': '"Not)A;Brand";v="8.0.0.0", "Chromium";v="138.0.7204.184", "Microsoft Edge";v="138.0.3351.121"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-model': '"Nexus 5"',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua-platform-version': '"6.0"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36 Edg/138.0.0.0',
            'x-asbd-id': '359341',
            'x-bloks-version-id': '4fd52d0e0985dd463fefe21d18f1609258ecf3c799cc7f12f6c4363b56697384',
            'x-csrftoken': self.tokens['csrf_token'],
            'x-fb-lsd': self.tokens['fb_lsd'],
            'x-ig-app-id': '1217981644879628',
            'x-root-field-name': 'fetch__XDTUserDict'
        }
        
        # Payload base
        payload = {
            'av': '17841476332219581',
            '__d': 'www',
            '__user': '0',
            '__a': '1',
            '__req': str(req_type),
            '__hs': '20302.HYP%3Ainstagram_web_pkg.2.1...0',
            'dpr': '2',
            '__ccg': 'EXCELLENT',
            '__rev': '1025456124',
            '__s': 'azx7hm%3Av651wx%3Ajjbnoc',
            '__hsi': '7534071026151167731',
            '__dyn': '7xeUjG1mxu1syUbFp41twpUnwgU7SbzEdF8aUco2qwJxS0k24o0B-q1ew6ywaq0yE462mcw5Mx62G5UswoEcE7O2l0Fwqo31w9a9wtUd8-U2zxe2GewGw9a361qw8Xxm16wUwtE1wEbUGdwtUd-2u2J0bS1LwTwKG1pg2fwxyo6O1FwlA3a3zhA6bwIxe6V89F8uwm8jxK2K2G0EoKmUhw4UxWawOwgV8',
            '__csr': 'hk4c5sIdiiWeWkp4my9OFliOZZm_GGlbnl8FQW_jqWWXrHZelBAGKQWAUxqjH9mGh9mtyGKcZ2rVtlmVCqfXmWupfAGm8QqUDhEOEnjqVHBGUGcAAx2hpoO4ojS7aDBzqxi5BAhUB5VeV8lyoyAWyQElABzoC4ayu79V8S4Uiw05vaw2bU25o30K1NA80qu584No0zapo1lU3zwwP1uuE0Z-07gVE4e7UKlF2cU1Iodo6Z2UTo1n86dwVg8UJCOwkcw3pc0nCpO08Vk7k0tdw09oK06480aHo',
            '__hsdp': 'gngpiOl4cZSxIajNnhshkxk2p6kKnjmEFEj9bae42bzXy98hzIywDwSzC9xpwCx22t7oTzVFNiwxD9AIU92zoCp3U6wwaob9QEaoe8hz8hwNwTgkefy8fUW0BopwXzUphGXAyopDwda7o10U6d05uwjE2vw2a821xa1eG3K3S1Hw8u0R8W0CE521mg8iw4pwxwLwhjzo6a0Jo562C',
            '__hblp': '1i7Q1YwJK9xN6mmcG12xKU2BCwv8bFFEC69E5a68Dgbbx22qAUSfGm8wGK2h2Ebk4ayohwNAG1rBGES2up3ojxy9wKwLxC5Q1chGBWyo-9DDwgE6i2a7ojwe-10wygiw8S0Lo4W3K18xG0Bo1gE4uu2K1fBBz85-2mu3S1HwVwjo3kzE2qAwiVoS11o8iwdm13wxzo6ix0N0oogwai68dqxq4E',
            '__sjsp': 'gngpiOl4cZSDPMFf5t5N5i5g9ApiVtdqyCxcAIwYg8K4Uyi4o7meoC3-48a9QeU-qskE8pOpbe2ydw3nEdE',
            '__comet_req': '7',
            'fb_dtsg': self.tokens['fb_dtsg'],
            'jazoest': '26195',
            'lsd': self.tokens['fb_lsd'],
            '__spin_r': '1025456124',
            '__spin_b': 'trunk',
            '__spin_t': '1754162606',
            '__crn': 'comet.igweb.PolarisFeedRoute',
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'PolarisProfilePageContentQuery',
            'server_timestamps': 'true',
            'doc_id': doc_id
        }
        
        # Configurar parámetros específicos según el tipo de consulta
        if query_type == "highlights":
            payload['fb_api_req_friendly_name'] = 'PolarisProfileStoryHighlightsTrayContentQuery'
            payload['__crn'] = 'comet.igweb.PolarisProfilePostsTabRoute'
            payload['variables'] = json.dumps({"user_id": user_id})
        elif query_type == "posts":
            payload['fb_api_req_friendly_name'] = 'PolarisProfilePostsQuery'
            payload['__crn'] = 'comet.igweb.PolarisProfilePostsTabRoute'
            payload['variables'] = json.dumps({
                "data": {
                    "count": 12,
                    "include_reel_media_seen_timestamp": True,
                    "include_relationship_info": True,
                    "latest_besties_reel_media": True,
                    "latest_reel_media": True
                },
                "username": username,
                "__relay_internal__pv__PolarisIsLoggedInrelayprovider": True,
                "__relay_internal__pv__PolarisShareSheetV3relayprovider": True
            })
        else:  # user
            payload['variables'] = json.dumps({
                "id": user_id,
                "render_surface": "PROFILE"
            })
        
        self.debug_log(f"GraphQL request para {query_type}", {
            'user_id': user_id,
            'doc_id': doc_id,
            'req_type': req_type
        })
        
        response = self.session.post("https://www.instagram.com/graphql/query", 
                                   headers=headers, data=payload)
        
        # Manejar rate limiting
        if response.status_code == 429:
            print(f"[!] Rate limit alcanzado en GraphQL request para {query_type}. Esperando 60s...")
            time.sleep(60)
            # Reintentar una vez
            response = self.session.post("https://www.instagram.com/graphql/query", 
                                       headers=headers, data=payload)
        
        return response
    
    def extract_user_data(self, data: dict) -> dict:
        """Extrae datos de usuario de la respuesta"""
        user_data = data['data']['user']
        return {
            'is_private': user_data.get('is_private'),
            'username': user_data.get('username'),
            'full_name': user_data.get('full_name'),  # Agregado full_name
            'biography': user_data.get('biography'),
            'pk': user_data.get('pk'),
            'profile_pic_url': user_data.get('profile_pic_url'),
            'hd_profile_pic_url_info': user_data.get('hd_profile_pic_url_info', {}).get('url'),
            'account_type': user_data.get('account_type'),
            'follower_count': user_data.get('follower_count'),
            'is_business': user_data.get('is_business'),
            'category': user_data.get('category'),
            'external_lynx_url': user_data.get('external_lynx_url'),
            'external_url': user_data.get('external_url'),
            'following_count': user_data.get('following_count'),
            'media_count': user_data.get('media_count')
        }
    
    def extract_posts_data(self, data: dict) -> list:
        """Extrae datos de posts de la respuesta"""
        posts_list = []
        if data and 'data' in data and data['data']:
            if 'xdt_api__v1__feed__user_timeline_graphql_connection' in data['data']:
                post_edges = data['data'].get('xdt_api__v1__feed__user_timeline_graphql_connection', {}).get('edges', [])
                for edge in post_edges:
                    node = edge.get('node', {})
                    if node:
                        post_data = {
                            'shortcode': node.get('code'),
                            'thumbnail_url': node.get('image_versions2', {}).get('candidates', [{}])[0].get('url'),
                            'is_video': node.get('media_type') == 2,
                            'like_count': node.get('like_count'),
                            'comment_count': node.get('comment_count')
                        }
                        posts_list.append(post_data)
        return posts_list
    
    def extract_highlights_data(self, data: dict) -> list:
        """Extrae datos de highlights de la respuesta"""
        highlights_list = []
        if data and 'data' in data and data['data']:
            if 'highlights' in data['data']:
                highlight_edges = data['data'].get('highlights', {}).get('edges', [])
                for edge in highlight_edges:
                    node = edge.get('node', {})
                    if node:
                        highlight_data = {
                            'id': node.get('id'),
                            'title': node.get('title'),
                            'thumbnail_url': node.get('cover_media', {}).get('cropped_image_version', {}).get('url')
                        }
                        highlights_list.append(highlight_data)
        return highlights_list
    
    def scrape_user_complete(self, username: str) -> Dict:
        """
        Scrapea un usuario completo (datos básicos, posts e highlights)
        
        Args:
            username (str): Username del usuario a scrapear
            
        Returns:
            Dict: Datos completos del usuario
        """
        print(f"\n[*] Scrapeando usuario completo: @{username}")
        
        # 1. Obtener user_id
        user_id = self.get_user_id_from_username(username)
        if not user_id:
            return {'username': username, 'error': 'User ID not found'}
        
        extracted_data = {'username': username}
        
        # 2. Obtener datos de usuario (__req = 3)
        print("[*] Obteniendo datos de usuario...")
        try:
            response_user = self.make_graphql_request(user_id, 3, self.DOC_IDS['user'], "user")
            if response_user.status_code == 429:
                print(f"[!] Rate limit alcanzado para '{username}'. Saltando usuario.")
                return {'username': username, 'error': 'Rate limit (429)'}
            elif response_user.status_code == 200:
                data_user = response_user.json()
                if 'errors' not in data_user and 'data' in data_user and data_user['data']['user']:
                    user_info = self.extract_user_data(data_user)
                    extracted_data.update(user_info)
                    
                    # Mostrar información detallada del usuario
                    print("✓ Datos de usuario obtenidos:")
                    print(f"   👤 Username: @{user_info.get('username', 'N/A')}")
                    print(f"   👤 Nombre completo: {user_info.get('full_name', 'N/A')}")
                    print(f"   📝 Biografía: {(user_info.get('biography') or 'Sin biografía')[:50]}{'...' if len(user_info.get('biography', '')) > 50 else ''}")
                    print(f"   👥 Seguidores: {self.format_number(user_info.get('follower_count'))}")
                    print(f"   👤 Siguiendo: {self.format_number(user_info.get('following_count'))}")
                    print(f"   📸 Posts: {self.format_number(user_info.get('media_count'))}")
                    print(f"   🔒 Privado: {'Sí' if user_info.get('is_private') else 'No'}")
                    print(f"   🏢 Negocio: {'Sí' if user_info.get('is_business') else 'No'}")
                    if user_info.get('category'):
                        print(f"   📂 Categoría: {user_info.get('category')}")
                    if user_info.get('external_url'):
                        print(f"   🔗 Link externo: {user_info.get('external_url')}")
                else:
                    print("✗ Error en respuesta de datos de usuario")
                    extracted_data['error'] = 'User data response error'
            else:
                print(f"✗ Error HTTP obteniendo datos de usuario: {response_user.status_code}")
                extracted_data['error'] = f'HTTP {response_user.status_code}'
        except Exception as e:
            print(f"✗ Error parseando datos de usuario: {e}")
            extracted_data['error'] = str(e)
        
        # 3. Obtener highlights (__req = 5)
        print("[*] Obteniendo highlights...")
        try:
            response_highlights = self.make_graphql_request(user_id, 5, self.DOC_IDS['highlights'], "highlights")
            if response_highlights.status_code == 429:
                print(f"[!] Rate limit en highlights para '{username}'. Saltando highlights.")
                extracted_data['highlights'] = []
            elif response_highlights.status_code == 200:
                data_highlights = response_highlights.json()
                if 'errors' not in data_highlights:
                    highlights = self.extract_highlights_data(data_highlights)
                    extracted_data['highlights'] = highlights
                    print(f"✓ {len(highlights)} highlights obtenidos")
                    if highlights:
                        print("   📚 Highlights encontrados:")
                        for i, highlight in enumerate(highlights[:5], 1):  # Mostrar solo los primeros 5
                            title = highlight.get('title', 'Sin título')
                            print(f"      {i}. {title}")
                        if len(highlights) > 5:
                            print(f"      ... y {len(highlights) - 5} más")
                else:
                    print("✗ Error en respuesta de highlights")
                    extracted_data['highlights'] = []
            else:
                print(f"✗ Error HTTP obteniendo highlights: {response_highlights.status_code}")
                extracted_data['highlights'] = []
        except Exception as e:
            print(f"✗ Error parseando highlights: {e}")
            extracted_data['highlights'] = []
        
        # 4. Obtener posts (__req = 7)
        if 'username' in extracted_data and not extracted_data.get('error'):
            print("[*] Obteniendo posts...")
            try:
                response_posts = self.make_graphql_request(user_id, 7, self.DOC_IDS['posts'], "posts", username)
                if response_posts.status_code == 429:
                    print(f"[!] Rate limit en posts para '{username}'. Saltando posts.")
                    extracted_data['posts'] = []
                elif response_posts.status_code == 200:
                    data_posts = response_posts.json()
                    if 'errors' not in data_posts:
                        posts = self.extract_posts_data(data_posts)
                        extracted_data['posts'] = posts
                        print(f"✓ {len(posts)} posts obtenidos")
                        if posts:
                            # Calcular estadísticas de posts
                            total_likes = sum(post.get('like_count', 0) for post in posts if post.get('like_count'))
                            total_comments = sum(post.get('comment_count', 0) for post in posts if post.get('comment_count'))
                            videos = sum(1 for post in posts if post.get('is_video'))
                            photos = len(posts) - videos
                            
                            print("   📊 Estadísticas de posts:")
                            print(f"      📸 Fotos: {photos} | 🎥 Videos: {videos}")
                            print(f"      ❤️ Total likes: {self.format_number(total_likes)}")
                            print(f"      💬 Total comentarios: {self.format_number(total_comments)}")
                            if posts:
                                avg_likes = total_likes / len(posts) if total_likes > 0 else 0
                                print(f"      📈 Promedio likes: {self.format_number(int(avg_likes))}")
                    else:
                        print("✗ Error en respuesta de posts")
                        extracted_data['posts'] = []
                else:
                    print(f"✗ Error HTTP obteniendo posts: {response_posts.status_code}")
                    extracted_data['posts'] = []
            except Exception as e:
                print(f"✗ Error parseando posts: {e}")
                extracted_data['posts'] = []
        else:
            print("✗ No se pudo obtener username, saltando consulta de posts")
            extracted_data['posts'] = []
        
        # Mostrar resumen final
        if not extracted_data.get('error'):
            print(f"\n📋 RESUMEN COMPLETO - @{username}")
            print("="*50)
            print(f"👥 Seguidores: {self.format_number(extracted_data.get('follower_count'))}")
            print(f"👤 Siguiendo: {self.format_number(extracted_data.get('following_count'))}")
            print(f"📸 Posts totales: {self.format_number(extracted_data.get('media_count'))}")
            print(f"📸 Posts extraídos: {len(extracted_data.get('posts', []))}")
            print(f"📚 Highlights: {len(extracted_data.get('highlights', []))}")
            print(f"🔒 Perfil privado: {'Sí' if extracted_data.get('is_private') else 'No'}")
            if extracted_data.get('category'):
                print(f"📂 Categoría: {extracted_data.get('category')}")
        
        return extracted_data
    
    def save_user_to_database(self, user_data: Dict) -> bool:
        """
        Guarda los datos del usuario en la base de datos
        
        Args:
            user_data (Dict): Datos del usuario
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            username = user_data.get('username')
            if not username:
                print("❌ No se puede guardar: falta username")
                return False
            
            # Adaptar datos para que coincidan con lo que espera insertar_usuario
            adapted_user_data = user_data.copy()
            
            # Asegurar que full_name existe, usar username como fallback si está vacío
            if not adapted_user_data.get('full_name'):
                adapted_user_data['full_name'] = username
            
            # Asegurar que is_business existe
            if 'is_business' not in adapted_user_data:
                adapted_user_data['is_business'] = adapted_user_data.get('account_type') == 3
            
            # Guardar usuario
            self.db.insertar_usuario(adapted_user_data)
            
            # Guardar media URLs (posts e highlights)
            self.db.insertar_media_urls(username, adapted_user_data)
            
            # Obtener conteos para el mensaje
            posts_count = len(user_data.get('posts', []))
            highlights_count = len(user_data.get('highlights', []))
            
            print(f"✅ Usuario @{username} guardado en BD ({posts_count} posts, {highlights_count} highlights)")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando usuario en BD: {e}")
            return False
    
    def scrape_pending_users(self) -> None:
        """Scrapea todos los usuarios pendientes en la base de datos"""
        print("\n" + "="*60)
        print("🚀 SCRAPER DE PERFILES - USUARIOS PENDIENTES")
        print("="*60)
        
        # Obtener usuarios pendientes
        pending_usernames = self.db.obtener_usuarios_para_scrapear(force_rescrape=SCRAPING_CONFIG['force_rescrape'])
        
        if not pending_usernames:
            print("✅ No hay usuarios pendientes para scrapear")
            return
        
        print(f"📋 Usuarios pendientes: {len(pending_usernames)}")
        for username in pending_usernames:
            print(f"   - @{username}")
        
        # Autenticar
        if not self.autenticar(headless=SCRAPING_CONFIG['headless']):
            print("❌ Error en autenticación. Abortando.")
            return
        
        # Scrapear cada usuario
        successful = 0
        failed = 0
        
        for i, username in enumerate(pending_usernames, 1):
            print(f"\n[{i}/{len(pending_usernames)}] Scrapeando @{username}...")
            
            try:
                # Scrapear usuario completo
                user_data = self.scrape_user_complete(username)
                
                # Si hay error de rate limit, aumentar el delay
                if user_data.get('error') == 'Rate limit (429)':
                    print(f"⏳ Rate limit detectado. Esperando 120s adicionales...")
                    time.sleep(120)  # Esperar 2 minutos adicionales
                    failed += 1
                elif self.save_user_to_database(user_data):
                    successful += 1
                else:
                    failed += 1
                
                # Delay entre usuarios
                if i < len(pending_usernames):
                    delay = random.uniform(SCRAPING_CONFIG['delay_min'], SCRAPING_CONFIG['delay_max'])
                    print(f"⏳ Esperando {delay:.1f}s antes del siguiente usuario...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"❌ Error scrapeando @{username}: {e}")
                failed += 1
        
        # Resumen final
        print(f"\n" + "="*60)
        print("📊 RESUMEN FINAL")
        print("="*60)
        print(f"✅ Exitosos: {successful}")
        print(f"❌ Fallidos: {failed}")
        print(f"📁 Base de datos: {self.db_path}")
        
        if OUTPUT_CONFIG['save_csv']:
            self.db.exportar_a_csv()
            print(f"📄 CSV exportado: {OUTPUT_CONFIG['csv_file']}")
    
    def add_users_to_database(self, usernames: List[str]) -> None:
        """
        Agrega usuarios a la base de datos
        
        Args:
            usernames (List[str]): Lista de usernames a agregar
        """
        print(f"\n[*] Agregando {len(usernames)} usuarios a la base de datos...")
        
        added = 0
        existing = 0
        
        for username in usernames:
            username = username.strip()
            if not username:
                continue
                
            if self.db.verificar_usuario_completo(username):
                print(f"   ⚠️ @{username} ya existe en BD")
                existing += 1
            else:
                # Agregar usuario inicial (solo username)
                self.db.agregar_usuarios_iniciales([username])
                print(f"   ✅ @{username} agregado")
                added += 1
        
        print(f"\n📊 Resumen:")
        print(f"   ✅ Agregados: {added}")
        print(f"   ⚠️ Ya existían: {existing}")
        print(f"   📁 Base de datos: {self.db_path}")

def main():
    """Función principal con menú interactivo"""
    # Inicializar base de datos con perfiles famosos si está vacía
    from database import inicializar_con_perfiles_famosos
    inicializar_con_perfiles_famosos()
    
    scraper = ScraperPerfil(debug_mode=False)
    
    while True:
        print("\n" + "="*60)
        print("🚀 SCRAPER DE PERFILES - MENÚ PRINCIPAL")
        print("="*60)
        print("1. 📥 Scrapear usuarios pendientes")
        print("2. ➕ Agregar usuarios a BD")
        print("3. 📊 Ver estadísticas de BD")
        print("4. 🔍 Scrapear usuario específico")
        print("5. ❌ Salir")
        print("="*60)
        
        try:
            opcion = input("Selecciona una opción (1-5): ").strip()
            
            if opcion == "1":
                scraper.scrape_pending_users()
                
            elif opcion == "2":
                usernames_input = input("\nIngresa usernames separados por comas: ").strip()
                if usernames_input:
                    usernames = [u.strip() for u in usernames_input.split(',')]
                    scraper.add_users_to_database(usernames)
                else:
                    print("❌ No se ingresaron usernames")
                    
            elif opcion == "3":
                stats = scraper.db.obtener_estadisticas()
                print(f"\n📊 ESTADÍSTICAS DE BASE DE DATOS")
                print(f"="*40)
                print(f"👥 Total usuarios: {stats['total_usuarios']}")
                print(f"✅ Activos: {stats['usuarios_activos']}")
                print(f"❌ Inactivos: {stats['usuarios_inactivos']}")
                print(f"🔒 Privados: {stats['usuarios_privados']}")
                print(f"🏢 Negocios: {stats['usuarios_negocio']}")
                print(f"🖼️ Total media URLs: {stats['total_media']}")
                print(f"📁 Archivo BD: {scraper.db_path}")
                
            elif opcion == "4":
                username = input("\nIngresa el username a scrapear: ").strip()
                if username:
                    if not scraper.session:
                        if not scraper.autenticar(headless=SCRAPING_CONFIG['headless']):
                            print("❌ Error en autenticación")
                            continue
                    
                    user_data = scraper.scrape_user_complete(username)
                    print(f"\n📋 DATOS EXTRAÍDOS:")
                    print("="*40)
                    print(json.dumps(user_data, indent=2, ensure_ascii=False))
                    
                    save = input("\n¿Guardar en BD? (s/n): ").strip().lower()
                    if save == 's':
                        scraper.save_user_to_database(user_data)
                else:
                    print("❌ No se ingresó username")
                    
            elif opcion == "5":
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción inválida. Selecciona 1-5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrumpido por el usuario. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()