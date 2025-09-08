import os, time, json, requests
from supabase import create_client
from flask import Flask, request, jsonify
from threading import Thread

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)
app = Flask(__name__)

def despertar_trabajador(nombre):
    print(f"⏰ Despertando al {nombre}...")
    return True

def ciclo_del_orquestador():
    print("\n--- CICLO DEL ORQUESTADOR INICIADO ---")
    try:
        # Lógica para revisar la base de datos y despertar workers...
        print("1. Revisando campañas pendientes...")
        response_campanas = supabase.table('campanas').select('*').eq('estado_campana', 'pendiente').limit(1).execute()
        if response_campanas.data:
            id_campana = response_campanas.data[0]['id']
            print(f"  -> Campaña pendiente encontrada (ID: {id_campana}). Activando Cazador.")
            supabase.table('campanas').update({'estado_campana': 'cazando'}).eq('id', id_campana).execute()
            despertar_trabajador("worker-cazador")
            return
        
        print("2. Revisando prospectos para analizar...")
        response_analizar = supabase.table('prospectos').select('prospecto_id', count='exact').eq('estado_prospecto', 'cazado').execute()
        if response_analizar.count > 0:
            print(f"  -> {response_analizar.count} prospectos listos. Despertando al Analista.")
            despertar_trabajador("worker-analista")
            return

        print("3. Revisando leads para persuadir...")
        response_persuadir = supabase.table('prospectos').select('prospecto_id', count='exact').eq('estado_prospecto', 'analizado_calificado').execute()
        if response_persuadir.count > 0:
            print(f"  -> {response_persuadir.count} leads listos. Despertando al Persuasor.")
            despertar_trabajador("worker-persuasor")
            return

        print("✅ No hay tareas nuevas.")

    except Exception as e:
        print(f"Error en el ciclo del Orquestador: {e}")
    
    print("--- CICLO DEL ORQUESTADOR FINALIZADO ---")

@app.route('/crear-campana', methods=['POST'])
def crear_nueva_campana():
    try:
        datos = request.get_json()
        nueva_campana = {
            'cliente_id': 1, 'nombre_campana': f"Campaña: {datos['cliente_ideal']}",
            'criterio_busqueda': json.dumps(datos), 'estado_campana': 'pendiente'
        }
        supabase.table('campanas').insert(nueva_campana).execute()
        return jsonify({"message": "Campaña creada con éxito."}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

def ciclo_continuo_orquestador():
    while True:
        ciclo_del_orquestador()
        print("\nOrquestador en modo de espera por 1 minuto...")
        time.sleep(60)

if __name__ == '__main__':
    orquestador_thread = Thread(target=ciclo_continuo_orquestador)
    orquestador_thread.daemon = True
    orquestador_thread.start()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
