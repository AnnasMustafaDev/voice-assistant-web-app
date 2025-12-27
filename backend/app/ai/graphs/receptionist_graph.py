"""Voice-first conversation orchestration (simplified for real-time voice)."""

from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from app.ai.groq_client import get_groq_client
from app.ai.prompts.system_prompts import get_system_prompt
from app.core.logging import logger


class IntentType(str, Enum):
    """Voice-specific intent types."""
    BOOKING = "booking"
    PRICING = "pricing"
    LEAD_CAPTURE = "lead_capture"
    ESCALATION = "escalation"
    UNKNOWN = "unknown"


# Acknowledgement filter: trivial utterances that need no LLM processing
ACKNOWLEDGEMENT_WORDS = {
    "thank you", "thanks", "thankyou",
    "ok", "okay", "okayed",
    "yes", "yeah", "yep", "sure", "certainly",
    "no", "nope",
    "hmm", "uh", "um", "uh-huh", "uhuh",
    "got it", "gotit",
    "thanks so much", "thank you so much"
}

# Acknowledgement responses: polite, brief closings
ACKNOWLEDGEMENT_RESPONSES = {
    "thank you": "You're welcome! Feel free to reach out if you need anything else.",
    "thanks": "My pleasure! Don't hesitate to ask if you need help.",
    "ok": "Great, I'm here if you need anything else.",
    "okay": "Perfect! Let me know if there's anything else I can help with.",
    "yes": "Excellent! Is there anything else I can assist you with?",
    "no": "Understood. Feel free to contact us if you need anything.",
}


@dataclass
class VoiceConversationState:
    """Minimal state for real-time voice conversations."""
    # Input
    user_utterance: str
    
    # Context (session-specific)
    tenant_id: str
    agent_id: str
    conversation_id: str
    language: str = "en"  # Lock language per session
    
    # Processing
    intent: IntentType = IntentType.UNKNOWN
    is_acknowledgement: bool = False
    
    # Output
    response: Optional[str] = None
    
    # Flags
    requires_escalation: bool = False


class ConversationOrchestrator:
    """Simplified orchestrator for real-time voice conversations."""
    
    def __init__(self):
        """Initialize orchestrator."""
        self.groq_client = get_groq_client()
    
    # ========== STAGE 1: Acknowledgement Filter ==========
    async def filter_acknowledgements(self, state: VoiceConversationState) -> VoiceConversationState:
        """
        MANDATORY FIRST STEP: Detect and handle trivial utterances.
        
        Examples: "thank you", "ok", "yes"
        
        Respond with a brief, polite closing line instead.
        """
        utterance_lower = state.user_utterance.lower().strip()
        word_count = len(utterance_lower.split())
        
        # Rule: Short utterance (≤2 words) that matches acknowledgements
        if word_count <= 2 and utterance_lower in ACKNOWLEDGEMENT_WORDS:
            state.is_acknowledgement = True
            state.response = ACKNOWLEDGEMENT_RESPONSES.get(
                utterance_lower,
                "Thank you! Is there anything else I can help you with?"
            )
            logger.info(f"[FILTER] Acknowledgement detected: '{utterance_lower}' → short response")
            return state
        
        logger.info(f"[FILTER] Not an acknowledgement: '{utterance_lower}' (passed to intent classification)")
        return state
    
    # ========== STAGE 2: Simplified Intent Classification ==========
    async def classify_intent(self, state: VoiceConversationState) -> VoiceConversationState:
        """
        Simplified intent classification for voice.
        
        Only classifies:
        - booking
        - pricing
        - lead_capture
        - escalation
        - UNKNOWN (triggers clarifying question)
        
        Uses keyword heuristics, no ML/RAG.
        """
        # Skip if already acknowledged
        if state.is_acknowledgement:
            return state
        
        try:
            utterance_lower = state.user_utterance.lower()
            
            # Booking intent
            if any(word in utterance_lower for word in ["book", "reserve", "table", "reservation", "appointment"]):
                state.intent = IntentType.BOOKING
                logger.info(f"[INTENT] BOOKING detected")
            
            # Pricing intent
            elif any(word in utterance_lower for word in ["price", "cost", "how much", "fee", "rate", "charge"]):
                state.intent = IntentType.PRICING
                logger.info(f"[INTENT] PRICING detected")
            
            # Lead capture intent
            elif any(word in utterance_lower for word in ["contact", "phone", "email", "call", "call me", "reach"]):
                state.intent = IntentType.LEAD_CAPTURE
                logger.info(f"[INTENT] LEAD_CAPTURE detected")
            
            # Escalation intent
            elif any(word in utterance_lower for word in ["help", "human", "agent", "support", "manager", "supervisor"]):
                state.intent = IntentType.ESCALATION
                logger.info(f"[INTENT] ESCALATION detected")
            
            # Default: UNKNOWN
            else:
                state.intent = IntentType.UNKNOWN
                logger.info(f"[INTENT] UNKNOWN - will ask clarifying question")
            
            return state
        
        except Exception as e:
            logger.error(f"[INTENT] Classification error: {str(e)}")
            state.intent = IntentType.UNKNOWN
            return state
    
    # ========== STAGE 3: LLM Response Generation ==========
    async def generate_response(self, state: VoiceConversationState) -> VoiceConversationState:
        """
        Generate response via LLM.
        
        Direct call to Groq API with:
        - System prompt based on intent
        - User utterance
        - NO RAG, NO caching, NO history
        
        For voice: keep responses short (< 500 chars)
        """
        # Skip if already responded (acknowledgement or escalation)
        if state.response or state.is_acknowledgement:
            return state
        
        try:
            # Build system prompt based on intent
            system_prompt = self._get_system_prompt_for_intent(state.intent, state.language)
            
            logger.info(f"[LLM] Generating response for intent={state.intent.value}, lang={state.language}")
            
            # Call LLM
            response = await self.groq_client.generate_response(
                system_prompt=system_prompt,
                user_message=state.user_utterance,
                conversation_history=[]  # No history for voice
            )
            
            state.response = response
            logger.info(f"[LLM] Response generated: {response[:80]}...")
            return state
        
        except Exception as e:
            logger.error(f"[LLM] Generation error: {str(e)}")
            # Fallback based on intent
            state.response = self._get_fallback_response(state.intent)
            logger.info(f"[LLM] Using fallback: {state.response[:80]}...")
            return state
    
    # ========== STAGE 4: Validation (Passive) ==========
    def validate_response(self, state: VoiceConversationState) -> VoiceConversationState:
        """
        Passive validation: only check response exists.
        
        RULE: Never replace a valid response with fallback.
        Escalation flag should NOT modify message content.
        """
        if not state.response:
            # Only assign fallback if no response at all
            state.response = "I'm here to help. Could you please rephrase your question?"
            logger.info(f"[VALIDATE] No response - using generic fallback")
        
        # Check escalation (informational only, doesn't change response)
        if state.intent == IntentType.ESCALATION:
            state.requires_escalation = True
            logger.info(f"[VALIDATE] Escalation flagged - response will be routed")
        
        logger.info(f"[VALIDATE] Response validated, length={len(state.response)} chars")
        return state
    
    # ========== EXECUTION ==========
    async def process_utterance(self, state: VoiceConversationState) -> VoiceConversationState:
        """
        Main orchestration flow (voice-first).
        
        STT → Utterance Filter → Intent Lite → LLM → Validate → TTS
        
        Each step logs clearly:
        - utterance filtered
        - intent detected
        - response generated
        """
        logger.info(f"[FLOW] Starting: '{state.user_utterance}' (tenant={state.tenant_id}, lang={state.language})")
        
        # Step 1: Filter acknowledgements (must be first)
        state = await self.filter_acknowledgements(state)
        
        # Step 2: Classify intent (skipped if acknowledgement)
        if not state.is_acknowledgement:
            state = await self.classify_intent(state)
        
        # Step 3: Generate response (skipped if already responded)
        if not state.response:
            state = await self.generate_response(state)
        
        # Step 4: Validate (always run)
        state = self.validate_response(state)
        
        logger.info(f"[FLOW] Complete: intent={state.intent.value}, ack={state.is_acknowledgement}, escalate={state.requires_escalation}")
        return state
    
    # ========== HELPER METHODS ==========
    def _get_system_prompt_for_intent(self, intent: IntentType, language: str) -> str:
        """Get appropriate system prompt for intent."""
        base_prompt = get_system_prompt("receptionist", language=language)
        
        # Add intent-specific guidance
        intent_guidance = {
            IntentType.BOOKING: "\nThe user is asking about making a reservation or booking.",
            IntentType.PRICING: "\nThe user is asking about pricing or costs.",
            IntentType.LEAD_CAPTURE: "\nThe user wants to be contacted. Ask for their preferred contact method and time.",
            IntentType.ESCALATION: "\nThe user wants to speak with a human agent. Acknowledge and prepare for handoff.",
            IntentType.UNKNOWN: "\nYou're not sure what the user wants. Ask a clarifying question to understand their need.",
        }
        
        return base_prompt + intent_guidance.get(intent, "")
    
    def _get_fallback_response(self, intent: IntentType) -> str:
        """Get fallback response for intent."""
        fallbacks = {
            IntentType.BOOKING: "I'd be happy to help with a booking. Could you tell me what date and time you're interested in?",
            IntentType.PRICING: "Our pricing depends on the specific service. What would you like to know more about?",
            IntentType.LEAD_CAPTURE: "I'd love to follow up with you. Could you provide your contact information?",
            IntentType.ESCALATION: "Let me connect you with a team member who can better assist you.",
            IntentType.UNKNOWN: "I want to make sure I understand correctly. Could you give me more details about what you need?",
        }
        return fallbacks.get(intent, "How can I help you today?")


# Global orchestrator singleton
_orchestrator = None


def get_orchestrator() -> ConversationOrchestrator:
    """Get or create global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ConversationOrchestrator()
    return _orchestrator
