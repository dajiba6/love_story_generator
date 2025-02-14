import requests
from typing import Dict, Any


class AIClient:
    def __init__(self, config: Dict[str, Any]):
        self.provider = config["provider"]
        self.config = config[self.provider]  # 获取对应提供商的配置

    def generate(self, prompt: str) -> str:
        """Generate text using configured AI provider"""
        print(f"Using {self.provider} to generate...")

        generators = {
            "openai": self._generate_with_openai,
            "ollama": self._generate_with_ollama,
        }

        if self.provider not in generators:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

        return generators[self.provider](prompt)

    def _generate_with_openai(self, prompt: str) -> str:
        """Generate text using OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.config["model"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 2000),
        }

        response = requests.post(
            f"{self.config['base_url']}/v1/chat/completions", headers=headers, json=data
        )
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]

    def _generate_with_ollama(self, prompt: str) -> str:
        """Generate text using Ollama API"""
        data = {
            "model": self.config["model"],
            "prompt": prompt,
            "temperature": self.config.get("temperature", 0.5),
            "stream": False,
        }

        response = requests.post(f"{self.config['base_url']}/api/generate", json=data)
        response.raise_for_status()

        return response.json()["response"]
