import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# ==============================================================================
# MÓDULO DE BASE DE DATOS PARA INSTAGRAM SCRAPER
# ==============================================================================

class InstagramDatabase:
    def __init__(self, db_path: str = "instagram_data.db"):
        """
        Inicializa la conexión a la base de datos SQLite
        
        Args:
            db_path (str): Ruta al archivo de base de datos
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Crea las tablas si no existen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla de usuarios únicos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios_unicos (
                    username TEXT PRIMARY KEY,
                    perfil_inactivo BOOLEAN DEFAULT FALSE,
                    nombre_persona TEXT,
                    categoria TEXT,
                    perfil_privado BOOLEAN DEFAULT FALSE,
                    cantidad_publicaciones INTEGER,
                    cantidad_destacadas INTEGER,
                    cantidad_seguidores INTEGER,
                    cantidad_seguidos INTEGER,
                    biografia TEXT,
                    links_externos TEXT,
                    fecha_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de URLs de media
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS media_urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    url_media TEXT,
                    tipo_media TEXT CHECK(tipo_media IN ('post', 'destacada')),
                    subtipo_post TEXT CHECK(subtipo_post IN ('foto', 'reel', 'video') OR subtipo_post IS NULL),
                    cantidad_likes INTEGER DEFAULT 0,
                    cantidad_comentarios INTEGER DEFAULT 0,
                    fecha_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES usuarios_unicos (username)
                )
            ''')
            
            # Índices para mejorar rendimiento
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_media_username ON media_urls(username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_media_tipo ON media_urls(tipo_media)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_fecha ON usuarios_unicos(fecha_scraping)')
            
            conn.commit()
            print(f"[+] Base de datos inicializada: {self.db_path}")
    
    def insertar_usuario(self, user_data: Dict) -> bool:
        """
        Inserta o actualiza un usuario en la base de datos
        
        Args:
            user_data (Dict): Datos del usuario extraídos del scraping
            
        Returns:
            bool: True si se insertó/actualizó correctamente
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Determinar si el perfil está inactivo
                perfil_inactivo = user_data.get('error') is not None
                
                # Preparar datos para inserción
                username = user_data.get('username')
                nombre_persona = user_data.get('full_name')
                categoria = user_data.get('category') if user_data.get('is_business') else None
                perfil_privado = user_data.get('is_private', False)
                cantidad_publicaciones = user_data.get('media_count', 0)
                cantidad_destacadas = len(user_data.get('highlights', []))
                cantidad_seguidores = user_data.get('follower_count', 0)
                cantidad_seguidos = user_data.get('following_count', 0)
                biografia = user_data.get('biography')
                links_externos = user_data.get('external_url')
                
                # INSERT OR REPLACE para actualizar si ya existe
                cursor.execute('''
                    INSERT OR REPLACE INTO usuarios_unicos (
                        username, perfil_inactivo, nombre_persona, categoria,
                        perfil_privado, cantidad_publicaciones, cantidad_destacadas,
                        cantidad_seguidores, cantidad_seguidos, biografia, links_externos,
                        ultima_actualizacion
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    username, perfil_inactivo, nombre_persona, categoria,
                    perfil_privado, cantidad_publicaciones, cantidad_destacadas,
                    cantidad_seguidores, cantidad_seguidos, biografia, links_externos
                ))
                
                conn.commit()
                print(f"[+] Usuario '{username}' guardado en BD")
                return True
                
        except Exception as e:
            print(f"[!] Error insertando usuario {user_data.get('username', 'N/A')}: {e}")
            return False
    
    def insertar_media_urls(self, username: str, user_data: Dict) -> bool:
        """
        Inserta las URLs de media (posts y destacadas) de un usuario
        
        Args:
            username (str): Username del usuario
            user_data (Dict): Datos del usuario con posts y highlights
            
        Returns:
            bool: True si se insertaron correctamente
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Limpiar media URLs anteriores del usuario
                cursor.execute('DELETE FROM media_urls WHERE username = ?', (username,))
                
                # Insertar posts
                posts = user_data.get('posts', [])
                for post in posts:
                    thumbnail_url = post.get('thumbnail_url')
                    if thumbnail_url:
                        # Determinar subtipo (foto/reel/video)
                        subtipo = 'reel' if post.get('is_video') else 'foto'
                        
                        cursor.execute('''
                            INSERT INTO media_urls (
                                username, url_media, tipo_media, subtipo_post,
                                cantidad_likes, cantidad_comentarios
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            username, thumbnail_url, 'post', subtipo,
                            post.get('like_count', 0), post.get('comment_count', 0)
                        ))
                
                # Insertar destacadas
                highlights = user_data.get('highlights', [])
                for highlight in highlights:
                    thumbnail_url = highlight.get('thumbnail_url')
                    if thumbnail_url:
                        cursor.execute('''
                            INSERT INTO media_urls (
                                username, url_media, tipo_media, subtipo_post,
                                cantidad_likes, cantidad_comentarios
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            username, thumbnail_url, 'destacada', None, 0, 0
                        ))
                
                conn.commit()
                print(f"[+] Media URLs de '{username}' guardadas: {len(posts)} posts, {len(highlights)} destacadas")
                return True
                
        except Exception as e:
            print(f"[!] Error insertando media URLs para {username}: {e}")
            return False
    
    def obtener_usuarios_para_scrapear(self, force_rescrape: bool = False, limite: Optional[int] = None) -> List[str]:
        """
        Obtiene lista de usernames desde la base de datos para scrapear
        
        Args:
            force_rescrape (bool): Si True, incluye usuarios ya scrapeados
            limite (int, optional): Límite de usuarios a obtener
            
        Returns:
            List[str]: Lista de usernames
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if force_rescrape:
                    # Obtener todos los usuarios, priorizando los menos actualizados
                    query = 'SELECT username FROM usuarios_unicos ORDER BY ultima_actualizacion ASC'
                else:
                    # Solo usuarios que NO están completamente scrapeados
                    # Un usuario está completo si tiene seguidores, seguidos y publicaciones != NULL
                    query = '''
                        SELECT username FROM usuarios_unicos 
                        WHERE cantidad_seguidores IS NULL 
                           OR cantidad_seguidos IS NULL 
                           OR cantidad_publicaciones IS NULL
                           OR perfil_inactivo = TRUE
                        ORDER BY ultima_actualizacion ASC
                    '''
                
                if limite:
                    query += f' LIMIT {limite}'
                
                cursor.execute(query)
                usernames = [row[0] for row in cursor.fetchall()]
                
                if force_rescrape:
                    print(f"[+] Obtenidos {len(usernames)} usuarios de la BD (incluyendo ya scrapeados)")
                else:
                    print(f"[+] Obtenidos {len(usernames)} usuarios pendientes de scrapear")
                
                return usernames
                
        except Exception as e:
            print(f"[!] Error obteniendo usuarios: {e}")
            return []
    
    def verificar_usuario_completo(self, username: str) -> bool:
        """
        Verifica si un usuario ya está completamente scrapeado
        
        Args:
            username (str): Username a verificar
            
        Returns:
            bool: True si el usuario está completo, False si necesita scraping
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT cantidad_seguidores, cantidad_seguidos, cantidad_publicaciones, perfil_inactivo
                    FROM usuarios_unicos 
                    WHERE username = ?
                ''', (username,))
                
                result = cursor.fetchone()
                
                if not result:
                    # Usuario no existe, necesita scraping
                    return False
                
                seguidores, seguidos, publicaciones, inactivo = result
                
                # Si es perfil inactivo, se considera incompleto (para reintentar)
                if inactivo:
                    return False
                
                # Usuario completo si tiene todos los campos principales
                completo = (seguidores is not None and 
                           seguidos is not None and 
                           publicaciones is not None)
                
                return completo
                
        except Exception as e:
            print(f"[!] Error verificando usuario {username}: {e}")
            return False
    
    def obtener_estadisticas_scraping(self) -> Dict:
        """
        Obtiene estadísticas específicas del progreso de scraping
        
        Returns:
            Dict: Estadísticas de progreso
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de usuarios
                cursor.execute('SELECT COUNT(*) FROM usuarios_unicos')
                total_usuarios = cursor.fetchone()[0]
                
                # Usuarios completos (con datos principales)
                cursor.execute('''
                    SELECT COUNT(*) FROM usuarios_unicos 
                    WHERE cantidad_seguidores IS NOT NULL 
                      AND cantidad_seguidos IS NOT NULL 
                      AND cantidad_publicaciones IS NOT NULL
                      AND perfil_inactivo = FALSE
                ''')
                usuarios_completos = cursor.fetchone()[0]
                
                # Usuarios pendientes
                usuarios_pendientes = total_usuarios - usuarios_completos
                
                # Usuarios inactivos/con error
                cursor.execute('SELECT COUNT(*) FROM usuarios_unicos WHERE perfil_inactivo = TRUE')
                usuarios_inactivos = cursor.fetchone()[0]
                
                # Progreso porcentual
                progreso = (usuarios_completos / total_usuarios * 100) if total_usuarios > 0 else 0
                
                return {
                    'total_usuarios': total_usuarios,
                    'usuarios_completos': usuarios_completos,
                    'usuarios_pendientes': usuarios_pendientes,
                    'usuarios_inactivos': usuarios_inactivos,
                    'progreso_porcentaje': round(progreso, 2)
                }
                
        except Exception as e:
            print(f"[!] Error obteniendo estadísticas de scraping: {e}")
            return {}
    
    def agregar_usuarios_iniciales(self, usernames: List[str]) -> bool:
        """
        Agrega usuarios iniciales a la base de datos (solo username, sin datos)
        
        Args:
            usernames (List[str]): Lista de usernames a agregar
            
        Returns:
            bool: True si se agregaron correctamente
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for username in usernames:
                    cursor.execute('''
                        INSERT OR IGNORE INTO usuarios_unicos (username, perfil_inactivo)
                        VALUES (?, FALSE)
                    ''', (username,))
                
                conn.commit()
                print(f"[+] Agregados {len(usernames)} usuarios iniciales a la BD")
                return True
                
        except Exception as e:
            print(f"[!] Error agregando usuarios iniciales: {e}")
            return False
    
    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas de la base de datos
        
        Returns:
            Dict: Estadísticas de usuarios y media
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Estadísticas de usuarios
                cursor.execute('SELECT COUNT(*) FROM usuarios_unicos')
                total_usuarios = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM usuarios_unicos WHERE perfil_inactivo = TRUE')
                usuarios_inactivos = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM usuarios_unicos WHERE perfil_privado = TRUE')
                usuarios_privados = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM usuarios_unicos WHERE categoria IS NOT NULL')
                usuarios_negocio = cursor.fetchone()[0]
                
                # Estadísticas de media
                cursor.execute('SELECT COUNT(*) FROM media_urls')
                total_media = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM media_urls WHERE tipo_media = "post"')
                total_posts = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM media_urls WHERE tipo_media = "destacada"')
                total_destacadas = cursor.fetchone()[0]
                
                return {
                    'total_usuarios': total_usuarios,
                    'usuarios_activos': total_usuarios - usuarios_inactivos,
                    'usuarios_inactivos': usuarios_inactivos,
                    'usuarios_privados': usuarios_privados,
                    'usuarios_negocio': usuarios_negocio,
                    'total_media': total_media,
                    'total_posts': total_posts,
                    'total_destacadas': total_destacadas
                }
                
        except Exception as e:
            print(f"[!] Error obteniendo estadísticas: {e}")
            return {}
    
    def exportar_a_csv(self) -> bool:
        """
        Exporta los datos a archivos CSV si está configurado
        
        Returns:
            bool: True si se exportó correctamente o no era necesario
        """
        from config import OUTPUT_CONFIG
        
        if not OUTPUT_CONFIG.get('save_csv', False):
            print("[*] Exportación CSV deshabilitada en config")
            return True
        
        try:
            import csv
            
            archivo_usuarios = OUTPUT_CONFIG.get('csv_file', 'usuarios_export.csv')
            
            with sqlite3.connect(self.db_path) as conn:
                # Exportar usuarios
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM usuarios_unicos')
                
                with open(archivo_usuarios, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    # Headers
                    writer.writerow([description[0] for description in cursor.description])
                    # Datos
                    writer.writerows(cursor.fetchall())
                
                print(f"[+] Datos exportados a {archivo_usuarios}")
                return True
                
        except Exception as e:
            print(f"[!] Error exportando a CSV: {e}")
            return False
    
    def obtener_todos_los_datos(self, incluir_media: bool = True) -> Dict:
        """
        Obtiene TODOS los datos de la base de datos para testing
        
        Args:
            incluir_media (bool): Si incluir las URLs de media o solo usuarios
            
        Returns:
            Dict: Todos los datos de la base de datos
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Obtener todos los usuarios
                cursor.execute('SELECT * FROM usuarios_unicos ORDER BY fecha_scraping DESC')
                usuarios_raw = cursor.fetchall()
                
                # Obtener nombres de columnas para usuarios
                cursor.execute('PRAGMA table_info(usuarios_unicos)')
                columnas_usuarios = [col[1] for col in cursor.fetchall()]
                
                # Convertir usuarios a diccionarios
                usuarios = []
                for usuario_raw in usuarios_raw:
                    usuario_dict = dict(zip(columnas_usuarios, usuario_raw))
                    usuarios.append(usuario_dict)
                
                resultado = {
                    'total_usuarios': len(usuarios),
                    'usuarios': usuarios,
                    'timestamp_consulta': datetime.now().isoformat()
                }
                
                # Incluir media si se solicita
                if incluir_media:
                    cursor.execute('SELECT * FROM media_urls ORDER BY fecha_scraping DESC')
                    media_raw = cursor.fetchall()
                    
                    # Obtener nombres de columnas para media
                    cursor.execute('PRAGMA table_info(media_urls)')
                    columnas_media = [col[1] for col in cursor.fetchall()]
                    
                    # Convertir media a diccionarios
                    media = []
                    for media_item_raw in media_raw:
                        media_dict = dict(zip(columnas_media, media_item_raw))
                        media.append(media_dict)
                    
                    resultado['total_media'] = len(media)
                    resultado['media_urls'] = media
                
                print(f"[+] Obtenidos {len(usuarios)} usuarios y {len(media) if incluir_media else 0} elementos de media")
                return resultado
                
        except Exception as e:
            print(f"[!] Error obteniendo todos los datos: {e}")
            return {}
    
    def obtener_usuario_especifico(self, username: str, incluir_media: bool = True) -> Dict:
        """
        Obtiene todos los datos de un usuario específico para testing
        
        Args:
            username (str): Username del usuario a obtener
            incluir_media (bool): Si incluir las URLs de media
            
        Returns:
            Dict: Datos completos del usuario
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Obtener datos del usuario
                cursor.execute('SELECT * FROM usuarios_unicos WHERE username = ?', (username,))
                usuario_raw = cursor.fetchone()
                
                if not usuario_raw:
                    print(f"[!] Usuario '{username}' no encontrado en la BD")
                    return {}
                
                # Obtener nombres de columnas para usuarios
                cursor.execute('PRAGMA table_info(usuarios_unicos)')
                columnas_usuarios = [col[1] for col in cursor.fetchall()]
                
                # Convertir a diccionario
                usuario_dict = dict(zip(columnas_usuarios, usuario_raw))
                
                resultado = {
                    'usuario': usuario_dict,
                    'timestamp_consulta': datetime.now().isoformat()
                }
                
                # Incluir media si se solicita
                if incluir_media:
                    cursor.execute('SELECT * FROM media_urls WHERE username = ? ORDER BY fecha_scraping DESC', (username,))
                    media_raw = cursor.fetchall()
                    
                    # Obtener nombres de columnas para media
                    cursor.execute('PRAGMA table_info(media_urls)')
                    columnas_media = [col[1] for col in cursor.fetchall()]
                    
                    # Convertir media a diccionarios
                    media = []
                    for media_item_raw in media_raw:
                        media_dict = dict(zip(columnas_media, media_item_raw))
                        media.append(media_dict)
                    
                    resultado['total_media'] = len(media)
                    resultado['media_urls'] = media
                
                print(f"[+] Obtenidos datos completos de '{username}': {len(media) if incluir_media else 0} elementos de media")
                return resultado
                
        except Exception as e:
            print(f"[!] Error obteniendo datos de {username}: {e}")
            return {}
    
    def exportar_datos_completos_json(self, archivo: str = "datos_completos.json") -> bool:
        """
        Exporta TODOS los datos a un archivo JSON para testing
        
        Args:
            archivo (str): Nombre del archivo JSON
            
        Returns:
            bool: True si se exportó correctamente
        """
        try:
            datos_completos = self.obtener_todos_los_datos(incluir_media=True)
            
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(datos_completos, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"[+] Datos completos exportados a {archivo}")
            print(f"    - {datos_completos.get('total_usuarios', 0)} usuarios")
            print(f"    - {datos_completos.get('total_media', 0)} elementos de media")
            
            return True
            
        except Exception as e:
            print(f"[!] Error exportando datos completos: {e}")
            return False

    def limpiar_base_datos(self) -> bool:
        """
        Limpia completamente la base de datos (CUIDADO: elimina todos los datos)
        
        Returns:
            bool: True si se limpió correctamente
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM media_urls')
                cursor.execute('DELETE FROM usuarios_unicos')
                conn.commit()
                
                print("[+] Base de datos limpiada completamente")
                return True
                
        except Exception as e:
            print(f"[!] Error limpiando base de datos: {e}")
            return False

# ==============================================================================
# FUNCIONES DE CONVENIENCIA
# ==============================================================================

def crear_base_datos(db_path: str = "instagram_data.db") -> InstagramDatabase:
    """
    Función de conveniencia para crear una instancia de la base de datos
    
    Args:
        db_path (str): Ruta al archivo de base de datos
        
    Returns:
        InstagramDatabase: Instancia de la base de datos
    """
    return InstagramDatabase(db_path)

def agregar_usuarios_desde_lista(usernames: List[str], db_path: str = "instagram_data.db") -> bool:
    """
    Función de conveniencia para agregar usuarios iniciales desde una lista
    
    Args:
        usernames (List[str]): Lista de usernames
        db_path (str): Ruta al archivo de base de datos
        
    Returns:
        bool: True si se agregaron correctamente
    """
    db = InstagramDatabase(db_path)
    return db.agregar_usuarios_iniciales(usernames)

def inicializar_con_perfiles_famosos(db_path: str = "instagram_data.db") -> bool:
    """
    Inicializa la base de datos con perfiles públicos famosos si está vacía
    
    Args:
        db_path (str): Ruta al archivo de base de datos
        
    Returns:
        bool: True si se inicializó correctamente
    """
    db = InstagramDatabase(db_path)
    
    # Verificar si ya hay usuarios en la base de datos
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM usuarios_unicos')
            total_usuarios = cursor.fetchone()[0]
            
            if total_usuarios > 0:
                print(f"[*] Base de datos ya contiene {total_usuarios} usuarios")
                return True
    except Exception as e:
        print(f"[!] Error verificando base de datos: {e}")
        return False
    
    # Lista de perfiles públicos famosos para inicializar
    perfiles_famosos = [
        # Deportistas
        'leomessi',           # Lionel Messi
        'cristiano',          # Cristiano Ronaldo
        'neymarjr',          # Neymar Jr
        'k.mbappe',          # Kylian Mbappé
        'sergiamos',         # Sergio Ramos
        'fcbarcelona',       # FC Barcelona
        'realmadrid',        # Real Madrid
        
        # Celebridades internacionales
        'therock',           # Dwayne Johnson
        'arianagrande',      # Ariana Grande
        'selenagomez',       # Selena Gomez
        'justinbieber',      # Justin Bieber
        'taylorswift',       # Taylor Swift
        'kimkardashian',     # Kim Kardashian
        'kyliejenner',       # Kylie Jenner
        
        # Marcas y medios
        'instagram',         # Instagram oficial
        'netflix',           # Netflix
        'nike',              # Nike
        'adidas',            # Adidas
        'cocacola',          # Coca Cola
        'nasa',              # NASA
        'natgeo',            # National Geographic
        
        # Celebridades hispanohablantes
        'shakira',           # Shakira
        'jbalvin',           # J Balvin
        'maluma',            # Maluma
        'badgalriri',        # Rihanna
        'zendaya',           # Zendaya
        
        # Influencers y creadores
        'elrubius',          # ElRubius
        'theellenshow',      # Ellen DeGeneres
        'gordodan',          # DanTDM
        'pewdiepie',         # PewDiePie
        
        # Actores y entretenimiento
        'vancityreynolds',   # Ryan Reynolds
        'priyankachopra',    # Priyanka Chopra
        'vindiesel',         # Vin Diesel
        'tomholland2013',    # Tom Holland
        'zacefron',          # Zac Efron
        
        # Música
        'ddlovato',          # Demi Lovato
        'champagnepapi',     # Drake
        'justintimberlake',  # Justin Timberlake
        'brunomars',         # Bruno Mars
        'ladygaga',          # Lady Gaga
    ]
    
    print(f"[+] Inicializando base de datos con {len(perfiles_famosos)} perfiles famosos...")
    
    success = db.agregar_usuarios_iniciales(perfiles_famosos)
    
    if success:
        print("[+] Base de datos inicializada con perfiles famosos")
        print("[*] Estos perfiles están listos para ser scrapeados")
        return True
    else:
        print("[!] Error inicializando base de datos con perfiles famosos")
        return False

# ==============================================================================
# SCRIPT DE PRUEBA
# ==============================================================================

if __name__ == '__main__':
    print("=== PRUEBA DEL MÓDULO DE BASE DE DATOS ===\n")
    
    # Crear instancia de BD
    db = InstagramDatabase("test_instagram.db")
    
    # Agregar algunos usuarios de prueba
    usuarios_prueba = ['leomessi', 'cristiano', 'nasa', 'instagram']
    db.agregar_usuarios_iniciales(usuarios_prueba)
    
    # Simular datos de usuario scrapeado
    datos_usuario_ejemplo = {
        'username': 'leomessi',
        'full_name': 'Leo Messi',
        'biography': 'Futbolista profesional',
        'follower_count': 500000000,
        'following_count': 300,
        'media_count': 1000,
        'is_private': False,
        'is_business': True,
        'category': 'Athlete',
        'external_url': 'https://example.com',
        'posts': [
            {
                'thumbnail_url': 'https://example.com/post1.jpg',
                'is_video': False,
                'like_count': 1000000,
                'comment_count': 50000
            },
            {
                'thumbnail_url': 'https://example.com/post2.jpg',
                'is_video': True,
                'like_count': 2000000,
                'comment_count': 75000
            }
        ],
        'highlights': [
            {
                'thumbnail_url': 'https://example.com/highlight1.jpg',
                'title': 'Mundial'
            }
        ]
    }
    
    # Insertar usuario y media
    db.insertar_usuario(datos_usuario_ejemplo)
    db.insertar_media_urls('leomessi', datos_usuario_ejemplo)
    
    # Mostrar estadísticas
    stats = db.obtener_estadisticas()
    print("\n=== ESTADÍSTICAS ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Exportar a CSV
    db.exportar_a_csv("test_usuarios.csv", "test_media.csv")
    
    print("\n[+] Prueba completada. Revisa los archivos generados.")