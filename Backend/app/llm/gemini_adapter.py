import os
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from ..config import settings
from .provider import LLMProvider

class GeminiAdapter(LLMProvider):
    """Adapter for Google's Gemini API."""
    
    def __init__(self):
        """Initialize the Gemini client."""
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required in settings or environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text using the Gemini API.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0.0 to 1.0)
            **kwargs: Additional parameters for the API call
            
        Returns:
            Generated text
        """
        try:
            # Configure generation parameters
            generation_config = {
                'temperature': min(max(temperature, 0), 1),  # Clamp to 0-1 range
                'max_output_tokens': max(1, min(max_tokens, 8192)),  # Clamp to valid range
                **kwargs
            }
            
            # Make the API call
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract and return the generated text
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                return response.candidates[0].content.parts[0].text
            else:
                return ""
                
        except Exception as e:
            # Log the error and re-raise with a more descriptive message
            error_msg = f"Error generating text with Gemini: {str(e)}"
            raise Exception(error_msg) from e
    
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate chat completion using the Gemini API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0.0 to 1.0)
            **kwargs: Additional parameters for the API call
            
        Returns:
            Generated text
        """
        try:
            # Convert messages to Gemini's format
            chat = self.model.start_chat(history=[])
            
            # Add all but the last message as history
            for msg in messages[:-1]:
                if msg['role'] == 'user':
                    chat.send_message(msg['content'])
                # Gemini doesn't support system messages directly, so we'll add them as user messages
                elif msg['role'] == 'system':
                    chat.send_message(f"System: {msg['content']}")
            
            # Configure generation parameters
            generation_config = {
                'temperature': min(max(temperature, 0), 1),  # Clamp to 0-1 range
                'max_output_tokens': max(1, min(max_tokens, 8192)),  # Clamp to valid range
                **kwargs
            }
            
            # Get the last message as the current prompt
            last_message = messages[-1]
            if last_message['role'] != 'user':
                raise ValueError("Last message must be from the user")
            
            # Generate the response
            response = chat.send_message(
                last_message['content'],
                generation_config=generation_config
            )
            
            # Extract and return the generated text
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                return response.candidates[0].content.parts[0].text
            else:
                return ""
                
        except Exception as e:
            # Log the error and re-raise with a more descriptive message
            error_msg = f"Error generating chat completion with Gemini: {str(e)}"
            raise Exception(error_msg) from e
