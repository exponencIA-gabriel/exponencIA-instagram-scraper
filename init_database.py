#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de inicialización de base de datos para Instagram Scraper
Inicializa la base de datos con perfiles públicos famosos si está vacía
"""

from database import inicializar_con_perfiles_famosos
import os
import sys

def main():
    """Función principal de inicialización"""
    print("🚀 INICIALIZADOR DE BASE DE DATOS - Instagram Scraper")
    print("="*60)
    
    # Verificar si ya existe una base de datos
    db_path = "instagram_data.db"
    
    if os.path.exists(db_path):
        print(f"[*] Base de datos encontrada: {db_path}")
    else:
        print(f"[*] No se encontró base de datos, se creará: {db_path}")
    
    # Inicializar con perfiles famosos
    try:
        success = inicializar_con_perfiles_famosos(db_path)
        
        if success:
            print("\n✅ Inicialización completada exitosamente")
            print("\n📋 La base de datos ahora contiene perfiles famosos listos para scrapear:")
            print("   - Deportistas: Messi, Cristiano, Neymar, Mbappé...")
            print("   - Celebridades: The Rock, Ariana Grande, Taylor Swift...")
            print("   - Marcas: Instagram, Netflix, Nike, NASA...")
            print("   - Y muchos más perfiles públicos famosos")
            print("\n🚀 Puedes ejecutar 'python scraper_perfil.py' para comenzar el scraping")
        else:
            print("\n❌ Error durante la inicialización")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()