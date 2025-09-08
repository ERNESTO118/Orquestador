import os
from postgrest import PostgrestClient
import time
import json
from flask import Flask, request, jsonify
from threading import Thread

# --- INICIALIZACIÓN DE SERVICIOS ---
supabase_url = os.environ.get("https://lgtihtfyndnfkbuwfbxo.supabase.co")
supabase_key = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxndGlodGZ5bmRuZmtidXdmYnhvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU5OTg4MjIsImV4cCI6MjA3MTU3NDgyMn0.K4igC3AgVkrmO6EDJDY9L_T-etecDTEXpmKfPimUE-g")
supabase = PostgrestClient(base_url=supabase_url, headers={"apikey": supabase_key})
app = Flask(__name__)

# --- CICLO DEL ORQUESTADOR ---
def ciclo_del_orquestador():
    while True:
        print("\n--- INICIANDO CICLO DEL ORQUESTADOR ---")
        try:
            response = supabase.from_("campanas").select("*", count='exact').eq('estado_campana', 'pendiente').limit(1).execute()
            if response.data:
                id_campana = response.data[0]['id']
                print(f"Se encontró campaña pendiente ID: {id_campana}.")
                supabase.from_("campanas").update({'estado_campana': 'cazando'}).eq('id', id_campana).execute()
            else:
                print("No hay campañas nuevas.")
        except Exception as e:
            print(f"Error en el ciclo del Orquestador: {e}")
        
        print("--- CICLO FINALIZADO. Durmiendo. ---")
        time.sleep(60)

# --- API PARA EL DASHBOARD ---
@app.route('/crear-campana', methods=['POST'])
def crear_nueva_campana():
    print("\n¡Recibida nueva orden del Dashboard!")
    try:
        datos = request.get_json()
        nueva_campana = {
            'cliente_id': 1, 'nombre_campana': f"Campaña: {datos['cliente_ideal']}",
            'criterio_busqueda': json.dumps(datos), 'estado_campana': 'pendiente'
        }
        supabase.from_("campanas").insert(nueva_campana).execute()
        return jsonify({"message": "Campaña creada con éxito."}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# --- ARRANQUE ---
if __name__ == '__main__':
    orquestador_thread = Thread(target=ciclo_del_orquestador)
    orquestador_thread.daemon = True
    orquestador_thread.start()
    
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

```4.  **Guarda los cambios.**

Espera a que Railway redespliegue al Orquestador. Esta vez, el error de red en sus logs desaparecerá. Y cuando eso pase, el Dashboard podrá enviarle las órdenes sin problemas. ¡Este es el culpable que hemos estado buscando todo el día
