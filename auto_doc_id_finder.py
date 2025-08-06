#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BUSCADOR AUTOMÁTICO DE DOC_IDS
===============================

Script que automáticamente encuentra y valida doc_ids actuales
desde Instagram después del login.
"""

import requests
import json
import time
import re
from login import get_instagram_session

class AutoDocIdFinder:
    def __init__(self):
        self.session = None
        self.tokens = None
        self.username = None
    
    def authenticate(self):
        """Realiza la autenticación"""
        print("🔐 Iniciando autenticación...")
        session, tokens, username = get_instagram_session(headless=True)
        
        if not session or not tokens:
            print("❌ Error en la autenticación")
            return False
        
        self.session = session
        self.tokens = tokens
        self.username = username
        
        print(f"✅ Autenticado como: {username}")
        return True
    
    def extract_doc_ids_from_page(self, url: str, description: str) -> list:
        """Extrae doc_ids de una página específica"""
        print(f"   📄 Analizando: {description}")
        
        try:
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                print(f"      ❌ Error {response.status_code}")
                return []
            
            content = response.text
            doc_ids = []
            
            # Múltiples patrones para encontrar doc_ids
            patterns = [
                r'"doc_id":"(\d{15,25})"',
                r'doc_id:"(\d{15,25})"',
                r'"documentId":"(\d{15,25})"',
                r'documentId:"(\d{15,25})"',
                r'"queryId":"(\d{15,25})"',
                r'queryId:"(\d{15,25})"',
                r'PolarisProfilePageContentQuery.*?"doc_id":"(\d{15,25})"',
                r'"(\d{17,25})"',  # Números largos que podrían ser doc_ids
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                doc_ids.extend(matches)
            
            # Filtrar duplicados y validar
            unique_doc_ids = list(set(doc_ids))
            valid_doc_ids = [doc_id for doc_id in unique_doc_ids 
                           if doc_id.isdigit() and 15 <= len(doc_id) <= 25]
            
            print(f"      ✅ Encontrados {len(valid_doc_ids)} doc_ids únicos")
            return valid_doc_ids
            
        except Exception as e:
            print(f"      ❌ Error: {e}")
            return []
    
    def find_all_doc_ids(self) -> list:
        """Encuentra doc_ids desde múltiples fuentes"""
        print("\n🔍 BUSCANDO DOC_IDS AUTOMÁTICAMENTE...")
        print("="*50)
        
        all_doc_ids = []
        
        # Fuente 1: Página principal
        doc_ids_1 = self.extract_doc_ids_from_page(
            "https://www.instagram.com/", 
            "Página principal"
        )
        all_doc_ids.extend(doc_ids_1)
        
        # Fuente 2: Página de perfil público
        doc_ids_2 = self.extract_doc_ids_from_page(
            "https://www.instagram.com/instagram/", 
            "Perfil @instagram"
        )
        all_doc_ids.extend(doc_ids_2)
        
        # Fuente 3: Página de explorar
        doc_ids_3 = self.extract_doc_ids_from_page(
            "https://www.instagram.com/explore/", 
            "Página de explorar"
        )
        all_doc_ids.extend(doc_ids_3)
        
        # Fuente 4: Intentar obtener archivos JS
        try:
            print("   🔧 Analizando archivos JavaScript...")
            main_response = self.session.get("https://www.instagram.com/")
            
            if main_response.status_code == 200:
                # Buscar referencias a archivos JS
                js_pattern = r'src="([^"]*static/bundles/[^"]*\.js[^"]*)"'
                js_matches = re.findall(js_pattern, main_response.text)
                
                for i, js_path in enumerate(js_matches[:2]):  # Solo los primeros 2
                    if js_path.startswith('/'):
                        js_url = f"https://www.instagram.com{js_path}"
                    else:
                        js_url = js_path
                    
                    print(f"      📦 Archivo JS {i+1}: {js_path.split('/')[-1][:30]}...")
                    
                    try:
                        js_response = self.session.get(js_url, timeout=10)
                        if js_response.status_code == 200:
                            # Buscar doc_ids en el contenido JS
                            js_doc_ids = re.findall(r'"(\d{17,25})"', js_response.text)
                            valid_js_doc_ids = [doc_id for doc_id in js_doc_ids 
                                               if 15 <= len(doc_id) <= 25]
                            all_doc_ids.extend(valid_js_doc_ids)
                            print(f"         ✅ {len(valid_js_doc_ids)} doc_ids encontrados")
                    except:
                        print(f"         ❌ Error descargando archivo")
                        
        except Exception as e:
            print(f"   ❌ Error analizando JS: {e}")
        
        # Eliminar duplicados y ordenar
        unique_doc_ids = list(set(all_doc_ids))
        unique_doc_ids.sort(key=len, reverse=True)  # Los más largos primero
        
        print(f"\n📊 RESUMEN:")
        print(f"   Total doc_ids encontrados: {len(all_doc_ids)}")
        print(f"   Doc_ids únicos: {len(unique_doc_ids)}")
        
        return unique_doc_ids
    
    def validate_doc_id(self, doc_id: str, test_user_id: str = "1552043361") -> dict:
        """Valida un doc_id específico"""
        try:
            headers = {
                'accept': '*/*',
                'accept-language': 'es-419,es;q=0.9',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'x-csrftoken': self.tokens['csrf_token'],
                'x-fb-friendly-name': 'PolarisProfilePageContentQuery',
                'x-fb-lsd': self.tokens['fb_lsd'],
                'x-ig-app-id': '936619743392459',
            }
            
            payload = {
                'fb_dtsg': self.tokens['fb_dtsg'],
                'variables': json.dumps({
                    "id": test_user_id,
                    "render_surface": "PROFILE"
                }),
                'doc_id': doc_id,
            }
            
            response = self.session.post("https://www.instagram.com/api/graphql", 
                                       headers=headers, data=payload, timeout=10)
            
            result = {
                'doc_id': doc_id,
                'status_code': response.status_code,
                'valid': False,
                'error': None,
                'data_found': False
            }
            
            if response.status_code == 200:
                data = response.json()
                
                if 'errors' in data:
                    error_msg = data['errors'][0].get('message', '')
                    result['error'] = error_msg
                    result['valid'] = 'was not found' not in error_msg
                elif 'data' in data and 'user' in data['data'] and data['data']['user']:
                    result['valid'] = True
                    result['data_found'] = True
                    
                    # Obtener algunos datos para confirmar
                    user_data = data['data']['user']
                    result['username'] = user_data.get('username')
                    result['follower_count'] = user_data.get('follower_count')
            
            return result
            
        except Exception as e:
            return {
                'doc_id': doc_id,
                'status_code': 0,
                'valid': False,
                'error': str(e),
                'data_found': False
            }
    
    def validate_all_doc_ids(self, doc_ids: list) -> list:
        """Valida todos los doc_ids encontrados"""
        print(f"\n🧪 VALIDANDO {len(doc_ids)} DOC_IDS...")
        print("="*60)
        
        valid_doc_ids = []
        
        for i, doc_id in enumerate(doc_ids):
            print(f"{i+1:2d}. Validando {doc_id}...", end=" ")
            
            result = self.validate_doc_id(doc_id)
            
            if result['valid'] and result['data_found']:
                print(f"✅ VÁLIDO - @{result.get('username', 'N/A')} ({result.get('follower_count', 'N/A')} seguidores)")
                valid_doc_ids.append(doc_id)
            elif result['valid']:
                print(f"⚠️ Válido pero sin datos")
            else:
                error = result.get('error', 'Error desconocido')
                if 'was not found' in error:
                    print(f"❌ Doc ID no encontrado")
                else:
                    print(f"❌ Error: {error[:50]}...")
            
            # Pausa para no sobrecargar
            time.sleep(0.8)
        
        return valid_doc_ids
    
    def run(self):
        """Ejecuta el proceso completo"""
        print("🚀 BUSCADOR AUTOMÁTICO DE DOC_IDS")
        print("="*50)
        
        # 1. Autenticar
        if not self.authenticate():
            return
        
        # 2. Buscar doc_ids
        doc_ids = self.find_all_doc_ids()
        
        if not doc_ids:
            print("❌ No se encontraron doc_ids")
            return
        
        # 3. Validar doc_ids
        valid_doc_ids = self.validate_all_doc_ids(doc_ids[:50])  # Validar máximo 50
        
        # 4. Mostrar resultados
        print(f"\n{'🎉'*20}")
        print(f"📊 RESULTADOS FINALES")
        print(f"{'🎉'*20}")
        print(f"Doc_ids encontrados: {len(doc_ids)}")
        print(f"Doc_ids válidos: {len(valid_doc_ids)}")
        
        if valid_doc_ids:
            print(f"\n✅ DOC_IDS VÁLIDOS PARA USAR:")
            for i, doc_id in enumerate(valid_doc_ids):
                print(f"   {i+1}. {doc_id}")
            
            print(f"\n💡 RECOMENDACIÓN:")
            print(f"Usa este doc_id en tu scraper: {valid_doc_ids[0]}")
            
            # Guardar en archivo
            with open("valid_doc_ids.json", "w") as f:
                json.dump({
                    "timestamp": time.time(),
                    "valid_doc_ids": valid_doc_ids,
                    "recommended": valid_doc_ids[0] if valid_doc_ids else None
                }, f, indent=2)
            
            print(f"💾 Doc_ids guardados en: valid_doc_ids.json")
        else:
            print(f"\n❌ NO SE ENCONTRARON DOC_IDS VÁLIDOS")

def main():
    finder = AutoDocIdFinder()
    finder.run()

if __name__ == '__main__':
    main()