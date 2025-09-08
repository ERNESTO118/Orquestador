import os, time, json
from postgrest import PostgrestClient
from flask import Flask, request, jsonify
from threading import Thread

# --- INICIALIZACIÓN ---
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase = PostgrestClient(base_url=supabase_url, headers={"apikey": supabase_key})
app = Flask(__name__)

# --- CICLO DEL ORQUESTADOR ---
def ciclo_del_orquestador():
    while True:
        # ... (lógica del ciclo usando supabase.from_("tabla")...) ...
        print("Ciclo...")
        time.sleep(60)

# --- API PARA EL DASHBOARD ---
@app.route('/crear-campana', methods=['POST'])
def crear_nueva_campana():
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
