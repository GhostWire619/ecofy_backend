"""
Chat Service using Gemini AI
Provides conversational AI capabilities with context management
"""

import logging
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from app.core.config import settings

logger = logging.getLogger(__name__)


class ChatGeminiService:
    """Service for conversational AI using Gemini"""

    def __init__(self):
        self.api_key = None
        self.client = None
        self.chat_model = "gemini-2.0-flash-exp"
        
    def _ensure_initialized(self):
        """Lazy initialization of Gemini client"""
        if self.client is None:
            self.api_key = settings.GOOGLE_GEMINI_API_KEY
            if not self.api_key:
                raise ValueError("GOOGLE_GEMINI_API_KEY environment variable not set")
            
            self.client = genai.Client(api_key=self.api_key)

    def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_instruction: Optional[str] = None,
        temperature: float = 0.9
    ) -> str:
        """
        Send a chat message and get a response
        
        Args:
            message: User's message
            conversation_history: List of previous messages [{"role": "user/model", "content": "..."}]
            system_instruction: Optional system instruction to guide the model's behavior
            temperature: Controls randomness (0.0-1.0, higher = more creative)
            
        Returns:
            AI response as string
        """
        self._ensure_initialized()
        
        try:
            # Build conversation contents
            contents = self._build_conversation_contents(message, conversation_history)
            
            # Configure generation
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=2048,
                top_p=0.95,
                top_k=40
            )
            
            # Add system instruction if provided
            if system_instruction:
                model = genai.GenerativeModel(
                    model_name=self.chat_model,
                    system_instruction=system_instruction
                )
                response = model.generate_content(
                    contents=contents,
                    config=config
                )
            else:
                response = self.client.models.generate_content(
                    model=self.chat_model,
                    contents=contents,
                    config=config
                )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error in chat service: {e}")
            raise

    def chat_with_context(
        self,
        message: str,
        context_data: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Chat with additional context (useful for domain-specific conversations)
        
        Args:
            message: User's message
            context_data: Additional context to provide to the model
            conversation_history: Previous conversation messages
            
        Returns:
            AI response as string
        """
        self._ensure_initialized()
        
        try:
            # Build enhanced message with context
            enhanced_message = self._build_contextual_message(message, context_data)
            
            return self.chat(
                message=enhanced_message,
                conversation_history=conversation_history,
                temperature=0.8
            )
            
        except Exception as e:
            logger.error(f"Error in contextual chat: {e}")
            raise

    def agricultural_chat(
        self,
        message: str,
        user_data: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Specialized chat for agricultural queries
        
        Args:
            message: User's agricultural question
            user_data: Optional user's farm/location data
            conversation_history: Previous messages
            
        Returns:
            Agricultural expert response
        """
        self._ensure_initialized()
        
        system_instruction = """You are an expert agricultural consultant with deep knowledge in:
        - Crop cultivation and management
        - Soil science and fertility
        - Pest and disease management
        - Weather and climate impact on agriculture
        - Agricultural markets and economics
        - Sustainable farming practices
        - Irrigation and water management
        - Organic farming techniques

        Provide practical, actionable advice based on scientific principles and best practices.
        Be conversational, friendly, and easy to understand while maintaining expertise.
        When relevant, ask clarifying questions to provide better recommendations."""

        try:
            # Add user context if available
            if user_data:
                context_note = f"\n\n[User Context: {user_data}]"
                message_with_context = message + context_note
            else:
                message_with_context = message
            
            return self.chat(
                message=message_with_context,
                conversation_history=conversation_history,
                system_instruction=system_instruction,
                temperature=0.8
            )
            
        except Exception as e:
            logger.error(f"Error in agricultural chat: {e}")
            raise

    def stream_chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_instruction: Optional[str] = None
    ):
        """
        Stream chat response for real-time display
        
        Args:
            message: User's message
            conversation_history: Previous messages
            system_instruction: Optional system instruction
            
        Yields:
            Chunks of the response as they're generated
        """
        self._ensure_initialized()
        
        try:
            contents = self._build_conversation_contents(message, conversation_history)
            
            config = types.GenerateContentConfig(
                temperature=0.9,
                max_output_tokens=2048,
                top_p=0.95
            )
            
            if system_instruction:
                model = genai.GenerativeModel(
                    model_name=self.chat_model,
                    system_instruction=system_instruction
                )
                response_stream = model.generate_content_stream(
                    contents=contents,
                    config=config
                )
            else:
                response_stream = self.client.models.generate_content_stream(
                    model=self.chat_model,
                    contents=contents,
                    config=config
                )
            
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Error in streaming chat: {e}")
            raise

    def _build_conversation_contents(
        self,
        current_message: str,
        conversation_history: Optional[List[Dict[str, str]]]
    ) -> List[types.Content]:
        """Build conversation contents from history and current message"""
        
        contents = []
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part(text=msg["content"])]
                    )
                )
        
        # Add current message
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=current_message)]
            )
        )
        
        return contents

    def _build_contextual_message(
        self,
        message: str,
        context_data: Dict[str, Any]
    ) -> str:
        """Enhance message with contextual information"""
        
        import json
        context_str = json.dumps(context_data, indent=2)
        
        return f"""{message}

        [Additional Context]:
        {context_str}

        Please consider the above context when formulating your response."""


# Singleton instance
chat_service = ChatGeminiService()