from abc import ABC, abstractmethod
from openai import AsyncOpenAI

from utils.env import get_env


class PromptResponseStrategy(ABC):
    @abstractmethod
    def response(self, prompt: str) -> None:
        pass


class NvidiaResponse(PromptResponseStrategy):
    async def response(self, prompt: str):
        '''
        Responde o prompt do usuário como streaming.\n
        Percorre cada chunk do stream e usa yield para devolver e retornar a cada próxima chamada.
        '''
        client = AsyncOpenAI(
            base_url=get_env('NVIDIA_API_URL'),
            api_key=get_env('NVIDIA_API_SECRET')
        )
        stream = await client.chat.completions.create(
            model=get_env('NVIDIA_API_MODEL'),
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        async for chunk in stream:
            yield chunk