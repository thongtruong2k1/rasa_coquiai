import asyncio
import inspect
import wave
from sanic import Sanic, Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable, NoReturn
import numpy as np
from stt import Model

import TTS
from pathlib import Path
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer


import rasa.utils.endpoints
from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)

class CoquiAI(InputChannel):
    @classmethod
    def name(cls):
        print("Get Start")
        return "coquiai"

    def Speech2Text(self, audio_file_path, scorer, myModel, myScorer_path):
        if audio_file_path:
            acoustic_model, scorer_path = myModel, myScorer_path
            audio = wave.open(audio_file_path, 'r')
            audio_buffer = np.frombuffer(audio.readframes(audio.getnframes()), np.int16)
            if scorer:
                acoustic_model.enableExternalScorer(scorer_path)
                result = acoustic_model.stt(audio_buffer)
            else:
                acoustic_model.disableExternalScorer()
                result = acoustic_model.stt(audio_buffer)  
            return result  


    def Text2Speech(self, model_name='tts_models/en/ljspeech/tacotron2-DCA',
        vocoder_name=None,
        use_cuda=False):
        """TTS entry point for PyTorch Hub that provides a Synthesizer object to synthesize speech from a give text.
        Example:
            >>> synthesizer = torch.hub.load('coqui-ai/TTS', 'tts', source='github')
            >>> wavs = synthesizer.tts("This is a test! This is also a test!!")
                wavs - is a list of values of the synthesized speech.
        Args:
            model_name (str, optional): One of the model names from .model.json. Defaults to 'tts_models/en/ljspeech/tacotron2-DCA'.
            vocoder_name (str, optional): One of the model names from .model.json. Defaults to 'vocoder_models/en/ljspeech/multiband-melgan'.
            pretrained (bool, optional): [description]. Defaults to True.
        Returns:
            TTS.utils.synthesizer.Synthesizer: Synthesizer object wrapping both vocoder and tts models.
        """
        manager = ModelManager()

        model_path, config_path, model_item = manager.download_model(model_name)
        vocoder_name = model_item[
            'default_vocoder'] if vocoder_name is None else vocoder_name
        vocoder_path, vocoder_config_path, _ = manager.download_model(vocoder_name)

        # create synthesizer
        synt = Synthesizer(tts_checkpoint=model_path,
                        tts_config_path=config_path,
                        vocoder_checkpoint=vocoder_path,
                        vocoder_config=vocoder_config_path,
                        use_cuda=use_cuda)
        return synt


    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:

        custom_webhook = Blueprint(
            "custom_webhook_{}".format(type(self).__name__),
            inspect.getmodule(self).__name__,
        )

        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            sender_id = request.json.get("sender") # method to get sender_id 
            text = request.json.get("message") # method to fetch text
            input_channel = self.name() # method to fetch input channel
            metadata = self.get_metadata(request) # method to get metadata
            collector = CollectingOutputChannel()
            await on_new_message(
                UserMessage(
                    text,
                    collector,
                    sender_id,
                    input_channel = input_channel
                )
            )
            
            return response.json(collector.messages)


        @custom_webhook.route("/STT", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:

            appConfig = "./channel/file_data"
            # 22000 seem good
            samplerate = 21000
            # A note on the left channel for 1 second.  

            with wave.open(f"{appConfig}/s2.wav", "wb") as f:
                # 2 Channels.
                f.setnchannels(1)
                # 2 bytes per sample.
                f.setsampwidth(2)
                f.setframerate(samplerate)
                f.writeframes(request.files["file_audio"][0].body)

            # Audio 2 Text
            en_stt_model_path = "C:\AntBuddy\AntBot-Rasa\model_coqui\STT\model.tflite"
            en_stt_scorer_path = "C:\AntBuddy\AntBot-Rasa\model_coqui\STT\huge-vocabulary.scorer"
            
            myModel = Model(en_stt_model_path) 
            myScorer_path = en_stt_scorer_path

            audio_path = r"C:\Users\Admin\Postman\files\s1.wav"
            text = self.Speech2Text(audio_path, True, myModel, myScorer_path)

            # Get Bot's Answer

            text = text
            collector = CollectingOutputChannel()
            
            # include exception handling
            await on_new_message(
                UserMessage(
                    text,
                    collector,
                )
            )

            response_ = collector.messages
            print(response_)
            text_response = response_[0]['text']
            
            file_name = 'test_tts.wav'

            synthesizer = self.Text2Speech('tts_models/en/ljspeech/tacotron2-DDC', 'vocoder_models/en/ljspeech/hifigan_v2')
            wav = synthesizer.tts(text_response)
            synthesizer.save_wav(wav, file_name)
            print("\nDone TTS\n")
            location = r'C:/AntBuddy/AntBot-Rasa'
            return await response.file(f"{location}/{file_name}")


        return custom_webhook