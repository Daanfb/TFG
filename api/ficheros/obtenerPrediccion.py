from dataset import TestDataset
from runModel import testSpotting
import torch
import yaml
import torch
from model import ASTRA
import numpy as np
from obtenerFeatures import features
import os

# Variable global para almacenar el modelo cargado y el archivo de configuración
model_astra = None
cfg = None

def load_model_astra():
    global model_astra
    global cfg

    ruta_directorio_actual = os.path.dirname(os.path.abspath(__file__))

    if model_astra is None:
        with open (ruta_directorio_actual + '/ASTRA.yaml', 'r') as f:
            cfg = yaml.load(f, Loader = yaml.FullLoader)

        model_astra = ASTRA(chunk_size = cfg['chunk_size'], n_output = int(cfg['outputrate'] * cfg['chunk_size']), resnet = cfg['resnet'], 
                        audio = cfg['audio'], model_cfg = cfg['model'])
        
        weights = torch.load(ruta_directorio_actual + '/model.pth.tar')
        model_astra.load_state_dict(weights, strict = False)
        
    return model_astra

def generar_json(video_path):
    model = load_model_astra().cuda()

    try:
        featR, featA = features(video_path)
    except Exception as e:
        return "Error al obtener las features", e
    
    try:
        dataset_test  = TestDataset(featR = featR, featA = featA, 
                        outputrate = cfg['outputrate'], chunk_size = cfg['chunk_size'], 
                        resnet = cfg['resnet'], audio = cfg['audio'])

        test_loader = torch.utils.data.DataLoader(dataset_test, batch_size = 1, shuffle = False, pin_memory = True)

        name_experiment = os.path.splitext(video_path)[0].replace('videos/', 'json/')

        print(f"Obteniendo el JSON de {video_path}")
        testSpotting(test_loader, model = model, model_name = "ASTRA", name_experiment=name_experiment,  NMS_threshold = cfg['NMS_threshold'], 
                                outputrate = cfg['outputrate'], chunk_size = cfg['chunk_size'], path_experiments = cfg['path_experiments'],)
    
        print(f"JSON de {video_path} obtenido")

        return name_experiment + '.json'

    except Exception as e:
        return "Error al obtener la predicción", e