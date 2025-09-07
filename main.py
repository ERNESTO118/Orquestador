import os
import requests
from supabase import create_client
import time
import json

# --- CONEXIÓN A SUPABASE ---
def inicializar_supabase():
    url_supabase = os.environ.get("SUPABASE_URL")
    key_supabase = os.environ.get("SUPABASE_KEY")
    return create_client(url_supabase, key_supabase)

# --- FUNCIÓN PARA "DESPERTAR" A UN TRABAJADOR ---
def despertar_trabajador(nombre_trabajador):
    print(f"⏰ Despertando al {nombre_trabajador}...")
    # Esta función necesitará la URL de reinicio de Railway en el futuro
    print(f"✅ Orden de reinicio enviada a {nombre_trabajador}.")
    return True

# --- EL CEREBRO DEL ORQUESTADOR v2.0 ---
def main():
    print("\n--- CICLO DEL ORQUESTADOR INICIADO ---")
    supabase = inicializar_supabase()
    if not supabase: return

    # TAREA 1: BUSCAR NUEVAS CAMPAÑAS PENDIENTES
    print("1. Verificando si hay campañas 'pendientes'...")
    response_campanas = supabase.table('campanas').select('*').eq('estado_campana', 'pendiente').limit(1).execute()

    if response_campanas.data:
        campana = response_campanas.data[0]
        id_campana = campana['id']
        print(f"  -> ¡Sí! Se encontró la campaña pendiente ID: {id_campana}. Iniciando...")
        
        supabase.table('campanas').update({'estado_campana': 'cazando'}).eq('id', id_campana).execute()
        despertar_trabajador("worker-cazador")
        return

    # TAREA 2: BUSCAR PROSPECTOS LISTOS PARA ANALIZAR
    print("2. Verificando si hay prospectos 'cazados'...")
    response_analizar = supabase.table('prospectos').select('prospecto_id', count='exact').eq('estado_prospecto', 'cazado').execute()
    if response_analizar.count > 0:
        print(f"  -> ¡Sí! Hay {response_analizar.count} prospectos listos. Despertando al Analista.")
        despertar_trabajador("worker-analista")
        return

    # TAREA 3: BUSCAR LEADS LISTOS PARA PERSUADIR
    print("3. Verificando si hay prospectos 'analizado_calificado'...")
    response_persuadir = supabase.table('prospectos').select('prospecto_id', count='exact').eq('estado_prospecto', 'analizado_calificado').execute()
    if response_persuadir.count > 0:
        print(f"  -> ¡Sí! Hay {response_persuadir.count} leads listos. Despertando al Persuasor.")
        despertar_trabajador("worker-persuadir")
        return
    
    print("✅ No hay nuevas tareas pendientes.")
    print("--- CICLO DEL ORQUESTADOR FINALIZADO ---")

# --- BUCLE PRINCIPAL ---
if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Ocurrió un error en el ciclo del Orquestador: {e}")
        
        print("\nOrquestador en modo de espera por 1 minuto...")
        time.sleep(60)
