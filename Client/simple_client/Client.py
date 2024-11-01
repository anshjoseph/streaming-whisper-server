# from WhisperLive import BasicWhisperClient
import numpy as np
import pyaudio
import logging
import gzip
from uuid import uuid4
import numpy as np
import threading
import json
import websocket
import uuid
from queue import Queue
from websockets.exceptions import *
import time
time_speech = 0
class BasicWhisperClient:
    def __init__(self,host:str, port:int, model:str) -> None:
        self.ws_url =  f"ws://{host}:{port}"
        self.ws_connection:websocket.WebSocket = websocket.WebSocket()
        self.ws_connection.connect(self.ws_url)
        self.client_id:str = str(uuid.uuid4())
        self.retrive_token= None
        self.recever_task = None
        self.model = model


        self.commited_list:list[str] = []



        self.prev_segment = None
        self.curr_segment = None
        self.seg_ptr = 0
        self.same_data_count = 0


        self.segments_collection_thread:threading.Thread = threading.Thread(target=self.get_segment) 

        self.segments:Queue = Queue()
    def MakeConnectionToServer(self):
        self.ws_connection.send(json.dumps(
            {
                "uid": str(uuid.uuid4()),
                "language": "en",
                "task": "transcribe",
                "model": self.model,
                "use_vad": True
            }
        ))
        self.retrive_token = json.loads(self.ws_connection.recv())
        self.segments_collection_thread.start()

    def __check_server_status(self):
        if self.retrive_token == None:
            return False
        elif self.retrive_token["message"] == "SERVER_READY":
            return True
        return False
    
    def send_data_chunk(self,chunk:bytes):
        print("send the chunk")
        self.ws_connection.send(chunk,websocket.ABNF.OPCODE_BINARY)
    

    def CloseConnectionToServer(self):
        self.ws_connection.close()
    
    def SendEOS(self):
        self.ws_connection.send(b'END_OF_AUDIO',websocket.ABNF.OPCODE_BINARY)
        return self.ws_connection.recv()
    
    def SendEnd(self):
        self.SendEOS()
        self.CloseConnectionToServer()
    
    


        
    
    def get_segment(self):
        while True:
            try:
                print("receverd some thing")
                __data = self.ws_connection.recv()
                print(__data)
                data:dict = json.loads(__data)
                print(data)
                if "message" not in data:
                    # self.segments.put(data)
                   
                    # print(data)
                    print(time_speech)
                else:
                    print(data)
                    if data['message'] == 'DISCONNECT':
                        self.ws_connection.close()
                        # self.onDisconnect()
                        break
                    elif data['message'] == "UTTERANCE_END":
                        if self.prev_segment != None:
                            if len(self.prev_segment) > 0:
                                self.prev_segment[-1]['is_final'] = True
                        # note make this changes
                    elif data['message'] == 'SERVER_READY':
                        print("server id ready")
                    

            except Exception as e:
                import traceback
                print(traceback.format_exc())
                print(f"rcever stoped {e}")
                break
    
         
    

    def onTranscript(self,segment:dict):
        print(f"TRANSCRIPT: {segment}")


class Client(BasicWhisperClient):
    def __init__(self, host: str, port: int) -> None:
        super().__init__(host, port, "whisper_tiny_ct")
    def onTranscript(self, segment: dict):
        super().onTranscript(segment)
        print(segment)

client = Client("127.0.0.1",9001)
client.MakeConnectionToServer()
print(client.retrive_token)


def bytes_to_float_array(audio_bytes):
    raw_data = np.frombuffer(buffer=audio_bytes, dtype=np.int16)
    return raw_data.astype(np.float32) / 32768.0

chunk = 8192
format = pyaudio.paInt16
channels = 1
rate = 16000
record_seconds = 60000
frames = b""

p = pyaudio.PyAudio()

stream = p.open(
            format=format,
            channels=channels,
            rate=rate,
            input=True,
            frames_per_buffer=chunk
        )
try:
    for _ in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk, exception_on_overflow=False)
        audio_array = bytes_to_float_array(data)
        try:
            if _%10 == 0:
                print("sleep")
                # time.sleep(5)
            data = audio_array.tobytes()
            comp = gzip.compress(data)
            print((len(comp)/len(data))*100)
            time_speech += chunk/rate 
            client.send_data_chunk(comp)
        except Exception as e:
            print(e)
            break

except KeyboardInterrupt:
    print(client.SendEOS())