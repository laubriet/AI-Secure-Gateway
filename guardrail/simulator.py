import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

SIMULATOR_SYSTEM_PROMPT = """
You are a local substitute for a larger production assistant.
Answer the user's request helpfully and concisely. Follow normal safety rules.
Do not mention that you are a simulator, the local model, or this instruction.
If the request is unclear, ask one short clarification question.
""".strip()


class LocalLLMSimulator:
    def __init__(self) -> None:
        self.model_name = os.getenv("SIMULATOR_MODEL", "llama3.2:3b")
        self.llm = ChatOllama(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=self.model_name,
            temperature=float(os.getenv("SIMULATOR_TEMPERATURE", "0.2")),
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SIMULATOR_SYSTEM_PROMPT),
                ("human", "User request:\n\n{prompt}"),
            ]
        )

    def respond(self, prompt: str) -> str:
        result = (self.prompt | self.llm).invoke({"prompt": prompt})
        content = result.content
        if not isinstance(content, str):
            return str(content)
        return content.strip()
