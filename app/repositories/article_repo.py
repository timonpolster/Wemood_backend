class ArticleRepository:
    """Repository für CRUD-Operationen und Suchfunktionen auf der Articles-Tabelle."""

    def __init__(self, session: AsyncSession):
        """Initialisiert das Repository mit einer async Datenbank-Session."""
        self.session = session

    async def create_with_ai_analysis(
            self, article_in: ArticleCreate, ai_data: ArticleAnalysisResult
    ) -> Article:
        """Erstellt einen Artikel mit zugehöriger KI-Analyse und persistiert ihn."""

    async def get_by_id(self, article_id: int) -> Optional[Article]:
        """Gibt einen Artikel anhand seiner ID zurück oder None."""

    async def get_all(
            self,
            skip: int = 0,
            limit: int = 100
    ) -> Tuple[List[Article], int]:
        """Gibt eine paginierte Artikelliste und die Gesamtanzahl zurück."""

    async def update(
            self,
            article_id: int,
            article_update: ArticleUpdate
    ) -> Optional[Article]:
        """Aktualisiert die Metadaten eines Artikels. Gibt None zurück falls nicht gefunden."""

    async def delete(self, article_id: int) -> bool:
        """Löscht einen Artikel. Gibt True bei Erfolg, False falls nicht gefunden."""

    async def hybrid_search(
            self,
            query_text: str,
            query_tags: List[str],
            limit: int = 20,
            fulltext_weight: float = 0.4,
            tag_weight: float = 0.6,
            min_score: float = 0.01
    ) -> List[Tuple[Article, float, dict]]:
        """Kombinierte Suche aus PostgreSQL-Volltext und semantischem Tag-Matching mit gewichteter Bewertung."""

    async def search_by_overlap_coefficient(
            self, query_tags: List[str], limit: int = 15, threshold: float = 0.05
    ) -> List[Tuple[Article, float]]:
        """Sucht Artikel anhand des Overlap-Koeffizienten zwischen Query-Tags und Artikel-Tags."""