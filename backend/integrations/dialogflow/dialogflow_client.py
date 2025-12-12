"""
Dialogflow Client
Handles NLP intent detection and entity extraction via Google Dialogflow
"""
import os
import logging

try:
    from google.cloud import dialogflow_v2beta1 as dialogflow
except ImportError:
    # Fallback to v2 if v2beta1 is not available
    try:
        from google.cloud import dialogflow_v2 as dialogflow
    except ImportError:
        raise ImportError(
            "google-cloud-dialogflow package is required. "
            "Install it with: pip install google-cloud-dialogflow"
        )

logger = logging.getLogger(__name__)


class DialogflowClient:
    """Dialogflow client for intent detection and NLP processing"""
    
    def __init__(self, project_id=None, credentials_path=None, language_code='en'):
        """
        Initialize Dialogflow client
        
        Args:
            project_id: Google Cloud project ID (defaults to env var)
            credentials_path: Path to service account JSON key (defaults to env var)
            language_code: Language code (default: 'en', can be 'hi' for Hindi)
        """
        self.project_id = project_id or os.getenv('DIALOGFLOW_PROJECT_ID')
        self.credentials_path = credentials_path or os.getenv('DIALOGFLOW_CREDENTIALS_PATH')
        self.language_code = language_code
        
        if not self.project_id:
            raise ValueError("DIALOGFLOW_PROJECT_ID must be set")
        
        # Set credentials if provided
        if self.credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
        
        try:
            self.session_client = dialogflow.SessionsClient()
            logger.info(f"DialogflowClient initialized for project {self.project_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Dialogflow client: {e}", exc_info=True)
            raise
    
    def detect_intent_texts(self, session_id, text, language_code=None):
        """
        Detect intent from text using Dialogflow
        
        Args:
            session_id: Session ID (typically phone number for context continuity)
            text: Input text to analyze
            language_code: Language code (defaults to instance language_code)
        
        Returns:
            dict: {
                "intent": str (intent display name),
                "confidence": float (0.0-1.0),
                "entities": dict (entity name -> value),
                "fulfillment_text": str (response text from Dialogflow)
            }
        """
        if language_code is None:
            language_code = self.language_code
        
        try:
            # Create session path
            session = self.session_client.session_path(self.project_id, session_id)
            
            # Create text input
            text_input = dialogflow.TextInput(text=text, language_code=language_code)
            
            # Create query input
            query_input = dialogflow.QueryInput(text=text_input)
            
            # Detect intent
            response = self.session_client.detect_intent(
                request={'session': session, 'query_input': query_input}
            )
            
            # Extract intent information
            intent = response.query_result.intent
            intent_name = intent.display_name if intent else 'Default Fallback Intent'
            confidence = response.query_result.intent_detection_confidence
            
            # Extract entities
            entities = {}
            for param_name, param_value in response.query_result.parameters.items():
                if param_value:  # Only include non-empty parameters
                    # Handle different parameter types
                    if isinstance(param_value, (list, tuple)):
                        entities[param_name] = param_value[0] if param_value else None
                    else:
                        entities[param_name] = param_value
            
            result = {
                'intent': intent_name,
                'confidence': confidence,
                'entities': entities,
                'fulfillment_text': response.query_result.fulfillment_text
            }
            
            logger.info(f"Detected intent '{intent_name}' (confidence: {confidence:.2f}) for session {session_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting intent for session {session_id}: {e}", exc_info=True)
            # Return fallback response
            return {
                'intent': 'Default Fallback Intent',
                'confidence': 0.0,
                'entities': {},
                'fulfillment_text': 'I did not understand that. Please try again.'
            }
    
    def detect_intent(self, session_id, text, language_code=None):
        """
        Alias for detect_intent_texts for backward compatibility
        """
        return self.detect_intent_texts(session_id, text, language_code)
    
    def extract_entities(self, session_id, text, intent_name=None):
        """
        Extract entities from text (convenience method)
        
        Args:
            session_id: Session ID
            text: Input text
            intent_name: Optional intent name to filter entities
        
        Returns:
            dict: Entity name -> value mapping
        """
        result = self.detect_intent_texts(session_id, text)
        
        # If intent_name specified, only return entities if intent matches
        if intent_name and result['intent'] != intent_name:
            return {}
        
        return result['entities']

