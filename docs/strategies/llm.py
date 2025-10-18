from abc import ABC, abstractmethod
from openai import OpenAI

from utils.env import get_env


class PromptResponseStrategy(ABC):
    @abstractmethod
    def response(self, prompt: str) -> None:
        pass


class NvidiaResponse(PromptResponseStrategy):
    def response(self, prompt: str) -> None:
        client: OpenAI = OpenAI(
            base_url=get_env('NVIDIA_API_URL'),
            api_key=get_env('NVIDIA_API_SECRET')
        )

        completion = client.chat.completions.create(
            model=get_env('NVIDIA_API_MODEL'),
            messages=[{"role":"user","content":prompt}],
            temperature=0.2,
            top_p=0.7,
            max_tokens=8192,
            extra_body={"chat_template_kwargs": {"thinking":True}},
            stream=True
        )

        # Trocar para web socket
        for chunk in completion:
            choice = chunk.choices[0].delta
            reasoning = getattr(choice, "reasoning_content", None)
            content = getattr(choice, "content", None)
            if reasoning: print(reasoning, end="")
            if content: print(content, end="")