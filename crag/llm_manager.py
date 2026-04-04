"""LLM and chain management with lazy loading."""

import logging
from typing import Optional
from functools import lru_cache
from crag.config import get_settings


logger = logging.getLogger(__name__)
import os
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


class LLMManager:
    """Manages LLM instances with lazy loading."""

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.0,openai_api_key:Optional[str]=None):
        self.model_name = model_name
        self.temperature = temperature
        self.openai_api_key=openai_api_key
        self._llm = None
        self._grader_chain = None
        self._generator_chain = None

    @property
    def llm(self):
        """Lazy load LLM."""
        if self._llm is None:
            logger.info(f"Initializing LLM: {self.model_name}")
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                openai_api_key=self.openai_api_key
            )
        return self._llm

    def get_grader_chain(self, prompt_template: str):
        """Get document grading chain."""
        if self._grader_chain is None:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate
            grader_prompt = ChatPromptTemplate.from_template(prompt_template)
            self._grader_chain = grader_prompt | self.llm | StrOutputParser()
        return self._grader_chain

    def get_generator_chain(self, prompt_template: str):
        """Get answer generation chain."""
        if self._generator_chain is None:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate
            generator_prompt = ChatPromptTemplate.from_template(prompt_template)
            self._generator_chain = generator_prompt | self.llm | StrOutputParser()
        return self._generator_chain
    
  

    def get_llm_manager(model_name:str ="gpt-4o-mini",temperature:float = 0.0) -> "LLMManager":
        global _instance
        if _instance is None:
            settings=get_settings()
            _instance = LLMManager(
                model_name= model_name,
                temperature=temperature,
                openai_api_key=settings.OPENAI_API_KEY
            )
        return _instance

    