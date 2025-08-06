# Instagram Scraper GraphQL Completo - Sistema Avanzado con Base de Datos

Sistema de scraping avanzado de Instagram que usa GraphQL API directa para extraer datos completos de usuarios, incluyendo posts e historias destacadas, con base de datos SQLite para evitar re-scrapear perfiles ya completos.

## 🚀 Inicio Rápido

### 📥 **Clonar desde Git**
```bash
# Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd instagram-scraper

# Instalar dependencias
pip install selenium webdriver-manager requests

# Inicializar base de datos con perfiles famosos
python init_database.py
```

### 🏠 **Instalación Local**
1. **Instalar dependencias:**
   ```bash
   pip install selenium webdriver-manager requests
   ```

2. **Inicializar base de datos (automático):**
   ```bash
   python scraper_perfil.py
   # La base de datos se inicializa automáticamente con perfiles famosos
   ```

3. **O inicializar manualmente:**
   ```bash
   python init_database.py
   ```

### 🎯 **Comenzar Scraping**
```bash
python scraper_perfil.py
# Seleccionar opción 1: Scrapear usuarios pendientes
# Login interactivo → Scraping automático de perfiles famosos
```

## 📁 Archivos del Proyecto

### 🎯 **Archivos Principales (Solo 5 esenciales)**
- **`scraper_perfil.py`** - 🆕 Scraper de perfiles completo con posts e highlights
- **`database.py`** - Módulo de base de datos SQLite con inicialización automática
- **`login.py`** - Sistema de login interactivo (EL ÚNICO archivo de login)
- **`config.py`** - Configuración del proyecto
- **`init_database.py`** - 🆕 Script de inicialización independiente para Git

### 🔧 **Archivos de Configuración Git**
- **`.gitignore`** - Configurado para ignorar BD, credenciales y archivos temporales
- **`README.md`** - Documentación completa del proyecto
- **`README_VARIABLES.md`** - Documentación técnica de variables

## 🆕 Características del Nuevo Scraper GraphQL

### ✅ **Datos Completos Extraídos**
- **Información básica**: Seguidores, siguiendo, biografía, etc.
- **Posts**: Thumbnails, likes, comentarios, tipo (foto/video)
- **Highlights**: Títulos, thumbnails de historias destacadas
- **Estadísticas**: Promedios, totales, análisis automático


### 🔒 **Variables Hardcodeadas vs Dinámicas**

El scraper utiliza una combinación de variables hardcodeadas y dinámicas para las solicitudes GraphQL. Aquí se explica cada tipo:

#### **🔴 Variables CRÍTICAS - Deben ser Dinámicas**
```python
# TOKENS DE AUTENTICACIÓN (Obtenidos dinámicamente del login)
'x-csrftoken': self.tokens['csrf_token']    # ✅ DINÁMICO - Cambia en cada sesión
'x-fb-lsd': self.tokens['fb_lsd']           # ✅ DINÁMICO - Cambia en cada sesión  
'fb_dtsg': self.tokens['fb_dtsg']           # ✅ DINÁMICO - Cambia en cada sesión
'lsd': self.tokens['fb_lsd']                # ✅ DINÁMICO - Cambia en cada sesión

# PARÁMETROS DE CONSULTA (Dinámicos según la operación)
'__req': str(req_type)                      # ✅ DINÁMICO - 3=user, 5=highlights, 7=posts.
                                             # Nota: Si bien en la inspección el __req varía según si el query es de user, highlights o posts, la consulta funciona igual con otro valor
'doc_id': doc_id                            # ✅ DINÁMICO - Diferentes para cada tipo
'variables': json.dumps({...})              # ✅ DINÁMICO - Según user_id y tipo de consulta´


```

#### **🟡 Variables SEMI-CRÍTICAS - Deberían ser Dinámicas**
```python
# IDENTIFICADORES DE SESIÓN (Actualmente hardcodeados, deberían ser dinámicos)
'__hs': '20302.HYP:instagram_web_pkg.2.1...0'     # ⚠️ HARDCODEADO - Debería ser dinámico
'__rev': '1025456124'                              # ⚠️ HARDCODEADO - Versión de Instagram
'__s': 'azx7hm:v651wx:jjbnoc'                      # ⚠️ HARDCODEADO - Hash de sesión
'__hsi': '7534071026151167731'                     # ⚠️ HARDCODEADO - ID de sesión
'__spin_t': '1754162606'                           # ⚠️ HARDCODEADO - Timestamp
'jazoest': '26195'                                 # ⚠️ HARDCODEADO - Token de validación

# HASHES COMPLEJOS (Muy difíciles de generar dinámicamente)
'__dyn': '7xeUjG1mxu1syUbFp41twpUnwgU7S6EdF8aUco38w5ux609vCwjE1EE2Cw8G11w6zx62G3i1ywOwa90Fw4Hw9O0M82zxe2GewGw9a361qw8W5U4q09yyES1Twoob82ZwrUdUbGw4mwr86C1mwrd6goK10xKi2qi7E5y4UrwHwcObBK4o16UswFwOwgU'  # Hash de capacidades dinámicas
'__csr': 'hk4c5sIdiiWeWkp4my9OFliOZZm_GGlbnl8FQW_jqWWXrHZelBAGKQWAUxqjH9mGh9mtyGKcZ2rVtlmVCqfXmWupfAGm8QqUDhEOEnjqVHBGUGcAAx2hpoO4ojS7aDBzqxi5BAhUB5VeV8lyoyAWyQElABzoC4ayu79V8S4Uiw05vaw2bU25o30K1NA80qu584No0zapo1lU3zwwP1uuE0Z-07gVE4e7UKlF2cU1Iodo6Z2UTo1n86dwVg8UJCOwkcw3pc0nCpO08Vk7k0tdw09oK06480aHo'  # Hash de configuración del cliente
'__hsdp', '__hblp', '__sjsp': '[HASHES_LARGOS]'  # Otros hashes de seguridad y configuración
```

#### **🟢 Variables SEGURAS - Pueden estar Hardcodeadas**
```python
# HEADERS HTTP ESTÁNDAR
'accept': '*/*'                                    # ✅ HARDCODEADO - Estándar HTTP
'content-type': 'application/x-www-form-urlencoded' # ✅ HARDCODEADO - Tipo de contenido
'origin': 'https://www.instagram.com'             # ✅ HARDCODEADO - Origen fijo
'referer': 'https://www.instagram.com/'           # ✅ HARDCODEADO - Referencia fija

# INFORMACIÓN DEL NAVEGADOR (User Agent)
'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N)...' # ✅ HARDCODEADO - Simula dispositivo
'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138"...'                  # ✅ HARDCODEADO - Info del navegador
'sec-ch-ua-platform': '"Android"'                 # ✅ HARDCODEADO - Plataforma simulada
'sec-ch-ua-mobile': '?1'                          # ✅ HARDCODEADO - Indica móvil

# IDENTIFICADORES DE APLICACIÓN
'x-ig-app-id': '1217981644879628'                 # ✅ HARDCODEADO - ID de la app de Instagram
'x-asbd-id': '359341'                             # ✅ HARDCODEADO - ID de seguridad
'x-bloks-version-id': '4fd52d0e0985dd463fefe21d18f1609258ecf3c799cc7f12f6c4363b56697384' # ✅ HARDCODEADO

# PARÁMETROS FIJOS
'av': '17841476332219581'                         # ✅ HARDCODEADO - ID de aplicación
'__d': 'www'                                      # ✅ HARDCODEADO - Dominio
'__user': '0'                                     # ✅ HARDCODEADO - Usuario por defecto
'__a': '1'                                        # ✅ HARDCODEADO - Parámetro de aplicación
'dpr': '2'                                        # ✅ HARDCODEADO - Device Pixel Ratio
'__ccg': 'EXCELLENT'                              # ✅ HARDCODEADO - Calidad de conexión
'__spin_r': '1025456124'                          # ✅ HARDCODEADO - Versión de Spin
'__spin_b': 'trunk'                               # ✅ HARDCODEADO - Branch de Spin
'__comet_req': '7'                                # ✅ HARDCODEADO - Versión de Comet
'fb_api_caller_class': 'RelayModern'              # ✅ HARDCODEADO - Clase de API
'server_timestamps': 'true'                      # ✅ HARDCODEADO - Timestamps del servidor
```

#### **🔒 Doc IDs Hardcodeados (CRÍTICOS)**
```python
DOC_IDS = {
    'user': '24059491867034637',      # ⚠️ CRÍTICO - Puede cambiar con actualizaciones
    'highlights': '9814547265267853', # ⚠️ CRÍTICO - Puede cambiar con actualizaciones  
    'posts': '24312092678414792'      # ⚠️ CRÍTICO - Puede cambiar con actualizaciones
}
```

#### **📊 Resumen de Criticidad**

| Tipo | Riesgo | Estado | Acción |
|------|--------|--------|--------|
| 🔴 **Tokens de autenticación** | Alto | ✅ Dinámicos | Funcionan correctamente |
| 🟡 **Hashes de sesión** | Medio | ⚠️ Hardcodeados | Actualizar si fallan |
| 🟢 **Headers HTTP estándar** | Bajo | ✅ Hardcodeados | No requieren cambios |
| 🔒 **Doc IDs** | Alto | ⚠️ Hardcodeados | Monitorear cambios |

#### **🚨 Variables que Pueden Causar Problemas**

- **Doc IDs**: Críticos, pueden cambiar con actualizaciones de Instagram
- **Hashes de sesión**: Pueden invalidarse, actualizar si el scraper falla
- **Timestamps/Versiones**: Valores muy antiguos pueden ser rechazados

#### **💡 Recomendaciones**

- **Monitorear errores** para detectar variables obsoletas
- **Actualizar Doc IDs** cuando dejen de funcionar
- **Rotar User Agents** periódicamente para evitar detección

### � **Cómdo Actualizar Variables Hardcodeadas**

Cuando el scraper deje de funcionar, probablemente sea por variables hardcodeadas obsoletas. Aquí se explica cómo actualizarlas:

#### **1. Obtener Nuevos Doc IDs**
```bash
# Abrir Instagram en el navegador
# DevTools > Network > Filtrar por 'graphql'
# Buscar consultas que devuelvan datos de usuario/posts/highlights
# Copiar el doc_id de cada consulta

# Actualizar en scraper_perfil.py:
self.DOC_IDS = {
    'user': 'NUEVO_DOC_ID_USUARIO',
    'highlights': 'NUEVO_DOC_ID_HIGHLIGHTS', 
    'posts': 'NUEVO_DOC_ID_POSTS'
}
```

#### **2. Actualizar Variables de Sesión**
```bash
# En DevTools > Network, copiar una solicitud GraphQL exitosa
# Buscar estos valores en los headers/payload:
# - __hs, __rev, __s, __hsi, __spin_t, jazoest
# - __dyn, __csr, __hsdp, __hblp, __sjsp

# Actualizar en el método make_graphql_request()
```

#### **3. Señales de Variables Obsoletas**
- **Error 400**: Parámetros inválidos (doc_id o hashes obsoletos)
- **Error 403**: Tokens de autenticación inválidos
- **Error 429**: Rate limiting (cambiar User Agent)
- **Respuesta vacía**: Doc ID incorrecto

#### **4. Herramientas de Debugging**
```python
# Activar modo debug para ver requests completos
scraper = ScraperPerfil(debug_mode=True)

# Ver respuestas completas en archivos debug_response_*.json
```

## 🗄️ Base de Datos

### 🎯 **Inicialización Automática con Perfiles Famosos**

El sistema incluye inicialización automática con perfiles listos para scrapear

### **🗂️ Estructura de Tablas**

### Tabla `usuarios_unicos`
- `username` - Username del usuario (clave primaria)
- `perfil_inactivo` - Si el perfil no se pudo scrapear
- `nombre_persona` - Nombre real de la persona
- `categoria` - Categoría si es perfil de negocio
- `perfil_privado` - Si el perfil es privado
- `cantidad_publicaciones` - Número de posts
- `cantidad_destacadas` - Número de historias destacadas
- `cantidad_seguidores` - Número de seguidores
- `cantidad_seguidos` - Número de seguidos
- `biografia` - Biografía del perfil
- `links_externos` - URL externa del perfil

### Tabla `media_urls`
- `username` - Username (clave foránea)
- `url_media` - URL de la imagen/video
- `tipo_media` - 'post' o 'destacada'
- `subtipo_post` - 'foto', 'reel', 'video' (solo posts)
- `cantidad_likes` - Likes del post
- `cantidad_comentarios` - Comentarios del post

## 🔐 Sistema de Login

**`login.py` es EL ÚNICO archivo que maneja la autenticación.** No hay otros archivos de login.

### Características:
- **Login interactivo**: Te pide usuario y contraseña al ejecutar
- **Contraseña oculta**: Usa `getpass` para ocultar la contraseña
- **Guardado opcional**: Puede guardar credenciales en `instagram_credentials.json`
- **Tokens automáticos**: Extrae automáticamente CSRF, fb_lsd, fb_dtsg
- **Manejo de 2FA**: Soporte para verificación adicional
- **Sesión completa**: Devuelve sesión de `requests` lista para usar

### Uso programático:
```python
from login import get_instagram_session

# Obtener sesión autenticada
session, tokens, username = get_instagram_session()
```

## ⚙️ Configuración

En `config.py`:

```python
# Configuración de scraping
SCRAPING_CONFIG = {
    'delay_min': 2,           # Delay mínimo entre requests
    'delay_max': 6,           # Delay máximo entre requests
    'headless': True,         # Chrome sin ventana visible
    'force_rescrape': False,  # Si re-scrapear perfiles completos
}

# Archivos de salida
OUTPUT_CONFIG = {
    'save_csv': True,         # Si guardar archivo CSV
    'csv_file': 'instagram_profiles.csv',
    'database_file': 'instagram_data.db',
}
```

## 📊 Información Detallada por Consola

El nuevo scraper muestra información completa durante la extracción:

### **Datos de Usuario**
```
✓ Datos de usuario obtenidos:
   👤 Nombre: @leomessi
   📝 Biografía: Futbolista profesional...
   👥 Seguidores: 500,000,000
   👤 Siguiendo: 300
   📸 Posts: 1,000
   🔒 Privado: No
   🏢 Negocio: Sí
   📂 Categoría: Athlete
   🔗 Link externo: https://example.com
```

### **Highlights**
```
✓ 15 highlights obtenidos
   📚 Highlights encontrados:
      1. Mundial
      2. Familia
      3. Entrenamientos
      4. Viajes
      5. Celebraciones
      ... y 10 más
```

### **Posts**
```
✓ 12 posts obtenidos
   📊 Estadísticas de posts:
      📸 Fotos: 8 | 🎥 Videos: 4
      ❤️ Total likes: 15,000,000
      💬 Total comentarios: 250,000
      📈 Promedio likes: 1,250,000
```

### **Resumen Final**
```
📋 RESUMEN COMPLETO - @leomessi
==================================================
👥 Seguidores: 500,000,000
👤 Siguiendo: 300
📸 Posts totales: 1,000
📸 Posts extraídos: 12
📚 Highlights: 15
🔒 Perfil privado: No
📂 Categoría: Athlete
```

## 🧠 Lógica Inteligente

El sistema evita re-scrapear perfiles ya completos:

- **Perfil Completo**: Tiene `cantidad_seguidores`, `cantidad_seguidos` y `cantidad_publicaciones` != NULL
- **Perfil Pendiente**: Le falta alguno de los campos principales
- **Force Rescrape**: Configurar `force_rescrape = True` para re-scrapear todo

## 🎯 Flujo de Trabajo Simple

1. **Agregar usuarios:**
   ```bash
   python scraper_perfil.py
   # Opción 2 → Ingresar: leomessi,cristiano,nasa
   ```

2. **Scrapear usuarios pendientes:**
   ```bash
   python scraper_perfil.py  
   # Opción 1 → Login interactivo → Scraping automático
   ```

3. **Scrapear usuario específico:**
   ```bash
   python scraper_perfil.py
   # Opción 4 → Ingresar username → Ver datos completos
   ```

4. **Ver estadísticas:**
   ```bash
   python scraper_perfil.py
   # Opción 3 → Ver estadísticas detalladas de BD
   ```

## 🔧 Uso de la Base de Datos

### Con DB Browser for SQLite (Recomendado)
1. Descargar [DB Browser for SQLite](https://sqlitebrowser.org/)
2. Abrir `instagram_data.db`
3. Ver/editar datos directamente

### Consultas SQL Útiles
```sql
-- Ver usuarios con más posts extraídos
SELECT u.username, u.cantidad_seguidores, COUNT(m.url_media) as posts_extraidos
FROM usuarios_unicos u
LEFT JOIN media_urls m ON u.username = m.username AND m.tipo_media = 'post'
GROUP BY u.username
ORDER BY u.cantidad_seguidores DESC;

-- Ver estadísticas de engagement
SELECT u.username, 
       AVG(m.cantidad_likes) as promedio_likes,
       AVG(m.cantidad_comentarios) as promedio_comentarios
FROM usuarios_unicos u
JOIN media_urls m ON u.username = m.username
WHERE m.tipo_media = 'post'
GROUP BY u.username
ORDER BY promedio_likes DESC;

-- Ver usuarios con highlights
SELECT u.username, u.cantidad_destacadas, COUNT(m.url_media) as highlights_extraidos
FROM usuarios_unicos u
LEFT JOIN media_urls m ON u.username = m.username AND m.tipo_media = 'destacada'
GROUP BY u.username
HAVING u.cantidad_destacadas > 0
ORDER BY u.cantidad_destacadas DESC;
```

## 🗂️ Archivos que Puedes Eliminar

### 🧪 **Archivos de Testing/Debug (Seguros para eliminar)**
```bash
# Scripts de debugging
rm debug_*.py
rm test_*.py
rm standalone_debug.py

# Respuestas de ejemplo
rm ejemplo_response_*.json
rm debug_response_*.json

# Herramientas de doc_id (ya no necesarias)
rm find_working_doc_ids.py
rm auto_doc_id_finder.py
rm doc_id_manager.py
rm test_doc_ids.py

# Scripts de testing específicos
rm test_format_fix.py
rm test_doc_id_logic.py
rm test_real_user.py
rm test_new_extraction.py
rm test_data_viewer.py
rm debug_now.py
rm debug_problematic_users.py
```

### 📚 **Archivos Legacy (Mantener como referencia)**
```bash
# Mantener por ahora como referencia
# scraper_user_data.py - Scraper original
# query_data_user.py - Prototipo GraphQL
```

## 🔒 Seguridad

- Login interactivo (no credenciales hardcodeadas)
- Contraseña oculta con `getpass`
- Delays inteligentes entre requests
- Manejo de 2FA y verificaciones adicionales
- Doc IDs hardcodeados (no búsqueda dinámica)

## 📊 Archivos Generados

- `instagram_data.db` - Base de datos SQLite principal (**ignorado por Git**)
- `instagram_profiles.csv` - Archivo CSV (si está habilitado) (**ignorado por Git**)
- `instagram_credentials.json` - Credenciales guardadas (**ignorado por Git**)
```

### **🔒 Archivos Ignorados por Git**
El `.gitignore` está configurado para ignorar automáticamente:

```gitignore
# Credenciales de Instagram (NUNCA subir a Git)
instagram_credentials.json
*credentials*.json
*password*.txt
*login*.json
*auth*.json

# Base de datos (se regenera automáticamente)
*.db
*.sqlite
*.sqlite3

# Resultados y archivos temporales
*.csv
debug_response_*.json
temp_*

# Archivos de sesión y cookies
session_*
cookies_*
*.session

# Python
__pycache__/
*.pyc
venv/
.venv/

# Logs y debugging
*.log
debug_*.txt

# Selenium drivers
chromedriver*
geckodriver*

# Archivos del sistema
.DS_Store
Thumbs.db
```

### **🛡️ Seguridad de Credenciales**
- ✅ **instagram_credentials.json** - Completamente ignorado por Git
- ✅ **Contraseñas** - Nunca se almacenan en código fuente
- ✅ **Tokens de sesión** - Solo en memoria durante ejecución
- ✅ **Cookies** - No se guardan en archivos versionados

### **📝 Configuración Manual de Credenciales (Opcional)**
Si prefieres configurar credenciales manualmente:

```bash
# Copiar el archivo de ejemplo
cp instagram_credentials.example.json instagram_credentials.json

# Editar con tus credenciales reales
# IMPORTANTE: instagram_credentials.json está en .gitignore y NUNCA se subirá a Git
```

Formato del archivo `instagram_credentials.json`:
```json
{
  "username": "tu_username_real",
  "password": "tu_password_real"
}
```

## � *o*Monitoreo y Mantenimiento**

### **📊 Indicadores de Salud del Scraper**
```python
# Ejecutar diagnóstico
python scraper_perfil.py
# Opción 4 → Probar con un usuario conocido

# Señales de que necesita mantenimiento:
# ❌ Error 400: "execution error" → Doc IDs obsoletos
# ❌ Error 403: "Forbidden" → Tokens/hashes obsoletos  
# ❌ Respuestas vacías → Parámetros incorrectos
# ❌ Rate limiting → Cambiar User Agent
```

### **🔄 Frecuencia de Actualización Recomendada**
- **Doc IDs**: Verificar mensualmente o cuando fallen
- **Hashes de sesión**: Actualizar cada 2-3 meses
- **User Agent**: Rotar semanalmente
- **Tokens de autenticación**: Se renuevan automáticamente

### **📈 Optimización de Rendimiento**
```python
# Configurar delays apropiados en config.py
SCRAPING_CONFIG = {
    'delay_min': 2,    # Mínimo 2 segundos entre requests
    'delay_max': 6,    # Máximo 6 segundos para evitar detección
}

# Monitorear tasa de éxito
# > 90% éxito = Configuración óptima
# < 70% éxito = Necesita mantenimiento
```

## 🚨 Consideraciones

- Respetar términos de servicio de Instagram
- Uso moderado para evitar detección
- Los tokens expiran, renovar sesión periódicamente
- **Variables hardcodeadas requieren mantenimiento periódico**
- **Doc IDs son críticos y pueden cambiar sin aviso**
- **Monitorear regularmente la tasa de éxito del scraper**

---




