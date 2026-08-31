# backend/llm_manager.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class LLMResponse:
    text: str
    provider: str

class LLMManager:
    """Tries providers in order, falls back on failure."""

    def __init__(self):
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.order = ["groq", "ollama", "gemini"]

    def generate(
        self,
        prompt: str,
        system: str = "",
        exclude: list[str] | None = None
    ) -> LLMResponse:

        exclude = exclude or []

        for provider in self.order:
            if provider in exclude:
                continue

            try:
                if provider == "groq" and self.groq_key:
                    return self._call_groq(prompt, system)

                if provider == "gemini" and self.gemini_key:
                    return self._call_gemini(prompt, system)

                if provider == "ollama":
                    return self._call_ollama(prompt, system)

            except Exception as e:
                print(f"[LLMManager] {provider} failed: {e} — falling back")
                continue

        raise RuntimeError("All providers failed")

    def _call_groq(self, prompt, system):
        from groq import Groq
        client = Groq(api_key=self.groq_key)
        resp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": prompt}],
        )
        return LLMResponse(resp.choices[0].message.content, "groq")

    def _call_gemini(self, prompt, system):
        from google import genai
        client = genai.Client(api_key=self.gemini_key)
        resp = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=f"{system}\n\n{prompt}",
        )
        return LLMResponse(resp.text, "gemini")

    def _call_ollama(self, prompt, system):
        import ollama
        resp = ollama.chat(
            model="llama3.2:3b",
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": prompt}],
        )
        return LLMResponse(resp["message"]["content"], "ollama")