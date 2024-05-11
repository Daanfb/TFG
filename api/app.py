from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import uuid
import os

import sys

if os.path.exists('/app'):
    sys.path.append('/app/ficheros')
    from obtenerPrediccion import generar_json
    from cortarVideo import MiVideo
else:
    from ficheros.obtenerPrediccion import generar_json
    from ficheros.cortarVideo import MiVideo

app = Flask(__name__)
CORS(app)

RUTA_VIDEOS = os.getcwd() + "/videos/"

@app.route('/')
def hello_world():
    print('Hello World')
    return 'Hello World'

@app.route('/subir_video', methods=['POST'])
def subir_video():

    print("Obteniendo video...")

    # Obtenemos el video del request
    video = request.files['video']

    # Guardamos el video en el servidor con un nombre aleatorio
    video_id = str(uuid.uuid4())
    ruta_video = RUTA_VIDEOS + video_id + os.path.splitext(video.filename)[1]
    video.save(ruta_video)

    print('Video guardado en:', ruta_video)
    
    respuesta = {'ruta_video': ruta_video}
    return jsonify(respuesta)


@app.route('/procesar_video', methods=['POST'])
def procesar_video():

    # Obtenemos la ruta del video en el servidor
    ruta_video = request.form.get('ruta_video')

    print('Procesando video:', ruta_video)

    try:
        ruta_json = generar_json(ruta_video)
        print(f"Procesamiento de video {ruta_video} finalizado")
        respuesta = {'ruta_json': ruta_json}

    except Exception as e:
        print(f"Error al procesar el video {ruta_video}:", e)
        respuesta = {'error': e}

    return jsonify(respuesta)

@app.route('/obtener_video_highlights', methods=['POST'])
def obtener_video_highlights():
    acciones_seleccionadas = request.form.get('acciones_seleccionadas')
    ruta_video = request.form.get('ruta_video')
    ruta_json = request.form.get('ruta_json')

    print("Acciones seleccionadas:", acciones_seleccionadas)
    print("Generando highlights de:", ruta_video)
    print("Usando JSON:", ruta_json)

    try:
        mi_video = MiVideo(ruta_json, acciones_seleccionadas, ruta_video)
        ruta_highlights = mi_video.cortar_video()

        if ruta_highlights is None:
            respuesta = {'vacio': 'Video vacio'}
            respuesta = jsonify(respuesta)
    
        else:
            if ruta_highlights.endswith('.mkv'):
                mimetype = 'video/x-matroska'
            else:
                mimetype = 'video/mp4'

            print('Highlights guardados en:', ruta_highlights)

            respuesta = send_file(ruta_highlights, as_attachment=True, mimetype=mimetype)

    except Exception as e:
        print(f"Error al generar highlights de {ruta_video}:", e)
        respuesta = jsonify({'error': e})

    return respuesta

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)