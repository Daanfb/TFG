import torch
from torch.utils.data import Dataset
from SoccerNet.Evaluation.utils import EVENT_DICTIONARY_V2

class TestDataset(Dataset):
    """
    Dataset class for SoccerNet (inference / testing)
    """

    def __init__(self, featR, featA, outputrate=2, chunk_size=4, resnet=True, audio = True):
        
        self.featR = featR
        self.featA = featA

        self.outputrate = outputrate
        self.chunk_size = chunk_size
        self.resnet = resnet
        self.audio = audio
        
        self.stride = 1 / outputrate

        self.dict_event = EVENT_DICTIONARY_V2
        self.num_classes = 17

    def __getitem__(self, index):

        data = dict()

        if self.resnet:
            data['featR'] = self.featR
            
        if self.audio:
            data['featA'] = self.featA

        return data

    def __len__(self):
        return 1

def feats2clip(feats, stride, clip_length, padding = "replicate_last", off=0):
    """
    Auxiliar function to split video features into clips
    """

    idx = torch.arange(start=0, end=feats.shape[0]-1, step=stride)
    idxs = [] # Almacena los índices de los clips
    for i in torch.arange(-off, clip_length-off):
    # for i in torch.arange(0, clip_length):
        idxs.append(idx+i)
    idx = torch.stack(idxs, dim=1)     # Para feats.shape = (2700, 8576) devuelve (108,50)

    if padding=="replicate_last":
        idx = idx.clamp(0, feats.shape[0]-1)
        # Not replicate last, but take the clip closest to the end of the video
        # idx[-1] = torch.arange(clip_length)+feats.shape[0]-clip_length

    return feats[idx,...]