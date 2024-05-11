import time
from tqdm import tqdm
import numpy as np
from SoccerNet.Evaluation.utils import AverageMeter, INVERSE_EVENT_DICTIONARY_V2
from torch import autocast
import json
from dataset import feats2clip
import os
import torch



def testSpotting(dataloader, model, model_name, name_experiment, NMS_window = 8, NMS_threshold=0.5, outputrate=2, chunk_size=32, stride = 8, postprocessing = 'SNMS', path_experiments = None):

    """
    Function for inference of the action spotting model (and evaluation)
    """

    spotting_predictions = list()

    model.eval()
    
    primer_partido = next(iter(dataloader))

    # Iterate over games (dataloader)
    data = primer_partido

    if model.resnet:
        featR = data['featR'].reshape(-1, data['featR'].shape[-1])

        # Tomamos los segundos que tiene las features (primera dimension)
        sec = featR.shape[0]

        # Dividimos las features en clips de duración chunk_size=32, con un stride (superposicion) de 8
        featR = feats2clip(featR, stride = stride, clip_length = chunk_size)

        # Número de clips
        lenR = len(featR)

    if model.audio:
        featA = data['featA'].reshape(-1, data['featA'].shape[-1])
        featA = feats2clip(featA.T, stride = stride * 50, clip_length = chunk_size * 100)

    #batch size for testing
    BS = 4

    json_data = dict()
    json_data["predictions"] = list()

    #HALF 1 PREDICTIONS
    featV = []
            
    #Initialize half1 preds
    timestamp_long = np.zeros((sec * outputrate, 17))
    q = 0

    # Recorremos cada clip y se lo pasamos al modelo de BS en BS (es decir, de 4 en 4)
    for b in tqdm(range(lenR)):
        if (b % BS == 0) | (b == lenR-1):
            if b != 0:
                # Tomamos BS clips
                featR_input = featR[b-q:b].clone().cuda()
                if model.audio:
                    featA_input = featA[b-q:b].clone().cuda()

                else:
                    featA = None

                with autocast(device_type='cuda', dtype=torch.float16):
                    with torch.no_grad():
                        output = model(featsR = featR_input, featsA = featA_input, inference = True)

                predC = output['preds'].cpu().detach().numpy()
                if model.model_cfg['uncertainty']:
                    predD = output['predsD'][:, :, :, 0].cpu().detach().numpy()
                else:
                    predD = output['predsD'].cpu().detach().numpy()
                batch, nf, nc = predC.shape
                for l in range(batch):
                    initial_pos = (b - len(predC) + l) * stride * outputrate
                    for j in range(nf):
                        for k in range(nc-1):
                            prob = predC[l, j, k+1]
                            if prob > NMS_threshold:
                                rel_position = j - predD[l, j, k+1]
                                position = min(len(timestamp_long)-1, max(0, int((initial_pos + rel_position).round())))
                                timestamp_long[position, k] = max(timestamp_long[position, k], prob)
                        
                q = 0

        q += 1
                
    spotting_predictions.append(timestamp_long)
            
    if postprocessing == 'NMS':
        get_spot = get_spot_from_NMS
        nms_window = [NMS_window] * 17

    elif postprocessing == 'SNMS':
        get_spot = get_spot_from_SNMS
        nms_window = [5, 7, 9, 12, 10, 14, 14, 5, 8, 8, 8, 8, 13, 5, 6, 6, 6]
    
    json_data = dict()
    json_data["predictions"] = list()

    timestamp = timestamp_long
    half = 0
                        
    for l in range(dataloader.dataset.num_classes):
        spots = get_spot(
            timestamp[:, l], window=nms_window[l]*outputrate, thresh=NMS_threshold)

        for spot in spots:
            frame_index = int(spot[0])
            confidence = spot[1]
            
            if confidence >= 0.4:

                seconds = int((frame_index//outputrate)%60)
                minutes = int((frame_index//outputrate)//60)

                prediction_data = dict()
                prediction_data["gameTime"] = str(half+1) + " - " + str(minutes) + ":" + str(seconds)

                prediction_data["label"] = INVERSE_EVENT_DICTIONARY_V2[l]

                prediction_data["position"] = str(int((frame_index/outputrate)*1000))
                prediction_data["confidence"] = str(confidence)
                json_data["predictions"].append(prediction_data)
    
    with open(f"{name_experiment}.json", 'w') as output_file:
        json.dump(json_data, output_file, indent=4)

def get_spot_from_NMS(Input, window, thresh=0.0, min_window=0):
    """
    Non-Maximum Suppression
    """
    detections_tmp = np.copy(Input)
    # res = np.empty(np.size(Input), dtype=bool)
    indexes = []
    MaxValues = []
    while(np.max(detections_tmp) >= thresh):
        
        # Get the max remaining index and value
        max_value = np.max(detections_tmp)
        max_index = np.argmax(detections_tmp)
                        
        # detections_NMS[max_index,i] = max_value
        
        nms_from = int(np.maximum(-(window/2)+max_index,0))
        nms_to = int(np.minimum(max_index+int(window/2), len(detections_tmp)))
                            
        if (detections_tmp[nms_from:nms_to] >= thresh).sum() > min_window:
            MaxValues.append(max_value)
            indexes.append(max_index)
        detections_tmp[nms_from:nms_to] = -1
        
    return np.transpose([indexes, MaxValues])

def get_spot_from_SNMS(Input, window, thresh=0.0, decay = 'pow2'):
    """
    Soft Non-Maximum Suppression
    """
    detections_tmp = np.copy(Input)

    indexes = []
    MaxValues = []
    while(np.max(detections_tmp) >= thresh):

        # Get the max remaining index and value
        max_value = np.max(detections_tmp)
        max_index = np.argmax(detections_tmp)

        nms_from = int(np.maximum(-(window/2)+max_index,0))
        nms_to = int(np.minimum(max_index+int(window/2), len(detections_tmp)-1)) + 1

        MaxValues.append(max_value)
        indexes.append(max_index)

        if decay == 'linear':
            weight = np.abs(np.arange(nms_from - max_index, nms_to - max_index)) / (window / 2)
        elif decay == 'sqrt':
            weight = np.sqrt(np.abs(np.arange(nms_from - max_index, nms_to - max_index))) / np.sqrt(window / 2)
        elif decay == 'pow2':
            weight = np.power(np.abs(np.arange(nms_from - max_index, nms_to - max_index)), 2) / np.power(window / 2, 2)

        detections_tmp[nms_from:nms_to] = detections_tmp[nms_from:nms_to] * weight
        detections_tmp[nms_from:nms_to][detections_tmp[nms_from:nms_to] < thresh] = -1


    return np.transpose([indexes, MaxValues])