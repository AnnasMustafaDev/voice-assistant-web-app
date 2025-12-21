"""Real estate specific orchestration."""

from app.ai.graphs.receptionist_graph import (
    ConversationOrchestrator,
    ConversationState,
    IntentType,
)
from app.core.logging import logger


class RealEstateOrchestrator(ConversationOrchestrator):
    """Real estate specific orchestration."""
    
    async def classify_intent(self, state: ConversationState) -> ConversationState:
        """
        Classify intent with real estate specific keywords.
        """
        try:
            message_lower = state.user_message.lower()
            
            if any(word in message_lower for word in ["view", "visit", "see", "appointment", "tour", "schedule"]):
                state.intent = IntentType.BOOKING
            elif any(word in message_lower for word in ["price", "cost", "how much", "payment", "financing"]):
                state.intent = IntentType.PRICING
            elif any(word in message_lower for word in ["name", "phone", "email", "contact", "call me"]):
                state.intent = IntentType.LEAD_CAPTURE
            elif any(word in message_lower for word in ["location", "where", "address", "neighborhood", "area"]):
                state.intent = IntentType.FAQ
            elif any(word in message_lower for word in ["help", "human", "agent", "support"]):
                state.intent = IntentType.ESCALATION
            else:
                state.intent = IntentType.FAQ
            
            logger.info(f"Real estate intent classified: {state.intent.value}")
            return state
        except Exception as e:
            logger.error(f"Intent classification error: {str(e)}")
            state.intent = IntentType.UNKNOWN
            return state


# Global instance
_re_orchestrator = None


def get_real_estate_orchestrator() -> RealEstateOrchestrator:
    """Get or create real estate orchestrator."""
    global _re_orchestrator
    if _re_orchestrator is None:
        _re_orchestrator = RealEstateOrchestrator()
    return _re_orchestrator
