# Instagram Scraper GraphQL Completo - Sistema Avanzado con Base de Datos

Sistema de scraping avanzado de Instagram que usa GraphQL API directa para extraer datos completos de usuarios, incluyendo posts e historias destacadas, con base de datos SQLite para evitar re-scrapear perfiles ya completos.

## 🚀 Inicio Rápido

1. **Instalar dependencias:**
   ```bash
   pip install selenium webdriver-manager requests
   ```

2. **Agregar usuarios a la base de datos:**
   ```bash
   python scraper_perfil.py
   # Seleccionar opción 2: Agregar usuarios a BD
   # Ingresar usernames separados por comas: leomessi,cristiano,nasa
   ```

3. **Scrapear usuarios:**
   ```bash
   python scraper_perfil.py
   # Seleccionar opción 1: Scrapear usuarios pendientes
   ```

## 📁 Archivos del Proyecto

### 🎯 **Archivos Principales (Solo 4 esenciales)**
- **`scraper_perfil.py`** - 🆕 Scraper de perfiles completo con posts e highlights
- **`database.py`** - Módulo de base de datos SQLite  
- **`login.py`** - Sistema de login interactivo (EL ÚNICO archivo de login)
- **`config.py`** - Configuración del proyecto

## 🆕 Características del Nuevo Scraper GraphQL

### ✅ **Datos Completos Extraídos**
- **Información básica**: Seguidores, siguiendo, biografía, etc.
- **Posts**: Thumbnails, likes, comentarios, tipo (foto/video)
- **Highlights**: Títulos, thumbnails de historias destacadas
- **Estadísticas**: Promedios, totales, análisis automático


### 🔒 **Variables Hardcodeadas vs Dinámicas**

El scraper utiliza una combinación de variables hardcodeadas y dinámicas para las solicitudes GraphQL. Aquí se explica cada tipo:

#### **📊 Resumen de Criticidad**

| Tipo | Riesgo | Estado | Acción |
|------|--------|--------|--------|
| 🔴 **Tokens de autenticación** | Alto | ✅ Dinámicos | Funcionan correctamente |
| 🟡 **Hashes de sesión** | Medio | ⚠️ Hardcodeados | Actualizar si fallan |
| 🟢 **Headers HTTP estándar** | Bajo | ✅ Hardcodeados | No requieren cambios |
| 🔒 **Doc IDs** | Alto | ⚠️ Hardcodeados | Monitorear cambios |

## 🗄️ Base de Datos

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

- `instagram_data.db` - Base de datos SQLite principal
- `instagram_profiles.csv` - Archivo CSV (si está habilitado)
- `instagram_credentials.json` - Credenciales guardadas (opcional)

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

## 🎉 **¡Nuevo Sistema GraphQL Completo!**

**El nuevo `scraper_perfil.py` es la evolución del sistema original, extrayendo datos completos de Instagram de forma rápida y eficiente usando la API GraphQL directa.**

### **Migración Recomendada:**
1. ✅ Usar `scraper_perfil.py` para nuevos proyectos
2. 📚 Mantener `scraper_user_data.py` como referencia
3. 🗑️ Eliminar archivos de testing/debug
4. 🔄 Migrar usuarios existentes ejecutando el nuevo scraper

