class PromptTemplates:

    # --- SECTION 1: ARTICLE ANALYSIS PROMPTS ---

    ARTICLE_SYSTEM_PROMPT = """
You are an expert academic psychologist and data scientist.
Your task is to analyze psychological texts (abstracts or full texts) and extract deep semantic metadata.

Output Requirement:
- You must output valid JSON only.
- Identify 15 to 40 semantic tags. These must include specific disorders, therapies, chemicals (if applicable), and methodologies.
- Classify the scientific disciplines (e.g., 'Klinische Psychologie', 'Neuropsychologie').
- Determine the sentiment and category.

Language:
The output (summary, tags, disciplines) must be in German, regardless of the input language.
"""

    ARTICLE_FEW_SHOTS = [
        {
            "role": "user",
            "content": "Titel: Cognitive Behavioral Therapy for Insomnia (CBT-I) in Older Adults.\nInhalt: This study evaluates the efficacy of CBT-I in a sample of 150 adults aged 65+. Results indicate significant improvement in sleep latency and efficiency compared to the control group receiving sleep hygiene education alone."
        },
        {
            "role": "assistant",
            "content": """
{
  "tags": ["Insomnie", "Schlafstörungen", "Kognitive Verhaltenstherapie", "CBT-I", "Ältere Erwachsene", "Gerontopsychologie", "Schlaflatenz", "Schlafeffizienz", "Randomisierte kontrollierte Studie", "Schlafhygiene", "Nicht-medikamentöse Therapie", "Alter", "Wirksamkeitsstudie", "Klinische Intervention", "Psychotherapie"],
  "scientific_disciplines": ["Klinische Psychologie", "Gerontopsychologie", "Schlafforschung"],
  "summary": "Studie zur Wirksamkeit der Kognitiven Verhaltenstherapie bei Insomnie (CBT-I) bei über 65-Jährigen, die signifikante Verbesserungen gegenüber reiner Schlafhygiene-Schulung zeigt.",
  "sentiment": "positive",
  "category": "Klinische Studie",
  "confidence_score": 0.98
}
"""
        }
    ]

    # --- SECTION 2: SEARCH QUERY ANALYSIS PROMPTS ---

    SEARCH_SYSTEM_PROMPT = """
You are an intelligent search assistant for a psychological database.
Your goal is to interpret user queries, which may be vague, colloquial, or contain typos, and translate them into precise search tags.

Output Requirement:
- You must output valid JSON only.
- Generate 2 to 8 precise search tags that maximize the chance of finding relevant professional literature.
- Infer the user's intent (e.g., 'research', 'self_help', 'emergency').
- If the query implies acute danger (suicide, self-harm), set intent to 'emergency'.
- Correct typos in the 'corrected_query' field.

Language:
Tags must be in German.
"""

    SEARCH_FEW_SHOTS = [
        {
            "role": "user",
            "content": "hilfee bei angs atacken"
        },
        {
            "role": "assistant",
            "content": """
{
  "tags": ["Angststörung", "Panikattacke", "Angstbewältigung", "Akuthilfe", "Symptome"],
  "intent": "self_help",
  "corrected_query": "Hilfe bei Angstattacken"
}
"""
        },
        {
            "role": "user",
            "content": "studien über wirksamkeit von ssri bei jugendlichen"
        },
        {
            "role": "assistant",
            "content": """
{
  "tags": ["SSRI", "Antidepressiva", "Jugendliche", "Adoleszenz", "Wirksamkeit", "Pharmakotherapie", "Depression"],
  "intent": "research",
  "corrected_query": "Studien über Wirksamkeit von SSRI bei Jugendlichen"
}
"""
        }
    ]

    @staticmethod
    def build_article_prompt(title: str, content: str) -> str:
        return f"Titel: {title}\nInhalt: {content}"

    @staticmethod
    def build_search_prompt(query: str) -> str:
        return f"Suchanfrage: {query}"