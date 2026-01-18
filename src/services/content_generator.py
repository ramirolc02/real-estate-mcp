"""Content generator service using Jinja2 templates."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.exceptions import ContentGenerationError, PropertyNotFoundError


class ContentGeneratorService:
    """Service for generating SEO-optimized HTML content for property listings."""

    def __init__(self, template_dir: Path | None = None):
        if template_dir is None:
            template_dir = Path(__file__).parent.parent.parent / "templates"

        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,
        )

    async def generate_listing_html(
        self,
        property_data: dict,
        target_language: str = "en",
        tone: str | None = None,
    ) -> str:
        """Generate SEO-optimized HTML content for a property listing.

        Args:
            property_data: Full property data dictionary
            target_language: Target language code (e.g., 'en', 'pt')
            tone: Content tone (professional, casual, luxury)

        Returns:
            Generated HTML content string
        """
        if not property_data:
            raise PropertyNotFoundError("unknown")

        tone = tone or "professional"

        try:
            template = self.env.get_template("listing.html.j2")

            # In production, this would call an LLM API
            # For now, template provides realistic structure with mock descriptions
            generated_description = self._mock_description(property_data, tone, target_language)

            return template.render(
                property=property_data,
                language=target_language,
                tone=tone,
                generated_description=generated_description,
            )
        except Exception as e:
            raise ContentGenerationError(str(e)) from e

    def _mock_description(self, prop: dict, tone: str, language: str) -> str:
        """Generate a mock LLM description based on tone and language.

        In production, this would be replaced with actual LLM API call.
        """
        property_type = prop.get("property_type", "property")
        city = prop.get("city", "the area")
        bedrooms = prop.get("bedrooms", 0)
        features = prop.get("features", [])

        # English descriptions
        if language == "en":
            tones = {
                "professional": (
                    f"This exceptional {property_type} in {city} offers {bedrooms} "
                    f"bedrooms and outstanding features including "
                    f"{', '.join(features[:3]) if features else 'modern amenities'}. "
                    f"An excellent opportunity for discerning buyers seeking quality "
                    f"and location."
                ),
                "casual": (
                    f"Check out this amazing {property_type} in {city}! "
                    f"It has {bedrooms} bedrooms and comes with awesome features like "
                    f"{', '.join(features[:3]) if features else 'great amenities'}. "
                    f"Perfect for anyone looking for their dream home!"
                ),
                "luxury": (
                    f"An extraordinary residence of unparalleled distinction in {city}. "
                    f"This magnificent {property_type} presents {bedrooms} exquisitely "
                    f"appointed bedrooms, complemented by world-class amenities including "
                    f"{', '.join(features[:3]) if features else 'exceptional finishes'}. "
                    f"A rare opportunity for the most discerning clientele."
                ),
            }
        # Portuguese descriptions
        elif language == "pt":
            tones = {
                "professional": (
                    f"Este excepcional {property_type} em {city} oferece {bedrooms} "
                    f"quartos e características notáveis incluindo "
                    f"{', '.join(features[:3]) if features else 'comodidades modernas'}. "
                    f"Uma excelente oportunidade para compradores exigentes."
                ),
                "casual": (
                    f"Veja este incrível {property_type} em {city}! "
                    f"Tem {bedrooms} quartos e vem com ótimas características como "
                    f"{', '.join(features[:3]) if features else 'ótimas comodidades'}. "
                    f"Perfeito para quem procura a casa dos sonhos!"
                ),
                "luxury": (
                    f"Uma residência extraordinária de distinção incomparável em {city}. "
                    f"Este magnífico {property_type} apresenta {bedrooms} quartos "
                    f"requintados, complementados por comodidades de classe mundial. "
                    f"Uma oportunidade rara para a clientela mais exigente."
                ),
            }
        else:
            # Default to English for unsupported languages
            tones = {
                "professional": f"A quality {property_type} in {city} with {bedrooms} bedrooms.",
                "casual": f"Great {property_type} in {city}!",
                "luxury": f"An exceptional {property_type} in {city}.",
            }

        return tones.get(tone, tones["professional"])
