
import modal

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
