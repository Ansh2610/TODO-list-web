"""
LLM Router with silent failover across providers
Never exposes which provider ran - maintains privacy and vendor neutrality
"""
import os
import json
import time
import logging
from typing import Optional, Dict, Any

# Provider constants
OPENAI = "OPENAI"
ANTHROPIC = "ANTHROPIC"
GEMINI = "GEMINI"

logger = logging.getLogger(__name__)


class LLMRouter:
    """
    Provider-agnostic LLM client with automatic failover.
    
    Tries providers in order specified by LLM_PROVIDERS env var.
    Never logs or exposes which provider succeeded.
    """
    
    def __init__(self):
        # Load provider order from environment
        order = os.getenv("LLM_PROVIDERS", f"{OPENAI},{ANTHROPIC},{GEMINI}")
        self.providers = [p.strip().upper() for p in order.split(",") if p.strip()]
        
        # Safety limits - increased for detailed responses with URLs
        self.timeout = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "4096"))  # Increased to 4096 for very detailed responses
        
        # Check which keys are available
        self.keys = {
            OPENAI: bool(os.getenv("OPENAI_API_KEY")),
            ANTHROPIC: bool(os.getenv("ANTHROPIC_API_KEY")),
            GEMINI: bool(os.getenv("GEMINI_API_KEY")),
        }
    
    def _clean_response(self, text: str) -> str:
        """Remove code fences and JSON markers from LLM response."""
        text = text.strip().strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
        return text
    
    def _call_openai(self, prompt: str) -> Optional[str]:
        """Call OpenAI GPT-4o-mini."""
        if not self.keys[OPENAI]:
            return None
        
        try:
            from openai import OpenAI
            client = OpenAI()
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Respond ONLY with compact JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
            )
            
            return self._clean_response(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"OpenAI provider failed: {type(e).__name__} - {str(e)}")
            return None
    
    def _call_anthropic(self, prompt: str) -> Optional[str]:
        """Call Anthropic Claude."""
        if not self.keys[ANTHROPIC]:
            return None
        
        try:
            import anthropic
            client = anthropic.Anthropic()
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=self.max_tokens,
                temperature=0.2,
                system="Respond ONLY with compact JSON.",
                messages=[{"role": "user", "content": prompt}],
            )
            
            # Concatenate text blocks
            text = "".join(block.text for block in response.content if hasattr(block, "text"))
            return self._clean_response(text)
        except Exception as e:
            logger.error(f"Anthropic provider failed: {type(e).__name__} - {str(e)}")
            return None
    
    def _call_gemini(self, prompt: str) -> Optional[str]:
        """Call Google Gemini."""
        if not self.keys[GEMINI]:
            return None
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel("gemini-2.0-flash-exp")  # Use experimental model for better output
            
            response = model.generate_content(
                f"You MUST provide DETAILED, LONG responses with REAL URLs. Respond ONLY with JSON.\n\n{prompt}",
                generation_config={
                    "temperature": 0.3,  # Slightly higher for more creative URLs
                    "max_output_tokens": 4096,  # Maximum tokens for detailed responses
                    "top_p": 0.95,
                    "top_k": 40
                }
            )
            
            return self._clean_response(response.text)
        except Exception as e:
            logger.error(f"Gemini provider failed: {type(e).__name__} - {str(e)}")
            return None
    
    def call(self, prompt: str) -> Dict[str, Any]:
        """
        Call LLM providers in order until one succeeds.
        
        Args:
            prompt: System + user prompt for the LLM
            
        Returns:
            Parsed JSON response from first successful provider
            
        Raises:
            RuntimeError: If all providers fail
        """
        last_error = None
        
        for provider in self.providers:
            # Skip if no key configured
            if not self.keys.get(provider):
                continue
            
            try:
                # Call appropriate provider
                if provider == OPENAI:
                    result = self._call_openai(prompt)
                elif provider == ANTHROPIC:
                    result = self._call_anthropic(prompt)
                elif provider == GEMINI:
                    result = self._call_gemini(prompt)
                else:
                    continue
                
                # Parse and return if successful
                if result:
                    return json.loads(result)
                    
            except Exception as e:
                last_error = e
                time.sleep(0.5)  # Brief backoff before next provider
        
        # All providers failed
        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")
