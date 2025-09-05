import os
import requests
from supabase import create_client, Client
import time

# --- 1. CONEXIÓN A LA BASE DE DATOS ---
def inicializar_supabase():
    url_supabase = os.environ.get("SUPABASE_URL")
    key_supabase = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url_supabase, key_supabase)
    print("✅ Conexión del Orquestador a Supabase establecida.")
    return supabase

# --- 2. FUNCIÓN PARA "DESPERTAR" A UN TRABAJADOR ---
# Railway nos da una URL especial para reiniciar un servicio.
def despertar_trabajador(nombre_trabajador):
    print(f"⏰ Despertando al {nombre_trabajador}...")
    # En el futuro, aquí pondremos la URL de reinicio que nos da Railway.
    # Por ahora, solo lo simulamos.
    print(f"✅ Orden de reinicio enviada a {nombre_trabajador}.")
    return True

# --- EL PUNTO DE ENTRADA: EL CEREBRO DEL ORQUESTADOR ---
def main():
    print("\n--- CICLO DEL ORQUESTADOR INICIADO ---")
    supabase = inicializar_supabase()
    
    if not supabase:
        print("❌ No se pudo conectar a Supabase. Abortando ciclo.")
        return

    # PRIORIDAD 1: ¿HAY LEADS LISTOS PARA PERSUADIR?
    print("1. Verificando si hay prospectos para el Persuasor...")
    response_persuadir = supabase.table('prospectos').select('prospecto_id', count='exact').eq('estado_prospecto', 'analizado_calificado').execute()
    if response_persuadir.count > 0:
        print(f"  -> ¡Sí! Hay {response_persuadir.count} leads listos. Despertando al Persuasor.")
        despertar_trabajador("worker-persuasor")
        return # Terminamos el ciclo aquí para darle prioridad.

    # PRIORIDAD 2: ¿HAY PROSPECTOS CAZADOS PARA ANALIZAR?
    print("2. Verificando si hay prospectos para el Analista...")
    response_analizar = supabase.table('prospectos').select('prospecto_id', count='exact').eq('estado_prospecto', 'cazado').execute()
    if response_analizar.count > 0:
        print(f"  -> ¡Sí! Hay {response_analizar.count} prospectos cazados. Despertando al Analista.")
        despertar_trabajador("worker-analista")
        return

    # PRIORIDAD 3: ¿NECESITAMOS CAZAR MÁS PROSPECTOS?
    print("3. Verificando si se necesita cazar nuevos prospectos...")
    # Esta lógica será más compleja en el futuro (revisará cuotas diarias, etc.)
    # Por ahora, simplemente activará al cazador si no hay otras tareas.
    print("  -> Decisión: Activar al Cazador para buscar nuevos prospectos.")
    despertar_trabajador("worker-cazador")
    
    print("--- CICLO DEL ORQUESTADOR FINALIZADO ---")

# --- BUCLE PRINCIPAL ---
if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Ocurrió un error en el ciclo principal del Orquestador: {e}")
        
        # El Orquestador revisa el estado del sistema cada 5 minutos.
        print("\nOrquestador en modo de espera por 5 minutos...")
        time.sleep(300)
