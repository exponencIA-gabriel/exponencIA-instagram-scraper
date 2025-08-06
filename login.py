import requests
import json
import time
import re
import os
import getpass
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ==============================================================================
# MÓDULO DE LOGIN CENTRALIZADO PARA INSTAGRAM
# ==============================================================================

class InstagramLogin:
    def __init__(self):
        self.session = None
        self.tokens = None
        self.credentials_file = 'instagram_credentials.json'
        self.username = None
        self.password = None
    
    def get_credentials(self):
        """Obtiene credenciales del usuario con prompt seguro"""
        print("=== CREDENCIALES DE INSTAGRAM ===")
        
        # Intentar cargar credenciales guardadas
        if os.path.exists(self.credentials_file):
            try:
                with open(self.credentials_file, 'r') as f:
                    saved_creds = json.load(f)
                
                print(f"[*] Se encontraron credenciales guardadas para: {saved_creds.get('username', 'N/A')}")
                use_saved = input("¿Usar credenciales guardadas? (s/n): ").lower().strip()
                
                if use_saved in ['s', 'si', 'y', 'yes', '']:
                    self.username = saved_creds['username']
                    self.password = saved_creds['password']
                    return self.username, self.password
                    
            except Exception as e:
                print(f"[!] Error leyendo credenciales guardadas: {e}")
        
        # Pedir credenciales nuevas
        print("\n[*] Ingresa tus credenciales de Instagram:")
        self.username = input("Username: ").strip()
        
        # Usar getpass para ocultar la contraseña
        self.password = getpass.getpass("Password: ")
        
        # Preguntar si guardar credenciales
        save_creds = input("\n¿Guardar credenciales para próximas ejecuciones? (s/n): ").lower().strip()
        
        if save_creds in ['s', 'si', 'y', 'yes']:
            try:
                with open(self.credentials_file, 'w') as f:
                    json.dump({
                        'username': self.username,
                        'password': self.password
                    }, f)
                print(f"[+] Credenciales guardadas en {self.credentials_file}")
                print("[!] IMPORTANTE: Este archivo contiene tu contraseña. Manténlo seguro.")
            except Exception as e:
                print(f"[!] Error guardando credenciales: {e}")
        
        return self.username, self.password
    
    def authenticate(self, headless=True):
        """
        Proceso completo de autenticación:
        1. Obtiene credenciales del usuario
        2. Hace login con Selenium
        3. Extrae tokens dinámicos
        4. Configura sesión de requests
        5. Devuelve sesión lista para usar
        """
        print("=== AUTENTICACIÓN DE INSTAGRAM ===\n")
        
        # 1. Obtener credenciales
        username, password = self.get_credentials()
        
        # 2. Configurar Selenium
        print(f"\n[*] Iniciando autenticación para: {username}")
        print("[*] Configurando navegador...")
        
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        try:
            # 3. Hacer login
            print("[*] Accediendo a Instagram...")
            driver.get("https://www.instagram.com/accounts/login/")
            wait = WebDriverWait(driver, 15)
            
            # Llenar formulario de login
            print("[*] Llenando formulario de login...")
            user_input = wait.until(EC.element_to_be_clickable((By.NAME, 'username')))
            pass_input = wait.until(EC.element_to_be_clickable((By.NAME, 'password')))
            
            user_input.send_keys(username)
            pass_input.send_keys(password)
            
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Esperar login exitoso
            print("[*] Esperando confirmación de login...")
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/direct/inbox/')]")))
                print("[+] ¡Login exitoso!")
            except:
                # Verificar si hay verificación adicional requerida
                if "challenge" in driver.current_url or "two_factor" in driver.current_url:
                    print("[!] Se requiere verificación adicional.")
                    print("[!] Por favor, completa la verificación manualmente en el navegador.")
                    input("Presiona Enter cuando hayas completado la verificación...")
                else:
                    print("[!] Login puede haber fallado. Continuando...")
                    time.sleep(5)
            
            # 4. Ir a un perfil para extraer tokens
            print("[*] Extrayendo tokens de autenticación...")
            driver.get("https://www.instagram.com/instagram/")
            time.sleep(3)
            
            # 5. Extraer valores dinámicos del HTML
            page_source = driver.page_source
            
            # Extraer CSRF token
            csrf_token = self._extract_csrf_token(driver, page_source)
            
            # Extraer fb_lsd
            fb_lsd = self._extract_fb_lsd(page_source)
            
            # Extraer fb_dtsg
            fb_dtsg = self._extract_fb_dtsg(page_source)
            
            # Doc ID para GraphQL
            doc_id = "7663787143717254"  # Doc ID que funciona para PolarisProfilePageContentQuery
            
            # 6. Obtener cookies
            cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
            
            # 7. Obtener user agent
            user_agent = driver.execute_script("return navigator.userAgent;")
            
            # 8. Mostrar estado de tokens
            self._show_token_status(csrf_token, fb_lsd, fb_dtsg)
            
            # 9. Configurar sesión de requests
            session = requests.Session()
            session.cookies.update(cookies)
            
            # Headers importantes
            session.headers.update({
                'User-Agent': user_agent,
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'es-ES,es;q=0.9,en;q=0.8',
                'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'upgrade-insecure-requests': '1',
                'x-ig-app-id': '936619743392459'
            })
            
            # 10. Guardar tokens
            self.tokens = {
                'csrf_token': csrf_token,
                'fb_lsd': fb_lsd,
                'fb_dtsg': fb_dtsg,
                'doc_id': doc_id,
                'user_agent': user_agent
            }
            
            self.session = session
            
            print("[+] ¡Autenticación completada exitosamente!")
            print(f"[+] Sesión configurada para el usuario: {username}")
            
            return True
            
        except Exception as e:
            print(f"[!] Error durante la autenticación: {e}")
            return False
        finally:
            driver.quit()
    
    def _extract_csrf_token(self, driver, page_source):
        """Extrae el CSRF token del HTML"""
        csrf_token = None
        
        # Método 1: Meta tag
        try:
            csrf_meta = driver.find_elements(By.XPATH, "//meta[@name='csrf-token']")
            if csrf_meta:
                csrf_token = csrf_meta[0].get_attribute('content')
        except:
            pass
        
        # Método 2: Buscar en el HTML
        if not csrf_token:
            csrf_match = re.search(r'"csrf_token":"([^"]+)"', page_source)
            if csrf_match:
                csrf_token = csrf_match.group(1)
        
        return csrf_token
    
    def _extract_fb_lsd(self, page_source):
        """Extrae el fb_lsd token del HTML"""
        # Intentar múltiples patrones
        patterns = [
            r'"LSD",\[\],{"token":"([^"]+)"',
            r'"lsd":"([^"]+)"',
            r'name="lsd" value="([^"]+)"'
        ]
        
        for pattern in patterns:
            lsd_match = re.search(pattern, page_source)
            if lsd_match:
                return lsd_match.group(1)
        
        return None
    
    def _extract_fb_dtsg(self, page_source):
        """Extrae el fb_dtsg token del HTML"""
        # Intentar múltiples patrones
        patterns = [
            r'"DTSGInitialData",\[\],{"token":"([^"]+)"',
            r'"fb_dtsg":"([^"]+)"',
            r'name="fb_dtsg" value="([^"]+)"'
        ]
        
        for pattern in patterns:
            dtsg_match = re.search(pattern, page_source)
            if dtsg_match:
                return dtsg_match.group(1)
        
        return None
    
    def _show_token_status(self, csrf_token, fb_lsd, fb_dtsg):
        """Muestra el estado de los tokens extraídos"""
        print("\n--- Estado de Tokens ---")
        print(f"CSRF Token: {'✅ ' + csrf_token[:20] + '...' if csrf_token else '❌ No encontrado'}")
        print(f"FB LSD: {'✅ ' + fb_lsd[:20] + '...' if fb_lsd else '❌ No encontrado'}")
        print(f"FB DTSG: {'✅ ' + fb_dtsg[:20] + '...' if fb_dtsg else '❌ No encontrado'}")
        print("------------------------\n")
    
    def get_session(self):
        """Devuelve la sesión autenticada"""
        return self.session
    
    def get_tokens(self):
        """Devuelve los tokens de autenticación"""
        return self.tokens
    
    def get_username(self):
        """Devuelve el username actual"""
        return self.username
    
    def is_authenticated(self):
        """Verifica si la sesión está autenticada"""
        return self.session is not None and self.tokens is not None

# ==============================================================================
# FUNCIÓN DE CONVENIENCIA
# ==============================================================================

def get_instagram_session(headless=True):
    """
    Función de conveniencia para obtener una sesión autenticada de Instagram
    
    Args:
        headless (bool): Si ejecutar el navegador en modo headless
    
    Returns:
        tuple: (session, tokens, username) si es exitoso, (None, None, None) si falla
    """
    login = InstagramLogin()
    
    if login.authenticate(headless=headless):
        return login.get_session(), login.get_tokens(), login.get_username()
    else:
        return None, None, None

# ==============================================================================
# SCRIPT DE PRUEBA
# ==============================================================================

if __name__ == '__main__':
    print("=== PRUEBA DEL MÓDULO DE LOGIN ===\n")
    
    # Probar autenticación
    session, tokens, username = get_instagram_session(headless=False)  # Mostrar navegador para debug
    
    if session and tokens:
        print("\n[+] ¡Autenticación exitosa!")
        print(f"[+] Usuario: {username}")
        print(f"[+] Sesión configurada con {len(session.cookies)} cookies")
        print(f"[+] Tokens disponibles: {list(tokens.keys())}")
        
        # Prueba rápida de la sesión
        print("\n[*] Probando sesión con una petición simple...")
        try:
            response = session.get("https://www.instagram.com/api/v1/users/web_profile_info/?username=instagram")
            if response.status_code == 200:
                print("[+] ¡Sesión funcionando correctamente!")
                data = response.json()
                user_data = data.get('data', {}).get('user', {})
                print(f"[+] Datos obtenidos para @instagram: {user_data.get('follower_count', 'N/A')} seguidores")
            else:
                print(f"[!] Sesión puede tener problemas (código: {response.status_code})")
        except Exception as e:
            print(f"[!] Error probando sesión: {e}")
    else:
        print("\n[!] Falló la autenticación")