import os
from supabase import create_client
import time
import json
from flask import Flask, request, jsonify
from threading import Thread

# --- INICIALIZACIÓN DE SERVICIOS ---
supabase_url = os.environ.get("https://orquestador-production.up.railway.app/crear-campana")
supabase_key = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxndGlodGZ5bmRuZmtidXdmYnhvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU5OTg4MjIsImV4cCI6MjA3MTU3NDgyMn0.K4igC3AgVkrmO6EDJDY9L_T-etecDTEXpmKfPimUE-g")
supabase = create_client(supabase_url, supabase_key)

app = Flask(__name__) # Inicializamos el servidor web Flask

# --- EL CEREBRO DEL ORQUESTADOR (El ciclo que ya conocemos) ---
def ciclo_del_orquestador():
    while True:
        print("\n--- INICIANDO CICLO DEL ORQUESTADOR ---")
        try:
            # Tarea 1: Buscar campañas 'pendientes'
            response_campanas = supabase.table('campanas').select('*').eq('estado_campana', 'pendiente').limit(1).execute()
            if response_campanas.data:
                # ... (Aquí irá la lógica para despertar a los workers, que añadiremos después) ...
                print(f"Se encontró una campaña pendiente: {response_campanas.data[0]['id']}")
                # Por ahora, solo la marcamos como 'cazando'
                supabase.table('campanas').update({'estado_campana': 'cazando'}).eq('id', response_campanas.data[0]['id']).execute()
                print("Campaña marcada como 'cazando'.")
            else:
                print("No hay campañas nuevas.")
            
            # ... (Aquí irá la lógica para revisar 'cazados', 'analizados', etc.) ...

        except Exception as e:
            print(f"Error en el ciclo del Orquestador: {e}")
        
        print("--- CICLO FINALIZADO. Durmiendo por 1 minuto. ---")
        time.sleep(60)

# --- LA NUEVA "PUERTA DE ESCUCHA" (API para el Dashboard) ---
@app.route('/crear-campana', methods=['POST'])
def crear_nueva_campana():
    print("\n¡Recibida una nueva orden del Dashboard!")
    try:
        # Obtenemos los datos que nos envía el Dashboard
        datos_formulario = request.get_json()
        
        # Preparamos la nueva campaña para guardarla
        nueva_campana = {
            'cliente_id': 1, # Fijo por ahora
            'nombre_campana': f"Campaña: {datos_formulario['cliente_ideal']}",
            'criterio_busqueda': json.dumps(datos_formulario),
            'estado_campana': 'pendiente' # ¡Lista para ser recogida por el ciclo!
        }

        # Guardamos la campaña en Supabase
        supabase.table('campanas').insert(nueva_campana).execute()
        print("✅ Nueva campaña guardada en la base de datos.")
        
        # Le respondemos al Dashboard que todo salió bien
        return jsonify({"status": "success", "message": "Campaña creada con éxito."}), 200

    except Exception as e:
        print(f"❌ Error al procesar la orden del Dashboard: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- ARRANQUE DEL SISTEMA ---
if __name__ == '__main__':
    # Iniciamos el ciclo del Orquestador en un "hilo" separado para que no bloquee la API
    orquestador_thread = Thread(target=ciclo_del_orquestador)
    orquestador_thread.daemon = True
    orquestador_thread.start()
    
    # Ponemos a funcionar la "puerta de escucha" (el servidor Flask)
    # Railway nos dará el puerto a través de la variable de entorno PORT
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
