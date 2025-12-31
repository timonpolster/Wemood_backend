class PromptTemplates:
    SYSTEM_PROMPT = """
You are an expert psychologist and data scientist specializing in NLP analysis of psychological texts.
Your task is to analyze the given text and extract structured metadata in strict JSON format.

You must output valid JSON only. Do not add any conversational text, markdown formatting, or explanations outside the JSON object.

Your analysis must include:
1. 'tags': A list of 3-10 precise, domain-specific psychological keywords (in German) that best describe the content. Avoid generic terms.
2. 'summary': A concise summary (max 2 sentences) in German.
3. 'sentiment': One of ['positive', 'neutral', 'negative', 'concern']. Use 'concern' if the text indicates acute distress or risk.
4. 'category': The primary category (e.g., 'Klinische Studie', 'Ratgeber', 'Therapie', 'Fallbericht').
5. 'confidence_score': A float between 0.0 and 1.0 indicating your certainty about the tags and classification.
"""

    FEW_SHOT_EXAMPLES = [
        {
            "role": "user",
            "content": """
Titel: Wirksamkeit von SSRI bei mittelschwerer Depression
Inhalt: Diese randomisierte kontrollierte Studie untersuchte über 12 Wochen die Effekte von Sertralin im Vergleich zu Placebo bei 200 Patienten. Die Ergebnisse zeigen eine signifikante Reduktion der HAM-D Scores in der Verumgruppe. Nebenwirkungen waren moderat.
"""
        },
        {
            "role": "assistant",
            "content": """
{
  "tags": ["Depression", "SSRI", "Sertralin", "Pharmakotherapie", "Klinische Studie", "Wirksamkeit", "HAM-D"],
  "summary": "Randomisierte Studie zur Wirksamkeit von Sertralin bei Depression, die eine signifikante Symptomverbesserung gegenüber Placebo belegt.",
  "sentiment": "neutral",
  "category": "Klinische Studie",
  "confidence_score": 0.95
}
"""
        },
        {
            "role": "user",
            "content": """
Titel: Panikattacken im Alltag bewältigen
Inhalt: Wenn das Herz rast und der Atem stockt, hilft oft die 4-7-8 Atemtechnik. Setzen Sie sich hin, atmen Sie tief ein und versuchen Sie, sich auf fünf Dinge im Raum zu konzentrieren, die Sie sehen können. Diese Erdungsübung unterbricht den Angstkreislauf.
"""
        },
        {
            "role": "assistant",
            "content": """
{
  "tags": ["Panikattacke", "Atemtechnik", "Selbsthilfe", "Erdungsübung", "Angstbewältigung", "4-7-8 Methode"],
  "summary": "Ratgeber zur akuten Bewältigung von Panikattacken mittels Atemtechniken und Erdungsübungen.",
  "sentiment": "positive",
  "category": "Ratgeber",
  "confidence_score": 0.98
}
"""
        }
    ]

    @staticmethod
    def build_analysis_prompt(title: str, content: str) -> str:
        return f"Titel: {title}\nInhalt: {content}"