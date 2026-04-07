class PromptTemplates:
    """Zentrale Prompt-Verwaltung für die Mistral-AI-Aufrufe zur Artikel- und Suchanfragen-Analyse."""

    # --- SECTION 1: ARTICLE ANALYSIS PROMPTS ---

    ARTICLE_SYSTEM_PROMPT = """
You are an expert academic psychologist and data scientist.
Your task is to analyze psychological texts (abstracts or full texts) and extract deep semantic metadata.

Output Requirement:
- You must output valid JSON only.
- Generate 20 to 50 semantic tags following these MANDATORY CATEGORIES:

  1. DISORDERS/CONDITIONS: Specific diagnoses (e.g., "Depression", "PTBS", "Generalisierte Angststörung", "Schizophrenie")
  2. SYMPTOMS: Observable signs (e.g., "Schlafstörung", "Grübeln", "Konzentrationsprobleme", "Erschöpfung")
  3. TREATMENTS: Therapies and interventions (e.g., "Kognitive Verhaltenstherapie", "EMDR", "Achtsamkeit", "Pharmakotherapie")
  4. POPULATIONS: Target groups (e.g., "Jugendliche", "Ältere Erwachsene", "Kinder", "Schwangere")
  5. METHODS: Research methodology (e.g., "Randomisierte kontrollierte Studie", "Metaanalyse", "Längsschnittstudie")
  6. MEDICATIONS: If applicable (e.g., "SSRI", "Benzodiazepine", "Antipsychotika", "Lithium")
  7. GENERAL CONCEPTS: Psychological constructs (e.g., "Resilienz", "Selbstwirksamkeit", "Emotionsregulation")
  8. SYNONYMS: Include German AND common English terms (e.g., both "Achtsamkeit" AND "Mindfulness")

- Always include BROADER and NARROWER terms (e.g., if about "Panikstörung", also tag "Angststörung" and "Psychische Störung")
- Include common abbreviations as separate tags (e.g., "KVT" AND "Kognitive Verhaltenstherapie")
- Classify the scientific disciplines (e.g., 'Klinische Psychologie', 'Neuropsychologie').
- Determine the sentiment and category.

Language:
The output (summary, tags, disciplines) must be in German, with common English psychology terms included where applicable.
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
  "tags": ["Insomnie", "Schlafstörung", "Schlaflosigkeit", "Kognitive Verhaltenstherapie", "KVT", "CBT-I", "CBT", "Verhaltenstherapie", "Psychotherapie", "Ältere Erwachsene", "Senioren", "Alter", "Gerontopsychologie", "Schlaflatenz", "Schlafeffizienz", "Schlafqualität", "Einschlafstörung", "Durchschlafstörung", "Randomisierte kontrollierte Studie", "RCT", "Schlafhygiene", "Nicht-medikamentöse Therapie", "Wirksamkeitsstudie", "Klinische Intervention", "Psychologische Behandlung", "Evidenzbasiert", "Kontrollgruppe", "Therapieerfolg"],
  "scientific_disciplines": ["Klinische Psychologie", "Gerontopsychologie", "Schlafforschung", "Verhaltensmedizin"],
  "summary": "Randomisierte kontrollierte Studie zur Wirksamkeit der Kognitiven Verhaltenstherapie bei Insomnie (CBT-I) bei Erwachsenen über 65 Jahren. Die Ergebnisse zeigen signifikante Verbesserungen bei Schlaflatenz und Schlafeffizienz im Vergleich zur Kontrollgruppe, die nur Schlafhygiene-Schulung erhielt.",
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
Your goal is to interpret user queries, which may be vague, colloquial, or contain typos, and translate them into comprehensive search tags.

Output Requirement:
- You must output valid JSON only.
- Generate 8 to 15 search tags to MAXIMIZE search coverage using this strategy:

  TAG GENERATION STRATEGY:
  1. EXACT TERMS: Direct matches to user's query
  2. SYNONYMS: Alternative words for same concept (e.g., "Traurigkeit" → "Niedergeschlagenheit", "Schwermut")
  3. BROADER TERMS: More general categories (e.g., "Panikattacke" → "Angststörung" → "Psychische Störung")
  4. NARROWER TERMS: More specific variants (e.g., "Angst" → "Generalisierte Angststörung", "Soziale Phobie")
  5. RELATED CONCEPTS: Associated topics (e.g., "Depression" → "Antriebslosigkeit", "Hoffnungslosigkeit")
  6. TREATMENTS: If help is implied (e.g., add "Therapie", "Behandlung", "Selbsthilfe")
  7. ABBREVIATIONS: Common short forms (e.g., "PTBS", "ADHS", "KVT", "DBT")

- Infer the user's intent:
  * 'research': Academic/scientific interest
  * 'self_help': Personal help seeking
  * 'emergency': Acute crisis (suicide, self-harm)
  * 'general_info': General curiosity

- EMERGENCY DETECTION - Set intent to 'emergency' if query contains:
  * Suicidal ideation ("will nicht mehr leben", "Suizid", "umbringen", "keinen Sinn mehr")
  * Self-harm ("selbst verletzen", "ritzen", "Selbstverletzung")
  * Acute crisis ("keinen Ausweg", "kann nicht mehr", "alles beenden")
  
- Correct typos in the 'corrected_query' field.

Language:
Tags must be in German.
"""

    SEARCH_FEW_SHOTS = [
        {
            "role": "user",
            "content": "Suchanfrage: hilfee bei angs atacken"
        },
        {
            "role": "assistant",
            "content": """
{
  "tags": ["Panikattacke", "Angstattacke", "Panikstörung", "Angststörung", "Angst", "Panik", "Angstbewältigung", "Akuthilfe", "Selbsthilfe", "Angstsymptome", "Atemübungen", "Entspannungstechniken", "Psychische Krise"],
  "intent": "self_help",
  "corrected_query": "Hilfe bei Angstattacken"
}
"""
        },
        {
            "role": "user",
            "content": "Suchanfrage: studien über wirksamkeit von ssri bei jugendlichen"
        },
        {
            "role": "assistant",
            "content": """
{
  "tags": ["SSRI", "Selektive Serotonin-Wiederaufnahmehemmer", "Antidepressiva", "Jugendliche", "Adoleszenz", "Teenager", "Wirksamkeit", "Wirksamkeitsstudie", "Pharmakotherapie", "Depression", "Medikamentöse Behandlung", "Klinische Studie", "Psychopharmaka", "Nebenwirkungen"],
  "intent": "research",
  "corrected_query": "Studien über Wirksamkeit von SSRI bei Jugendlichen"
}
"""
        },
        {
            "role": "user",
            "content": "Suchanfrage: ich will nicht mehr leben alles ist sinnlos"
        },
        {
            "role": "assistant",
            "content": """
{
  "tags": ["Suizidalität", "Suizidgedanken", "Suizidprävention", "Lebensmüdigkeit", "Hoffnungslosigkeit", "Krise", "Krisenintervention", "Depression", "Psychische Krise", "Notfall", "Akuthilfe", "Telefonseelsorge"],
  "intent": "emergency",
  "corrected_query": "Suizidgedanken - Krisenhilfe"
}
"""
        },
        {
            "role": "user",
            "content": "Suchanfrage: trauma bei kindern"
        },
        {
            "role": "assistant",
            "content": """
{
  "tags": ["Trauma", "Kindheitstrauma", "PTBS", "Posttraumatische Belastungsstörung", "Kinder", "Kindheit", "Traumatherapie", "EMDR", "Traumafolgestörung", "Entwicklungstrauma", "Kinderpsychologie", "Traumatisierung", "Belastende Kindheitserfahrungen"],
  "intent": "general_info",
  "corrected_query": "Trauma bei Kindern"
}
"""
        }
    ]

    @staticmethod
    def build_article_prompt(title: str, content: str) -> str:
        """Baut den User-Prompt für die Artikelanalyse aus Titel und Inhalt."""
        return f"Titel: {title}\nInhalt: {content}"

    @staticmethod
    def build_search_prompt(query: str) -> str:
        """Baut den User-Prompt für die Suchanfragen-Analyse."""
        return f"Suchanfrage: {query}"