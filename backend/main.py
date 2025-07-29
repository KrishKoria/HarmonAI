
import base64
import os
from typing import List
import uuid
import boto3
import modal
from pydantic import BaseModel
import requests

from prompts import LYRICS_GENERATOR_PROMPT, PROMPT_GENERATOR_PROMPT
from botocore.client import Config

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

class AudioGenerationBase(BaseModel):
    audio_duration: float = 180
    seed: int = -1
    guidance_scale: float = 15.0
    infer_step: int = 60
    instrumental: bool = False
    scheduler_type: str = "euler"
    cfg_type: str = "apg"
    omega_scale: float = 10.0
    guidance_interval: float = 0.5
    guidance_interval_decay: float = 0.0
    min_guidance_scale: float = 3.0
    use_erg_tag: bool = True
    use_erg_lyric: bool = True
    use_erg_diffusion: bool = True
    oss_steps: list = []


class GenerateFromDescriptionRequest(AudioGenerationBase):
    full_described_song: str


class GenerateWithCustomLyricsRequest(AudioGenerationBase):
    prompt: str
    lyrics: str


class GenerateWithDescribedLyricsRequest(AudioGenerationBase):
    prompt: str
    described_lyrics: str


class GenerateMusicResponseS3(BaseModel):
    s3_key: str
    cover_image_s3_key: str
    categories: List[str]


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
        self.music_model = ACEStepPipeline(
            checkpoint_dir="/models",
            dtype="bfloat16",
            torch_compile=False,
            cpu_offload=False,
            overlapped_decode=False
        )
        model_Id = "Qwen/Qwen2-7B-Instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(model_Id)
        self.llm_model = AutoModelForCausalLM.from_pretrained(
            model_Id,
            torch_dtype="auto",
            device_map="auto",
            cache_dir="/.cache/huggingface"
        )
        self.image_pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16", cache_dir="/.cache/huggingface")
        self.image_pipe.to("cuda")


    def prompt_qwen(self, question: str):
        messages = [
            {"role": "user", "content": question}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer(
            [text], return_tensors="pt").to(self.llm_model.device)

        generated_ids = self.llm_model.generate(
            model_inputs.input_ids,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True)[0]

        return response

    def generate_prompt(self, description: str):
        completed_prompt = PROMPT_GENERATOR_PROMPT.format(user_prompt=description)
        return self.prompt_qwen(completed_prompt)
    

    def generate_lyrics(self, description: str):
        generator_prompt = LYRICS_GENERATOR_PROMPT.format(description=description)
        return self.prompt_qwen(generator_prompt)
    
    def generate_categories(self, description: str) -> List[str]:
        prompt = f"Based on the following music description, list 3-5 relevant genres or categories as a comma-separated list. For example: Pop, Electronic, Sad, 80s. Description: '{description}'"

        response_text = self.prompt_qwen(prompt)
        categories = [cat.strip()
                      for cat in response_text.split(",") if cat.strip()]
        return categories
    
    def generate_and_upload_to_s3(
            self,
            prompt: str,
            lyrics: str,
            instrumental: bool,
            audio_duration: float,
            infer_step: int,
            guidance_scale: float,
            seed: int,
            description_for_categorization: str,
            scheduler_type: str,
            cfg_type: str,
            omega_scale: float,
            guidance_interval: float,
            guidance_interval_decay: float,
            min_guidance_scale: float,
            use_erg_tag: bool,
            use_erg_lyric: bool,
            use_erg_diffusion: bool,
            oss_steps: list
    ) -> GenerateMusicResponseS3:
        final_lyrics = "[instrumental]" if instrumental else lyrics
        print(f"Generated lyrics: \n{final_lyrics}")
        print(f"Prompt: \n{prompt}")

        s3_client = boto3.client("s3", endpoint_url='https://t3.storage.dev', config=Config(s3={'addressing_style': 'virtual'}))
        bucket_name = os.environ["S3_BUCKET_NAME"]

        output_dir = "/tmp/outputs"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{uuid.uuid4()}.wav")

        self.music_model(
            prompt=prompt,
            lyrics=final_lyrics,
            audio_duration=audio_duration,
            infer_step=infer_step,
            guidance_scale=guidance_scale,
            save_path=output_path,
            manual_seeds=str(seed),
            scheduler_type=scheduler_type,
            cfg_type=cfg_type,
            omega_scale=omega_scale,
            guidance_interval=guidance_interval,
            guidance_interval_decay=guidance_interval_decay,
            min_guidance_scale=min_guidance_scale,
            use_erg_tag=use_erg_tag,
            use_erg_lyric=use_erg_lyric,
            use_erg_diffusion=use_erg_diffusion,
            oss_steps=oss_steps
        )

        audio_s3_key = f"{uuid.uuid4()}.wav"
        s3_client.upload_file(output_path, bucket_name, audio_s3_key)
        os.remove(output_path)

        thumbnail_prompt = f"{prompt}, album cover art"
        image = self.image_pipe(
            prompt=thumbnail_prompt, num_inference_steps=2, guidance_scale=0.0).images[0]

        image_output_path = os.path.join(output_dir, f"{uuid.uuid4()}.png")
        image.save(image_output_path)

        image_s3_key = f"{uuid.uuid4()}.png"
        s3_client.upload_file(image_output_path, bucket_name, image_s3_key)
        os.remove(image_output_path)

        categories = self.generate_categories(description_for_categorization)

        return GenerateMusicResponseS3(
            s3_key=audio_s3_key,
            cover_image_s3_key=image_s3_key,
            categories=categories
        )
    
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
    
    @modal.fastapi_endpoint(method="POST")
    def generate_from_description(self, request: GenerateFromDescriptionRequest) -> GenerateMusicResponseS3:
        prompt = self.generate_prompt(request.full_described_song)
        lyrics = ""
        if not request.instrumental:
            lyrics = self.generate_lyrics(request.full_described_song)
        return self.generate_and_upload_to_s3(
            prompt=prompt,
            lyrics=lyrics,
            description_for_categorization=request.full_described_song,
            **request.model_dump(exclude={"full_described_song"})
        )

    @modal.fastapi_endpoint(method="POST")
    def generate_with_lyrics(self, request: GenerateWithCustomLyricsRequest) -> GenerateMusicResponseS3:
        return self.generate_and_upload_to_s3(prompt=request.prompt, lyrics=request.lyrics,
                                              description_for_categorization=request.prompt, **request.model_dump(exclude={"prompt", "lyrics"}))

    @modal.fastapi_endpoint(method="POST")
    def generate_with_described_lyrics(self, request: GenerateWithDescribedLyricsRequest) -> GenerateMusicResponseS3:
        lyrics = ""
        if not request.instrumental:
            lyrics = self.generate_lyrics(request.described_lyrics)
        return self.generate_and_upload_to_s3(prompt=request.prompt, lyrics=lyrics,
                                              description_for_categorization=request.prompt, **request.model_dump(exclude={"described_lyrics", "prompt"}))

@app.local_entrypoint()
def main():
    server = MusicGenServer()
    # endpoint_url = server.generate_from_description.get_web_url()
    # endpoint_url = server.generate_with_lyrics.get_web_url()
    endpoint_url = server.generate_with_described_lyrics.get_web_url()
    print(f"Music generation endpoint URL: {endpoint_url}")

    # request_data = GenerateFromDescriptionRequest(
    #     full_described_song="A funky rave track with a disco vibe, featuring groovy basslines and upbeat rhythms.",
    # )
#     request_data = GenerateWithCustomLyricsRequest(
#         prompt="A funky rave track with a disco vibe, featuring groovy basslines and upbeat rhythms.",
#         lyrics="""
# [verse]
# Woke up in a city that's always alive
# Neon lights they shimmer they thrive
# Electric pulses beat they drive
# My heart races just to survive

# [chorus]
# Oh electric dreams they keep me high
# Through the wires I soar and fly
# Midnight rhythms in the sky
# Electric dreams together we’ll defy

# [verse]
# Lost in the labyrinth of screens
# Virtual love or so it seems
# In the night the city gleams
# Digital faces haunted by memes

# [chorus]
# Oh electric dreams they keep me high
# Through the wires I soar and fly
# Midnight rhythms in the sky
# Electric dreams together we’ll defy

# [bridge]
# Silent whispers in my ear
# Pixelated love serene and clear
# Through the chaos find you near
# In electric dreams no fear

# [verse]
# Bound by circuits intertwined
# Love like ours is hard to find
# In this world we’re truly blind
# But electric dreams free the mind
# """,
#     )
    request_data = GenerateWithDescribedLyricsRequest(
        prompt="rave, disco, funky, upbeat, groovy, 140BPM, dance, energetic",
        described_lyrics="lyrics about a funky rave track with a disco vibe, featuring groovy basslines and upbeat rhythms.",
    )

    
    payload = request_data.model_dump()
    response = requests.post(
        endpoint_url,
        json=payload,
    )
    response.raise_for_status()
    result = GenerateMusicResponseS3(**response.json())
    # audio_data = base64.b64decode(result.audio_data)
    # output_file = "output.wav"
    # with open(output_file, "wb") as f:
    #     f.write(audio_data)
    print(f"Generated audio S3 key: {result.s3_key} {result.cover_image_s3_key} {result.categories}")