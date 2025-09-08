import os
import requests
from supabase import create_client
import time

# --- 1. CONEXIONES ---
def inicializar_supabase():
    try:
        url_supabase = os.environ.get("SUPABASE_URL")
        key_supabase = os.environ.get("SUPABASE_KEY")
        supabase = create_client(url_supabase, key_supabase)
        print("✅ Conexión del Orquestador a Supabase establecida.")
        return supabase
    except Exception as e:
        print(f"❌ Error al conectar con Supabase: {e}")
        return None

# --- 2. FUNCIÓN PARA "DESPERTAR" A UN TRABAJADOR ---
def despertar_trabajador(nombre_trabajador):
    print(f"⏰ Despertando al {nombre_trabajador}...")
    # Esta es una función placeholder. En el futuro la conectaremos a la API de Railway.
    print(f"✅ Orden de reinicio enviada a {nombre_trabajador}.")
    return True

# --- EL CEREBRO DEL ORQUESTADOR v3.0 (Simplificado y Robusto) ---
def main():
    print("\n--- CICLO DEL ORQUESTADOR INICIADO ---")
    supabase = inicializar_supabase()
    if not supabase:
        print("No se pudo conectar a Supabase. Saltando este ciclo.")
        return

    # PRIORIDAD 1: ¿HAY LEADS LISTOS PARA PERSUADIR?
    print("1. Verificando si hay prospectos para el Persuasor...")
    response_persuadir = supabase.table('prospectos').select('prospecto_id', count='exact').eq('estado_prospecto', 'analizado_calificado').execute()
    if response_persuadir.count > 0:
        print(f"  -> ¡Sí! Hay {response_persuadir.count} leads listos. Despertando al Persuasor.")
        despertar_trabajador("worker-persuasor")
        return

    # PRIORIDAD 2: ¿HAY PROSPECTOS CAZADOS PARA ANALIZAR?
    print("2. Verificando si hay prospectos para el Analista...")
    response_analizar = supabase.table('prospectos').select('prospecto_id', count='exact').eq('estado_prospecto', 'cazado').execute()
    if response_analizar.count > 0:
        print(f"  -> ¡Sí! Hay {response_analizar.count} prospectos cazados. Despertando al Analista.")
        despertar_trabajador("worker-analista")
        return

    # PRIORIDAD 3: ¿HAY CAMPAÑAS PENDIENTES PARA CAZAR?
    print("3. Verificando si hay campañas pendientes...")
    response_campanas = supabase.table('campanas').select('*').eq('estado_campana', 'pendiente').limit(1).execute()
    if response_campanas.data:
        id_campana = response_campanas.data[0]['id']
        print(f"  -> ¡Sí! Se encontró la campaña pendiente ID: {id_campana}. Despertando al Cazador.")
        supabase.table('campanas').update({'estado_campana': 'cazando'}).eq('id', id_campana).execute()
        despertar_trabajador("worker-cazador")
        return
    
    print("✅ No hay nuevas tareas pendientes. El sistema está al día.")
    print("--- CICLO DEL ORQUESTADOR FINALIZADO ---")

# --- BUCLE PRINCIPAL ---
if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Ocurrió un error en el ciclo principal del Orquestador: {e}")
        
        print("\nOrquestador en modo de espera por 1 minuto...")
        time.sleep(60)
