import yaml
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.schemas import DetectedLanguage

class NLUService:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(NLUService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        # Load model
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Load data
        core_path = Path(__file__).parent.parent / "core"
        with open(core_path / "nlu.yml", "r", encoding="utf-8") as f:
            self.nlu_data = yaml.safe_load(f)
        with open(core_path / "domain.yml", "r", encoding="utf-8") as f:
            self.domain_data = yaml.safe_load(f)
            
        self.intents = []
        self.examples = []
        self.intent_indices = []
        
        for item in self.nlu_data.get("nlu", []):
            intent = item["intent"]
            # Filter out the dash and split by lines
            examples = [e.strip("- ").strip() for e in item["examples"].split("\n") if e.strip("- ").strip()]
            for example in examples:
                self.intents.append(intent)
                self.examples.append(example)
                
        # Precompute embeddings for all training examples
        self.example_embeddings = self.model.encode(self.examples)
        self._initialized = True

    def find_best_match(self, text: str, threshold: float = 0.75):
        """
        Finds the best intent for the given text using cosine similarity.
        Returns: (intent_name, confidence_score)
        """
        query_embedding = self.model.encode([text])
        similarities = cosine_similarity(query_embedding, self.example_embeddings)[0]
        
        best_idx = np.argmax(similarities)
        confidence = similarities[best_idx]
        
        if confidence >= threshold:
            return self.intents[best_idx], confidence
        return None, confidence

    def get_response(self, intent: str, lang: DetectedLanguage):
        """
        Retrieves the localized response for an intent.
        """
        response_key = f"utter_{intent}"
        responses = self.domain_data.get("responses", {}).get(response_key, {})
        
        # Mapping DetectedLanguage enum to YAML keys
        lang_key = lang.value.lower()
        if lang_key == "ne_rom":
            return responses.get("ne_rom") or responses.get("en")
        elif lang_key == "ne":
            return responses.get("ne") or responses.get("en")
        
        return responses.get("en") or "I'm sorry, I don't have a response for that."

    def get_fallback_response(self, lang: DetectedLanguage):
        """
        Returns the localized fallback response.
        """
        responses = self.domain_data.get("responses", {}).get("utter_default_fallback", {})
        lang_key = lang.value.lower()
        return responses.get(lang_key) or responses.get("en")

nlu_service = NLUService()
