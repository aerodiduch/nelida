#!/usr/bin/env python3
"""
Test para verificar RSS feeds de medios argentinos
"""
import sys
import os
import asyncio
from dotenv import load_dotenv

# Cargar variables de entorno PRIMERO
load_dotenv()

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.functions.rss_feeds import obtener_noticias_hoy, obtener_noticias_categoria, rss_manager

async def test_rss_feeds():
    """Test completo del sistema RSS"""
    
    print("📰 Probando sistema RSS para medios argentinos")
    print("=" * 60)
    
    # Test 1: RSS Manager básico
    print("1️⃣ Test RSS Manager - Feeds configurados")
    print(f"📡 Feeds disponibles: {len(rss_manager.feeds)}")
    for key, feed in rss_manager.feeds.items():
        print(f"   • {feed['nombre']}: {feed['descripcion']}")
    
    print("\n" + "-" * 60)
    
    # Test 2: Parsear un feed específico
    print("2️⃣ Test parsing de Clarín")
    try:
        noticias_clarin = rss_manager.parse_feed("clarin")
        if noticias_clarin:
            print(f"✅ Clarín parseado: {len(noticias_clarin)} noticias")
            print(f"   Primera noticia: {noticias_clarin[0]['titulo'][:60]}...")
            print(f"   Fuente: {noticias_clarin[0]['fuente']}")
            print(f"   Categoría: {noticias_clarin[0]['categoria']}")
        else:
            print("❌ No se pudieron obtener noticias de Clarín")
    except Exception as e:
        print(f"❌ Error con Clarín: {e}")
    
    print("\n" + "-" * 60)
    
    # Test 3: Función de noticias de hoy
    print("3️⃣ Test función obtener_noticias_hoy")
    try:
        resultado_hoy = await obtener_noticias_hoy(limite=5, user_id=12345)
        
        if resultado_hoy['success']:
            print(f"✅ Noticias de hoy obtenidas: {resultado_hoy['total']}")
            print(f"📰 Fuentes: {', '.join(resultado_hoy['fuentes'])}")
            
            print("\n📋 Primeras 3 noticias:")
            for i, noticia in enumerate(resultado_hoy['noticias'][:3], 1):
                print(f"   {i}. {noticia['titulo'][:50]}...")
                print(f"      📍 {noticia['fuente']} - {noticia['categoria']} - {noticia['hora']}")
        else:
            print(f"❌ Error: {resultado_hoy['error']}")
            
    except Exception as e:
        print(f"❌ Excepción: {e}")
    
    print("\n" + "-" * 60)
    
    # Test 4: Noticias por categoría
    print("4️⃣ Test función obtener_noticias_categoria")
    try:
        resultado_politica = await obtener_noticias_categoria("política", limite=3, user_id=12345)
        
        if resultado_politica['success']:
            print(f"✅ Noticias de política: {resultado_politica['total']}")
            
            for i, noticia in enumerate(resultado_politica['noticias'], 1):
                print(f"   {i}. {noticia['titulo'][:50]}...")
                print(f"      📍 {noticia['fuente']} - {noticia['hora']}")
        else:
            print(f"❌ Error: {resultado_politica['error']}")
            
    except Exception as e:
        print(f"❌ Excepción: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Resultado del Test:")
    print("• Si ves noticias de hoy con títulos argentinos = ✅ RSS funcionando")
    print("• Si hay errores de conexión = verificar URLs de feeds")
    print("• Fuentes esperadas: Clarín, La Nación, Infobae, Perfil")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_rss_feeds())