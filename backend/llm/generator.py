"""
LLM Generator - Handles text generation with citations and cost tracking
"""

from typing import Dict, Any, List, Optional
import re
import time
from datetime import datetime
import asyncio
import tiktoken


class LLMGenerator:
    """
    LLM wrapper supporting multiple providers with citation tracking
    """
    
    def __init__(
        self,
        provider: str = "gemini",  # openai, anthropic, huggingface, gemini
        model: str = "gemini-1.5-flash",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.base_url = base_url or "https://router.huggingface.co/models/"
        
        # Initialize client
        if provider == "openai":
            try:
                import openai
                self.client = openai.AsyncOpenAI(api_key=api_key)
            except ImportError:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
        elif provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.AsyncAnthropic(api_key=api_key)
            except ImportError:
                print("Warning: Anthropic package not installed. Use Gemini instead.")
                self.client = None
        elif provider == "gemini":
            # Google Gemini uses google-generativeai
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                # Ensure model has models/ prefix
                if not model.startswith("models/"):
                    model = f"models/{model}"
                # Map to available models
                model_map = {
                    "models/gemini-1.5-flash": "models/gemini-2.5-flash",
                    "models/gemini-1.5-pro": "models/gemini-2.5-pro",
                    "models/gemini-pro": "models/gemini-2.5-flash"
                }
                gemini_model = model_map.get(model, "models/gemini-2.5-flash")
                self.client = genai.GenerativeModel(gemini_model)
            except ImportError:
                raise ImportError("Google Generative AI not installed. Run: pip install google-generativeai")
        elif provider == "huggingface":
            # HuggingFace uses httpx for API calls
            import httpx
            self.client = httpx.AsyncClient(
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=60.0
            )
        else:
            self.client = None
        
        # Token counter
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except:
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Simple text generation
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        if self.provider == "openai":
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            return response.choices[0].message.content
        
        elif self.provider == "anthropic":
            if not self.client:
                raise ValueError("Anthropic client not initialized. Install: pip install anthropic")
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.content[0].text
        
        elif self.provider == "gemini":
            # Google Gemini API
            try:
                response = await asyncio.to_thread(
                    self.client.generate_content,
                    prompt,
                    generation_config={
                        "max_output_tokens": max_tokens,
                        "temperature": temperature,
                    }
                )
                return response.text
            except Exception as e:
                raise ValueError(f"Gemini API error: {str(e)}")
        
        elif self.provider == "huggingface":
            # HuggingFace Inference API
            url = f"{self.base_url}{self.model}"
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False,
                    **kwargs
                }
            }
            
            response = await self.client.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    return result.get("generated_text", "")
                return str(result)
            else:
                raise ValueError(f"HuggingFace API error: {response.status_code} - {response.text}")
        
        else:
            raise ValueError(f"Provider {self.provider} not supported. Use 'gemini', 'huggingface', 'openai', or 'anthropic'.")
    
    async def generate_with_citations(
        self,
        question: str,
        context: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Generate answer with inline citations
        
        Args:
            question: User question
            context: Retrieved context with numbered sources
            temperature: LLM temperature
            max_tokens: Maximum tokens
            
        Returns:
            Dict with answer, citations, and metadata
        """
        start_time = time.time()
        
        # Build prompt with citation instructions
        prompt = f"""You are a helpful AI assistant. Answer the question based on the provided context.

IMPORTANT: Use inline citations in your answer. When referencing information from the context, add [N] where N is the source number.

For example: "Zero Knowledge Proofs allow verification without revealing information [2]."

Context:
{context}

Question: {question}

Answer with citations:"""
        
        # Count input tokens
        input_tokens = len(self.encoding.encode(prompt))
        
        # Generate response
        try:
            answer = await self.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Count output tokens
            output_tokens = len(self.encoding.encode(answer))
            total_tokens = input_tokens + output_tokens
            
            # Extract citations
            citations = self._extract_citations(answer)
            
            # Calculate cost
            cost = self._calculate_cost(input_tokens, output_tokens)
            
            generation_time = time.time() - start_time
            
            return {
                "answer": answer,
                "citations": citations,
                "tokens_used": total_tokens,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "estimated_cost": cost,
                "generation_time": generation_time,
                "model": self.model
            }
            
        except Exception as e:
            raise Exception(f"Generation failed: {str(e)}")
    
    async def generate_streaming(
        self,
        question: str,
        context: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """
        Generate answer with streaming support
        
        Yields:
            Chunks of generated text
        """
        prompt = f"""You are a helpful AI assistant. Answer the question based on the provided context.

IMPORTANT: Use inline citations in your answer. When referencing information from the context, add [N] where N is the source number.

Context:
{context}

Question: {question}

Answer with citations:"""
        
        if self.provider == "openai":
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        elif self.provider == "anthropic":
            if not self.client:
                raise ValueError("Anthropic client not initialized. Use HuggingFace instead.")
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        
        elif self.provider == "gemini":
            # Gemini streaming
            try:
                response = await asyncio.to_thread(
                    self.client.generate_content,
                    prompt,
                    generation_config={
                        "max_output_tokens": max_tokens,
                        "temperature": temperature,
                    },
                    stream=True
                )
                
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
            except Exception as e:
                # Fallback to non-streaming
                full_response = await self.generate(prompt, max_tokens, temperature)
                words = full_response.split()
                for i, word in enumerate(words):
                    if i == 0:
                        yield word
                    else:
                        yield " " + word
                    await asyncio.sleep(0.01)
        
        elif self.provider == "huggingface":
            # HuggingFace doesn't support streaming in Inference API
            # Generate full response and yield in chunks
            full_response = await self.generate(prompt, max_tokens, temperature)
            
            # Simulate streaming by yielding words
            words = full_response.split()
            for i, word in enumerate(words):
                if i == 0:
                    yield word
                else:
                    yield " " + word
                await asyncio.sleep(0.01)  # Small delay to simulate streaming
    
    def _extract_citations(self, text: str) -> List[int]:
        """Extract citation numbers from text"""
        # Find all [N] patterns
        citations = re.findall(r'\[(\d+)\]', text)
        # Convert to integers and remove duplicates
        return sorted(list(set([int(c) for c in citations])))
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate estimated cost based on model pricing
        
        Prices per 1M tokens (as of 2024)
        HuggingFace Inference API is FREE for most models!
        """
        pricing = {
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
            "gpt-4": {"input": 30.00, "output": 60.00},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
            "claude-3-opus": {"input": 15.00, "output": 75.00},
            "claude-3-sonnet": {"input": 3.00, "output": 15.00},
            "claude-3-haiku": {"input": 0.25, "output": 1.25},
            # Google Gemini is FREE!
            "gemini-pro": {"input": 0.0, "output": 0.0},
            "gemini-1.5-flash": {"input": 0.0, "output": 0.0},
            # HuggingFace models are free!
            "mistralai/Mistral-7B-Instruct-v0.2": {"input": 0.0, "output": 0.0},
            "meta-llama/Llama-2-7b-chat-hf": {"input": 0.0, "output": 0.0},
            "google/flan-t5-large": {"input": 0.0, "output": 0.0},
        }
        
        model_pricing = pricing.get(self.model, {"input": 0, "output": 0})
        
        input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
        output_cost = (output_tokens / 1_000_000) * model_pricing["output"]
        
        return round(input_cost + output_cost, 6)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    async def compress_context(
        self,
        context: str,
        max_tokens: int = 2000
    ) -> str:
        """
        Compress context to fit within token limit
        Uses LLM to summarize if needed
        
        Args:
            context: Original context
            max_tokens: Maximum tokens allowed
            
        Returns:
            Compressed context
        """
        current_tokens = self.count_tokens(context)
        
        if current_tokens <= max_tokens:
            return context
        
        # Use LLM to compress
        compression_prompt = f"""Summarize the following context, keeping the most important information.
Keep it under {max_tokens} tokens while preserving key facts and details.

Context:
{context}

Compressed Summary:"""
        
        try:
            compressed = await self.generate(
                prompt=compression_prompt,
                max_tokens=max_tokens,
                temperature=0.3
            )
            return compressed
        except:
            # Fallback: simple truncation
            tokens = self.encoding.encode(context)
            truncated_tokens = tokens[:max_tokens]
            return self.encoding.decode(truncated_tokens)
