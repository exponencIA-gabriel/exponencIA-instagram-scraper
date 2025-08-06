# 🔒 Variables Hardcodeadas - Guía Técnica de Mantenimiento

## ⚠️ **PROBLEMA PENDIENTE DE RESOLVER**

**El scraper actual funciona con muchas variables hardcodeadas que eventualmente fallarán cuando Instagram actualice su API. Esta es una limitación técnica conocida que requiere mantenimiento periódico.**

---

## 🎯 **Resumen del Problema**

El scraper `scraper_perfil.py` utiliza una combinación de variables hardcodeadas y dinámicas para las solicitudes GraphQL. Mientras que los **tokens de autenticación son dinámicos**, muchas otras variables críticas están **hardcodeadas** y pueden fallar sin previo aviso.

### **📊 Estado Actual**
- ✅ **6 variables críticas** son dinámicas (tokens de autenticación)
- ⚠️ **8+ variables semi-críticas** están hardcodeadas (hashes de sesión)
- ✅ **20+ variables seguras** pueden estar hardcodeadas (headers HTTP)
- 🔒 **3 Doc IDs críticos** están hardcodeados por diseño

---

## 🔴 **Variables CRÍTICAS - Funcionan Correctamente (Dinámicas)**

```python
# TOKENS DE AUTENTICACIÓN (✅ Ya implementado dinámicamente)
'x-csrftoken': self.tokens['csrf_token']    # Obtenido del login
'x-fb-lsd': self.tokens['fb_lsd']           # Obtenido del login
'fb_dtsg': self.tokens['fb_dtsg']           # Obtenido del login
'lsd': self.tokens['fb_lsd']                # Obtenido del login

# PARÁMETROS DE CONSULTA (✅ Ya implementado dinámicamente)
'__req': str(req_type)                      # 3=user, 5=highlights, 7=posts
'doc_id': doc_id                            # Diferentes para cada tipo
'variables': json.dumps({...})              # Según user_id y tipo de consulta
```

---

## 🟡 **Variables SEMI-CRÍTICAS - PROBLEMA PENDIENTE**

### **⚠️ Estas variables están hardcodeadas y pueden fallar:**

```python
# IDENTIFICADORES DE SESIÓN (HARDCODEADOS - Deberían ser dinámicos)
'__hs': '20302.HYP:instagram_web_pkg.2.1...0'     # ⚠️ Versión de Instagram
'__rev': '1025456124'                              # ⚠️ Revisión de la aplicación
'__s': 'azx7hm:v651wx:jjbnoc'                      # ⚠️ Hash de sesión
'__hsi': '7534071026151167731'                     # ⚠️ ID de sesión
'__spin_t': '1754162606'                           # ⚠️ Timestamp (puede expirar)
'jazoest': '26195'                                 # ⚠️ Token de validación

# HASHES COMPLEJOS (HARDCODEADOS - Muy difíciles de generar)
'__dyn': '7xeUjG1mxu1syUbFp41twpUnwgU7S6EdF8aUco38w5ux609vCwjE1EE2Cw8G11w6zx62G3i1ywOwa90Fw4Hw9O0M82zxe2GewGw9a361qw8W5U4q09yyES1Twoob82ZwrUdUbGw4mwr86C1mwrd6goK10xKi2qi7E5y4UrwHwcObBK4o16UswFwOwgU'
'__csr': 'hk4c5sIdiiWeWkp4my9OFliOZZm_GGlbnl8FQW_jqWWXrHZelBAGKQWAUxqjH9mGh9mtyGKcZ2rVtlmVCqfXmWupfAGm8QqUDhEOEnjqVHBGUGcAAx2hpoO4ojS7aDBzqxi5BAhUB5VeV8lyoyAWyQElABzoC4ayu79V8S4Uiw05vaw2bU25o30K1NA80qu584No0zapo1lU3zwwP1uuE0Z-07gVE4e7UKlF2cU1Iodo6Z2UTo1n86dwVg8UJCOwkcw3pc0nCpO08Vk7k0tdw09oK06480aHo'
'__hsdp': 'gngpiOl4cZSxIajNnhshkxk2p6kKnjmEFEj9bae42bzXy98hzIywDwSzC9xpwCx22t7oTzVFNiwxD9AIU92zoCp3U6wwaob9QEaoe8hz8hwNwTgkefy8fUW0BopwXzUphGXAyopDwda7o10U6d05uwjE2vw2a821xa1eG3K3S1Hw8u0R8W0CE521mg8iw4pwxwLwhjzo6a0Jo562C'
'__hblp': '1i7Q1YwJK9xN6mmcG12xKU2BCwv8bFFEC69E5a68Dgbbx22qAUSfGm8wGK2h2Ebk4ayohwNAG1rBGES2up3ojxy9wKwLxC5Q1chGBWyo-9DDwgE6i2a7ojwe-10wygiw8S0Lo4W3K18xG0Bo1gE4uu2K1fBBz85-2mu3S1HwVwjo3kzE2qAwiVoS11o8iwdm13wxzo6ix0N0oogwai68dqxq4E'
'__sjsp': 'gngpiOl4cZSDPMFf5t5N5i5g9ApiVtdqyCxcAIwYg8K4Uyi4o7meoC3-48a9QeU-qskE8pOpbe2ydw3nEdE'
```

### **🚨 Riesgo de Estas Variables:**
- **Pueden invalidarse** con actualizaciones de Instagram
- **Difíciles de regenerar** automáticamente
- **Requieren extracción manual** desde DevTools del navegador
- **No hay algoritmo conocido** para generarlas dinámicamente

---

## 🔒 **Doc IDs - PROBLEMA CRÍTICO PENDIENTE**

```python
# HARDCODEADOS POR DISEÑO (Pueden cambiar sin aviso)
DOC_IDS = {
    'user': '24059491867034637',      # ⚠️ CRÍTICO - Puede cambiar
    'highlights': '9814547265267853', # ⚠️ CRÍTICO - Puede cambiar  
    'posts': '24312092678414792'      # ⚠️ CRÍTICO - Puede cambiar
}
```

### **🚨 Riesgo de los Doc IDs:**
- **Críticos para el funcionamiento** del scraper
- **Pueden cambiar sin previo aviso** con actualizaciones de Instagram
- **Cuando fallan, el scraper deja de funcionar completamente**
- **Requieren monitoreo constante** y actualización manual

---

## 🟢 **Variables SEGURAS - No Requieren Cambios**

```python
# HEADERS HTTP ESTÁNDAR (✅ Seguros para hardcodear)
'accept': '*/*'
'content-type': 'application/x-www-form-urlencoded'
'origin': 'https://www.instagram.com'
'referer': 'https://www.instagram.com/'

# INFORMACIÓN DEL NAVEGADOR (✅ Seguros para hardcodear)
'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N)...'
'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138"...'

# IDENTIFICADORES DE APLICACIÓN (✅ Seguros para hardcodear)
'x-ig-app-id': '1217981644879628'
'x-asbd-id': '359341'

# PARÁMETROS FIJOS (✅ Seguros para hardcodear)
'av': '17841476332219581'
'__d': 'www'
'__user': '0'
'dpr': '2'
```

---

## 🔧 **Cómo Actualizar Variables Cuando Fallan**

### **1. Detectar Variables Obsoletas**
```bash
# Señales de que necesita actualización:
# ❌ Error 400: "execution error" → Doc IDs obsoletos
# ❌ Error 403: "Forbidden" → Hashes obsoletos  
# ❌ Respuestas vacías → Parámetros incorrectos
# ❌ Rate limiting → User Agent detectado
```

### **2. Obtener Nuevos Valores desde DevTools**
```bash
# 1. Abrir Instagram en Chrome/Edge
# 2. DevTools (F12) > Network tab
# 3. Filtrar por 'graphql'
# 4. Realizar una acción (ver perfil, posts, highlights)
# 5. Buscar solicitudes POST a /graphql/query
# 6. Copiar valores de Headers y Form Data
```

### **3. Actualizar Doc IDs**
```python
# En scraper_perfil.py, línea ~32:
self.DOC_IDS = {
    'user': 'NUEVO_DOC_ID_USUARIO',
    'highlights': 'NUEVO_DOC_ID_HIGHLIGHTS', 
    'posts': 'NUEVO_DOC_ID_POSTS'
}
```

### **4. Actualizar Variables de Sesión**
```python
# En make_graphql_request(), actualizar:
'__hs': 'NUEVO_VALOR_HS',
'__rev': 'NUEVO_VALOR_REV',
'__s': 'NUEVO_VALOR_S',
'__hsi': 'NUEVO_VALOR_HSI',
'__spin_t': 'NUEVO_TIMESTAMP',
'jazoest': 'NUEVO_JAZOEST',
'__dyn': 'NUEVO_HASH_DYN',
'__csr': 'NUEVO_HASH_CSR',
# ... etc
```

---

## 📊 **Frecuencia de Mantenimiento Esperada**

| Variable | Frecuencia de Cambio | Dificultad de Actualización |
|----------|---------------------|----------------------------|
| **Doc IDs** | 1-3 meses | 🟡 Media (copiar desde DevTools) |
| **Hashes de sesión** | 2-6 meses | 🔴 Alta (múltiples valores) |
| **Timestamps** | 3-12 meses | 🟢 Baja (un solo valor) |
| **Versiones** | 6-12 meses | 🟢 Baja (valores simples) |

---

## 🚨 **LIMITACIONES ACTUALES**

### **❌ Lo que NO está implementado:**
1. **Generación automática** de hashes complejos (`__dyn`, `__csr`)
2. **Detección automática** de Doc IDs obsoletos
3. **Rotación automática** de User Agents
4. **Monitoreo proactivo** de variables que van a expirar
5. **Fallback automático** cuando las variables fallan

### **⚠️ Dependencias Manuales:**
- **Extracción manual** de variables desde DevTools
- **Actualización manual** del código cuando falla
- **Monitoreo manual** de la tasa de éxito
- **Testing manual** después de cada actualización

---

## 💡 **SOLUCIONES FUTURAS RECOMENDADAS**

### **🎯 Prioridad Alta:**
1. **Sistema de monitoreo automático** que detecte cuando variables fallan
2. **Extractor automático de Doc IDs** desde las páginas de Instagram
3. **Rotación automática de User Agents** para evitar detección

### **🎯 Prioridad Media:**
1. **Parser automático de hashes** desde el JavaScript de Instagram
2. **Sistema de fallback** con múltiples conjuntos de variables
3. **Alertas automáticas** cuando el scraper necesita mantenimiento

### **🎯 Prioridad Baja:**
1. **Ingeniería inversa** de los algoritmos de generación de hashes
2. **Simulación completa** del navegador para generar variables dinámicamente

---

## 🔍 **Herramientas de Debugging Actuales**

```python
# Activar modo debug
scraper = ScraperPerfil(debug_mode=True)

# Ver requests completos en archivos debug_response_*.json
# Analizar errores específicos
# Comparar con solicitudes exitosas del navegador
```

---

## ⚡ **CONCLUSIÓN**

**El scraper actual es funcional pero requiere mantenimiento manual periódico. Las variables hardcodeadas son una limitación técnica conocida que eventualmente causará fallos cuando Instagram actualice su API.**

### **Estado Actual:**
- ✅ **Funciona correctamente** con las variables actuales
- ⚠️ **Requiere monitoreo** para detectar cuando falla
- 🔧 **Necesita mantenimiento manual** cuando las variables expiran

### **Recomendación:**
**Usar el scraper en su estado actual, pero estar preparado para actualizarlo manualmente cuando las variables hardcodeadas fallen. Considerar implementar las soluciones automáticas mencionadas para reducir el mantenimiento futuro.**

---

**📅 Última actualización:**  6/8/2025  
