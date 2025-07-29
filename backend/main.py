
import base64
import os
import uuid
import modal
from pydantic import BaseModel
import requests

app = modal.App("HarmonAI")

image = (
    modal.Image.debian_slim()
    .apt_install("git")
    .pip_install_from_requirements("requirements.txt")
    .run_commands(["git clone https://github.com/ace-step/ACE-Step.git /tmp/ACE-Step", "cd /tmp/ACE-Step && pip install ."])
    .env({"HF_HOME": "/.cache/huggingface"})
    .add_local_python_source("prompts")
)

model_volume = modal.Volume.from_name(
    "ace-step-models", create_if_missing=True)
hf_volume = modal.Volume.from_name("qwen-hf-cache", create_if_missing=True)

secrets = modal.Secret.from_name("HarmonAI-AWS")



class GenerateMusicResponse(BaseModel):
    audio_data: str
    
@app.cls(
    image=image,
    secrets=[secrets],
    volumes={"/models": model_volume, "/.cache/huggingface": hf_volume},
    gpu="L40S",
    scaledown_window=15
)
class MusicGenServer:
    @modal.enter()
    def load_model(self):
        from acestep.pipeline.ace_step import ACEStepPipeline
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from diffusers import AutoPipelineForText2Image
        import torch
        # Load the ACE-Step model
        self.music_model = ACEStepPipeline(
            checkpoint_dir="/models",
            dtype="bfloat16",
            torch_compile=False,
            cpu_offload=False,
            overlapped_decode=False
        )
        # Load the tokenizer and model for text generation
        model_Id = "Qwen/Qwen2-7B-Instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(model_Id)
        self.llm_model = AutoModelForCausalLM.from_pretrained(
            model_Id,
            torch_dtype="auto",
            device_map="auto",
            cache_dir="/.cache/huggingface"
        )
        # Load the image generation model
        self.image_pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16", cache_dir="/.cache/huggingface")
        self.image_pipe.to("cuda")

    @modal.fastapi_endpoint(method="POST")
    def generate(self) -> GenerateMusicResponse:
        output_dir = "/tmp/output"
        os.mkdir(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{uuid.uuid4()}.wav")
        self.music_model(
            prompt="funk, pop, soul, rock, melodic, guitar, drums, bass, keyboard, percussion, 105 BPM, energetic, upbeat, groovy, vibrant, dynamic",
            lyrics="[verse]\nNeon lights they flicker bright\nCity hums in dead of night\nRhythms pulse through concrete veins\nLost in echoes of refrains\n\n[verse]\nBassline groovin' in my chest\nHeartbeats match the city's zest\nElectric whispers fill the air\nSynthesized dreams everywhere\n\n[chorus]\nTurn it up and let it flow\nFeel the fire let it grow\nIn this rhythm we belong\nHear the night sing out our song\n\n[verse]\nGuitar strings they start to weep\nWake the soul from silent sleep\nEvery note a story told\nIn this night we’re bold and gold\n\n[bridge]\nVoices blend in harmony\nLost in pure cacophony\nTimeless echoes timeless cries\nSoulful shouts beneath the skies\n\n[verse]\nKeyboard dances on the keys\nMelodies on evening breeze\nCatch the tune and hold it tight\nIn this moment we take flight",
            audio_duration=180,
            infer_step=60,
            guidance_scale=15,
            save_path=output_path,
        )

        with open(output_path, "rb") as f:
            audio_data = f.read()
        
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')

        os.remove(output_path)

        return GenerateMusicResponse(audio_data=audio_b64)


@app.local_entrypoint()
def main():
    server = MusicGenServer()
    endpoint_url = server.generate.get_web_url()
    print(f"Music generation endpoint URL: {endpoint_url}")
    response = requests.post(
        endpoint_url,
    )
    response.raise_for_status()
    result = GenerateMusicResponse(**response.json())
    audio_data = base64.b64decode(result.audio_data)
    output_file = "output.wav"
    with open(output_file, "wb") as f:
        f.write(audio_data)