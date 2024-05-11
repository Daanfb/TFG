import json
from moviepy.editor import VideoFileClip, concatenate_videoclips
from tqdm import tqdm
import os
import numpy as np

class MiVideo():

    def __init__(self, json, acciones, ruta_video):
        
        # Diccionario de acciones de español a inglés
        dicc_esp_ingles = {
            'Gol': 'Goal',
            'Tiro a puerta': 'Shots on target',
            'Tiro que no va a puerta': 'Shots off target',
            'Falta': 'Foul',
            'Lanzamiento de falta directa': 'Direct free-kick',
            'Lanzamiento de falta indirecta': 'Indirect free-kick',
            'Fuera de juego': 'Offside',
            'Despeje': 'Clearance',
            'Lanzamiento de corner': 'Corner',
            'Penalti': 'Penalty',
            'Sustitución': 'Substitution',
            'Saque desde el centro del campo': 'Kick-off',
            'Primera tarjeta amarilla': 'Yellow card',
            'Segunda tarjeta amarilla': 'Yellow->red card',
            'Tarjeta roja': 'Red card',
            'Saque de banda': 'Throw-in',
            'Balón fuera': 'Ball out of play'
        }

        
        self.json = json
        acciones = acciones.split(",") if isinstance(acciones, str) else acciones
        self.acciones = [dicc_esp_ingles[accion.strip()] for accion in acciones]
        self.ruta_video = ruta_video
        
    def _calculo_predicciones(self, data):
        lista_acciones_agrupadas = []
        limite = 60
        
        # Añado los grupos de las acciones que se quieren buscar
        for accion in self.acciones:
            
            # Me quedo con los 40 elementos con más confianza de dicha accion
            elementos = [e for e in data if e['label']==accion]
            elementos.sort(key=lambda e:e['confidence'], reverse=True)
            elementos = elementos[:40]
            
            # Lista que contendrá listas con los elementos que sean cercanos en tiempo
            lista_grupos = []
            
            # Recorro los elementos y los agrupo en listas si están cerca en tiempo
            for e in elementos:
                tiempo = int(e['position'])
                
                lista_seleccionada = -1
                for i in range(len(lista_grupos)):
                    menor_tiempo = int(min(lista_grupos[i], key=lambda x: int(x['position']))['position'])
                    mayor_tiempo = int(max(lista_grupos[i], key=lambda x: int(x['position']))['position'])
                    
                    # Si el tiempo de la accion actual está a menos de 60seg de alguno de los elementos del grupo
                    if abs(menor_tiempo - tiempo)<=(limite*1000) or abs(mayor_tiempo-tiempo)<=(limite*1000):
                        lista_seleccionada = i
                        break
                
                if lista_seleccionada==-1:
                    lista_grupos.append([e])
                else:
                    lista_grupos[lista_seleccionada].append(e)
    
            # Minimo numero de elementos de debe haber en el grupo para ser seleccionado
            longitudes = [len(l) for l in lista_grupos]
            minimo_elementos = np.mean(longitudes) + np.std(longitudes)

            # Si el grupo tiene más elementos que el minimo, lo añado a la lista de grupos
            for l in lista_grupos:
                if len(l)>=minimo_elementos:
                    lista_acciones_agrupadas.append(l)

        # Una vez tengo los grupos de las acciones, calculo el tiempo medio de cada grupo
        lista_res = []
        for l in lista_acciones_agrupadas:
            position = int(sum(int(e['position']) for e in l)/len(l))
            segundos_totales = position//1000
            minutos = segundos_totales//60
            segundos = segundos_totales%60
            gameTime = f"{minutos}:{segundos}"
            label = l[0]['label']

            lista_res.append({'gameTime': gameTime, 'label': label, 'position': position})

        # Ordeno la lista por el tiempo de la accion
        lista_res.sort(key=lambda x: x['position'])
        
        return lista_res

    def cortar_video(self):

        # Cargamos el video
        video = VideoFileClip(self.ruta_video)

        # Cargamos el json
        with open(self.json, 'r') as f:
            data = json.load(f)['predictions']

        # Calculamos las predicciones
        predicciones = self._calculo_predicciones(data)
        predicciones_restantes = len(predicciones)

        # Lista para almacenar los clips
        clips_combinados = []

        saltar_accion = False

        # Iteramos sobre cada par de predicciones consecutivas
        for prediccion_actual, prediccion_siguiente in tqdm(zip(predicciones, predicciones[1:]), total=len(predicciones)):
            
            predicciones_restantes -= 1

            # Si saltar_accion es True, se salta la iteracion actual
            if saltar_accion:
                saltar_accion = False
                continue

            # Obtener los datos de la prediccion actual
            tiempo_actual = prediccion_actual['gameTime']
            minuto_actual, segundos_actual = map(int, tiempo_actual.split(":"))
                
            # Calculamos los segundos de inicio y fin de la acción actual
            start_time_actual = max(0, minuto_actual*60+segundos_actual-4)  # 4 segundos antes del instante de la accion 1
            end_time_actual = min(video.duration, minuto_actual*60+segundos_actual+4)  # 4 segundos despues del instante de la accion 1

            # Obtenemos los datos de la predicción siguiente
            tiempo_siguiente = prediccion_siguiente['gameTime']
            minuto_siguiente, segundos_siguiente = map(int, tiempo_siguiente.split(":"))

            # Calculamos los segundos de inicio y fin de la accion siguiente
            start_time_siguiente = max(0, minuto_siguiente*60+segundos_siguiente-4)  # 4 segundos antes del instante de la accion 2
            end_time_siguiente = min(video.duration, minuto_siguiente*60+segundos_siguiente+4)  # 4 segundos despues del instante de la accion 2

            # Las acciones se superponen (con una diferencia de 3 segundos o menos)
            if end_time_actual - start_time_siguiente >= -3:
                start_time = start_time_actual
                end_time = end_time_siguiente
                saltar_accion = True
            else:
                start_time = start_time_actual
                end_time = end_time_actual

            # Cortamos el video para el segmento actual y añadimos el clip a la lista
            clip = video.subclip(start_time, end_time)
            clips_combinados.append(clip)

        if predicciones_restantes != 0:
            # Obtenemos los datos de la última predicción
            prediccion = predicciones[-1]
            tiempo = prediccion['gameTime']
            minuto, segundos = map(int, tiempo.split(":"))

            # Calculamos los segundos de inicio y fin de la acción
            start_time = max(0, minuto*60+segundos-4)
            end_time = min(video.duration, minuto*60+segundos+4)

            # Cortamos el video para el segmento actual y añadimos el clip a la lista
            clip = video.subclip(start_time, end_time)
            clips_combinados.append(clip)

        if len(clips_combinados)==0:
            return None
        
        # Concatenamos todos los clips en uno solo
        video_combinado = concatenate_videoclips(clips_combinados)

        # Creamos la ruta del video combinado
        nombre_video, extension = os.path.splitext(self.ruta_video)
        ruta_video_combinado = nombre_video + "_highlights" + extension
        ruta_video_combinado = ruta_video_combinado.replace("videos", "highlights")

        # Guardamos el video combinado
        video_combinado.write_videofile(ruta_video_combinado, codec="libx264", audio_codec="mp3")
            
        # Cierra los videos
        video.close()
        video_combinado.close()

        return ruta_video_combinado
