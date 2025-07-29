
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
        from acestep.pipeline_ace_step import ACEStepPipeline
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
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{uuid.uuid4()}.wav")
        self.music_model(
            prompt= "electronic rap",
            lyrics= "[verse]\nWaves on the bass, pulsing in the speakers,\nTurn the dial up, we chasing six-figure features,\nGrinding on the beats, codes in the creases,\nDigital hustler, midnight in sneakers.\n\n[chorus]\nElectro vibes, hearts beat with the hum,\nUrban legends ride, we ain't ever numb,\nCircuits sparking live, tapping on the drum,\nLiving on the edge, never succumb.\n\n[verse]\nSynthesizers blaze, city lights a glow,\nRhythm in the haze, moving with the flow,\nSwagger on stage, energy to blow,\nFrom the blocks to the booth, you already know.\n\n[bridge]\nNight's electric, streets full of dreams,\nBass hits collective, bursting at seams,\nHustle perspective, all in the schemes,\nRise and reflective, ain't no in-betweens.\n\n[verse]\nVibin' with the crew, sync in the wire,\nGot the dance moves, fire in the attire,\nRhythm and blues, soul's our supplier,\nRun the digital zoo, higher and higher.\n\n[chorus]\nElectro vibes, hearts beat with the hum,\nUrban legends ride, we ain't ever numb,\nCircuits sparking live, tapping on the drum,\nLiving on the edge, never succumb.",
            audio_duration= 221.42547916666666,
            infer_step= 60,
            guidance_scale= 15,
            scheduler_type= "euler",
            cfg_type= "apg",
            omega_scale= 10,
            guidance_interval= 0.5,
            guidance_interval_decay= 0,
            min_guidance_scale= 3,
            use_erg_tag= True,
            use_erg_lyric= True,
            use_erg_diffusion= True,
            oss_steps= [],
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