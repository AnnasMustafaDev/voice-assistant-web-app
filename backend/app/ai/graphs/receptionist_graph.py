"""LangGraph orchestration for conversation flows."""

from typing import Dict, List, Optional, Any, Annotated
from enum import Enum
from dataclasses import dataclass, field
from app.ai.groq_client import get_groq_client
from app.ai.rag.retriever import get_retriever
from app.ai.rag.cache import get_cag
from app.ai.prompts.system_prompts import get_system_prompt
from app.core.logging import logger

try:
    from langgraph.graph import StateGraph
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False
    logger.warning("LangGraph not installed, using simplified orchestration")


class IntentType(str, Enum):
    """Intent classification types."""
    BOOKING = "booking"
    FAQ = "faq"
    PRICING = "pricing"
    LEAD_CAPTURE = "lead_capture"
    ESCALATION = "escalation"
    UNKNOWN = "unknown"


@dataclass
class ConversationState:
    """State for conversation flow."""
    # Input
    user_message: str
    
    # Context
    tenant_id: str
    agent_id: str
    agent_type: str
    conversation_id: str
    
    # Processing
    intent: Optional[IntentType] = None
    context_documents: List[Dict] = field(default_factory=list)
    cache_hit: bool = False
    cached_response: Optional[str] = None
    
    # Output
    response: Optional[str] = None
    requires_escalation: bool = False
    
    # History
    messages: List[Dict] = field(default_factory=list)


class ConversationOrchestrator:
    """Orchestrates conversation flow using LangGraph-like pattern."""
    
    def __init__(self):
        """Initialize orchestrator."""
        self.groq_client = get_groq_client()
        self.retriever = get_retriever()
        self.cag = get_cag()
    
    async def classify_intent(self, state: ConversationState) -> ConversationState:
        """
        Classify user intent.
        
        Node: IntentClassifier
        """
        try:
            # Quick heuristic-based intent classification
            message_lower = state.user_message.lower()
            
            if any(word in message_lower for word in ["book", "reserve", "table", "reservation"]):
                state.intent = IntentType.BOOKING
            elif any(word in message_lower for word in ["price", "cost", "how much", "fee"]):
                state.intent = IntentType.PRICING
            elif any(word in message_lower for word in ["contact", "phone", "email", "call", "speaking"]):
                state.intent = IntentType.LEAD_CAPTURE
            elif any(word in message_lower for word in ["help", "human", "agent", "support"]):
                state.intent = IntentType.ESCALATION
            else:
                state.intent = IntentType.FAQ
            
            logger.info(f"Intent classified: {state.intent.value}")
            return state
        except Exception as e:
            logger.error(f"Intent classification error: {str(e)}")
            state.intent = IntentType.UNKNOWN
            return state
    
    async def check_cache(self, state: ConversationState) -> ConversationState:
        """
        Check if response is cached.
        
        Node: CacheCheck (CAG)
        """
        try:
            cached = await self.cag.get(
                state.tenant_id,
                state.agent_id,
                state.user_message
            )
            
            if cached:
                state.cache_hit = True
                state.cached_response = cached
                logger.info("Cache hit!")
            
            return state
        except Exception as e:
            logger.error(f"Cache check error: {str(e)}")
            return state
    
    async def retrieve_context(
        self,
        db,
        state: ConversationState
    ) -> ConversationState:
        """
        Retrieve relevant documents from knowledge base.
        
        Node: RAGRetriever
        """
        try:
            docs = await self.retriever.retrieve(
                db,
                state.tenant_id,
                state.user_message,
                top_k=3
            )
            
            state.context_documents = [
                {
                    "title": doc.title,
                    "source": doc.source,
                    "content": doc.content[:500]
                }
                for doc in docs
            ]
            
            logger.info(f"Retrieved {len(docs)} context documents")
            return state
        except Exception as e:
            logger.error(f"Context retrieval error: {str(e)}")
            return state
    
    async def generate_response(
        self,
        state: ConversationState
    ) -> ConversationState:
        """
        Generate LLM response.
        
        Node: LLMResponse
        """
        if state.cache_hit:
            # Use cached response
            state.response = state.cached_response
            return state
        
        try:
            # Build system prompt
            system_prompt = get_system_prompt(
                state.agent_type,
                context=self._format_context(state.context_documents)
            )
            
            # Add conversation history
            history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in state.messages[-4:]  # Last 2 turns
            ]
            
            # Generate response
            response = await self.groq_client.generate_response(
                system_prompt=system_prompt,
                user_message=state.user_message,
                conversation_history=history
            )
            
            state.response = response
            
            # Cache the response
            await self.cag.set(
                state.tenant_id,
                state.agent_id,
                state.user_message,
                response
            )
            
            logger.info("Response generated and cached")
            return state
        except Exception as e:
            logger.error(f"Response generation error: {str(e)}")
            # Provide context-aware fallback responses based on detected intent
            fallback_responses = {
                IntentType.BOOKING: "I'd be happy to help you with a booking. Could you please provide me with your preferred date and time?",
                IntentType.PRICING: "Our pricing varies based on the service. Let me check the current rates for you. What specific service are you interested in?",
                IntentType.LEAD_CAPTURE: "Thank you for contacting us. Could you please provide your name and phone number so we can follow up with you?",
                IntentType.ESCALATION: "I understand you'd like to speak with an agent. Let me connect you with someone who can better assist you.",
                IntentType.FAQ: "That's a great question. Let me provide you with more information about that.",
            }
            state.response = fallback_responses.get(
                state.intent,
                "I apologize, I'm having trouble processing your request. Could you please rephrase?"
            )
            return state
    
    def validate_response(self, state: ConversationState) -> ConversationState:
        """
        Validate response before returning.
        
        Node: Validation
        """
        if not state.response:
            state.response = "I'm not sure how to help with that. Could you provide more details?"
        
        # Check if response requires escalation
        if state.intent == IntentType.ESCALATION:
            state.requires_escalation = True
        
        logger.info("Response validated")
        return state
    
    async def execute_flow(
        self,
        db,
        state: ConversationState
    ) -> ConversationState:
        """
        Execute full conversation flow.
        
        Flow:
        START → IntentClassifier → CacheCheck → RAGRetriever → 
        LLMResponse → Validation → END
        """
        logger.info(f"Starting conversation flow for message: {state.user_message[:50]}")
        
        # Execute nodes in sequence
        state = await self.classify_intent(state)
        state = await self.check_cache(state)
        
        if not state.cache_hit:
#            state = await self.retrieve_context(db, state)
            state = await self.generate_response(state)
        
        state = self.validate_response(state)
        
        logger.info(f"Conversation flow complete. Response: {state.response[:100]}")
        return state
    
    def _format_context(self, documents: List[Dict]) -> str:
        """Format context documents for prompt."""
        if not documents:
            return ""
        
        formatted = "Available context:\n"
        for doc in documents:
            formatted += f"\n- {doc['title']} ({doc['source']}):\n{doc['content'][:200]}...\n"
        
        return formatted


# Global orchestrator
_orchestrator = None


def get_orchestrator() -> ConversationOrchestrator:
    """Get or create orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ConversationOrchestrator()
    return _orchestrator
