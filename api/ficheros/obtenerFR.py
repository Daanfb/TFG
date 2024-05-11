from tensorflow import keras
from tensorflow.keras.models import Model
from tensorflow.keras.applications.resnet import preprocess_input
from SoccerNet.DataLoader import FrameCV
import numpy as np
import pickle as pkl
import os

from tensorflow.keras.utils import Sequence

# Variable global para almacenar el modelo cargado
loaded_model = None

# Variable global para almacenar el average
average = None

# Variable global para almacenar el pca
pca = None

class DataGenerator(Sequence):
    def __init__(self, x_set, batch_size):
        self.x = x_set
        self.batch_size = batch_size

    def __len__(self):
        return int(np.ceil(len(self.x) / float(self.batch_size)))

    def __getitem__(self, idx):
        batch_x = self.x[idx * self.batch_size:(idx + 1) * self.batch_size]
        return batch_x

def load_model():
    global loaded_model
    if loaded_model is None:
        # Cargar el modelo solo si no está cargado
        base_model = keras.applications.resnet.ResNet152(include_top=True,
                                                         weights='imagenet',
                                                         input_tensor=None,
                                                         input_shape=None,
                                                         pooling=None,
                                                         classes=1000)
        model = Model(base_model.input,
                      outputs=[base_model.get_layer("avg_pool").output])
        model.trainable = False
        loaded_model = model
        
    return loaded_model

def load_PCA():
    global pca
    global average

    ruta_directorio_actual = os.path.dirname(os.path.abspath(__file__))
    
    if pca is None:
        with open(ruta_directorio_actual + "/pca_512_TF2.pkl", "rb") as fobj:
            pca = pkl.load(fobj)
            
    if average is None:
        with open(ruta_directorio_actual + "/average_512_TF2.pkl", "rb") as fobj:
            average = pkl.load(fobj)
            
    return pca, average

def extraeFR(video_path):

    # Cargar el modelo
    model = load_model()
    
    # Cargar los archivos de pca y average
    pca, average = load_PCA()

    videoLoader = FrameCV(video_path, FPS=1.0, transform="crop", start=None, duration=None)

    # Si el alto es 225 elimina una columna para que los frames sean 224x224
    if videoLoader.frames.shape[2] == 225:
        videoLoader.frames = videoLoader.frames[:,:,:-1,:]

    print(f"Preprocesando video {video_path}")
    frames = preprocess_input(videoLoader.frames)

    framesGen = DataGenerator(frames, batch_size=8)
    
    print("Extrayendo features visuales...")
    features = model.predict(framesGen, batch_size=8, verbose=1)
    print(f"Features visuales de video {video_path} extraídos")

    features = features - average
    features = pca.transform(features)

    return features