import os
import requests
from supabase import create_client, Client
import time

# --- 1. CONEXIONES ---
def inicializar_supabase():
    url_supabase = os.environ.get("SUPABASE_URL")
    key_supabase = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url_supabase, key_supabase)
    print("✅ Conexión del Orquestador a Supabase establecida.")
    return supabase

# --- 2. FUNCIÓN PARA "DESPERTAR" A UN TRABAJADOR ---
def despertar_trabajador(nombre_trabajador):
    print(f"⏰ Despertando al {nombre_trabajador}...")
    # En el futuro, aquí pondremos la URL de reinicio que nos da Railway.
    print(f"✅ Orden de reinicio enviada a {nombre_trabajador}.")
    return True

# --- EL CEREBRO DEL ORQUESTADOR v2.0 ---
def main():
    print("\n--- CICLO DEL ORQUESTADOR INICIADO ---")
    supabase = inicializar_supabase()
    if not supabase: return

    # TAREA 1: BUSCAR NUEVAS CAMPAÑAS SOLICITADAS POR EL CLIENTE
    print("1. Verificando si hay nuevas campañas pendientes...")
    response_campanas = supabase.table('campanas').select('*').eq('estado_campana', 'pendiente').limit(1).execute()

    if response_campanas.data:
        campana_a_iniciar = response_campanas.data[0]
        id_campana = campana_a_iniciar['id']
        print(f"  -> ¡Sí! Se encontró la campaña pendiente ID: {id_campana}. Iniciando proceso.")
        
        # Marcamos la campaña como 'en_proceso' para no volver a tomarla
        supabase.table('campanas').update({'estado_campana': 'cazando'}).eq('id', id_campana).execute()
        
        # Despertamos al primer trabajador de la línea
        despertar_trabajador("worker-cazador")
        return # Terminamos el ciclo aquí

    # (Aquí iría la lógica para despertar al Analista y al Persuasor que ya teníamos)
    
    print("✅ No hay nuevas tareas pendientes. El sistema está al día.")
    print("--- CICLO DEL ORQUESTADOR FINALIZADO ---")

# --- BUCLE PRINCIPAL ---
if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Ocurrió un error en el ciclo del Orquestador: {e}")
        
        print("\nOrquestador en modo de espera por 1 minuto...")
        time.sleep(60) # Lo ponemos a revisar cada minuto
