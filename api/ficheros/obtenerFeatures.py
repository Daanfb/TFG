from threading import Thread

from obtenerAudio import vid2mel
from obtenerFR import extraeFR

class CustomThread(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)
        self.result = None

    def run(self):
        if self._target is not None:
            self.result = self._target(*self._args, **self._kwargs)

    def join(self):
        Thread.join(self)
        return self.result

def features(video_path):
    
    # Crea hilos para ejecutar las dos funciones simultáneamente
    t1 = CustomThread(target=extraeFR, args=(video_path,))
    t2 = CustomThread(target=vid2mel, args=(video_path,))
    
    # Inicia los hilos
    t1.start()
    t2.start()
    
    # Espera a que los hilos terminen
    features_resnet = t1.join()
    features_audio = t2.join()

    print(f"Features de {video_path} extraídos")

    return features_resnet, features_audio