from .demucs import Demucs
import torch
from uuid import uuid4
from WhisperLive.logger_config import configure_logger
import torchaudio
import numpy as np
from WhisperLive.whisper_live.vad import VoiceActivityDetector
logger = configure_logger(__name__)


class BasicInferenceMechanism:
    def __init__(self,model:Demucs) -> None:
        self.model:Demucs = model
        self.vad = VoiceActivityDetector(0.6)
        self.model_id:str = str(uuid4())
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        logger.info(f"BasicInferenceMechanism with model id: {self.model_id} loaded, detected device {self.device}")
        self.model.to(self.device)
    def __call__(self, audio:np.ndarray) -> np.ndarray:
        if self.vad(audio):
            audio = audio.reshape((1,audio.shape[0])).copy()
            audio = torch.from_numpy(audio).to(self.device)
            with torch.no_grad():
                output:torch.Tensor = self.model(audio[None])[0]
            return output.cpu().detach().numpy()
        return np.array([])
