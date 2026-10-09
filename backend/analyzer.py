import re
import json
import logging
from typing import Optional, List, Tuple
from fastapi import HTTPException
import anthropic

from .config import settings
from .models import AnalyzeResponse, SentimentResult, ClassificationResult

logger = logging.getLogger("textinsight.analyzer")

SYSTEM_PROMPT = """You are TextInsight, an elite natural language processing and text analytics engine.
Analyze the user's text across 5 dimensions with rigorous precision and deep semantic understanding:

1. SUMMARY (Executive-level, 2-3 sentences):
   - Sentence 1: Primary subject and core event/action (who/what did what).
   - Sentence 2: Critical supporting detail, concrete metrics, or mechanisms (how/why).
   - Sentence 3: Primary implication, outcome, or strategic conclusion.
   - Strict rule: NEVER use meta-openers like "This text discusses...", "The author states...", or "The article describes...". State the direct facts and core takeaways directly and densely.

2. SENTIMENT & CALIBRATED CONFIDENCE SCORE:
   - "label": exactly one of "positive", "negative", or "neutral"
   - "confidence": float between 0.0 and 1.0, strictly calibrated:
     * 0.90 - 1.00: Unanimous, strong polarity throughout without opposing points or conflicting caveats.
     * 0.75 - 0.89: Clear dominant polarity, with minor neutral background or mild reservations.
     * 0.60 - 0.74: Modest polarity slant, with notable conflicting or mixed viewpoints.
     * 0.50 - 0.59: Balanced or ambiguous sentiment with slight directional lean.
   - Evaluate lexical valence, tone consistency, sentiment modifiers, and contrastive conjunctions ("however", "although", "but").

3. CLASSIFICATION & CALIBRATED CONFIDENCE SCORE:
   - "category": strictly one of ["News", "Business", "Technology", "Entertainment", "Sports", "Personal", "Other"]
   - "confidence": float between 0.0 and 1.0, strictly calibrated:
     * 0.90 - 1.00: Unambiguous domain match with dense domain-specific terminology and unmistakable intent.
     * 0.75 - 0.89: Strong primary domain alignment, with minor crossover elements (e.g., tech earnings).
     * 0.50 - 0.74: Multi-disciplinary topic spanning multiple domains or best categorized as Other.

4. KEYWORDS:
   - An array of the top 10 most salient keywords or key phrases. Preserve multi-word entity names (e.g., "Claude 3.5 Sonnet", "quarterly earnings").

5. EXPLANATION:
   - A concise, articulate paragraph (3-4 sentences) explaining:
     a) The specific linguistic and tonal evidence justifying the sentiment label and its confidence score.
     b) The contextual indicators justifying the classification category and its confidence score.

CRITICAL INSTRUCTION:
You must respond ONLY with a single valid JSON object adhering strictly to this schema:
{
  "summary": "2-3 high-density sentences summarizing the core facts.",
  "sentiment": {
    "label": "positive" | "negative" | "neutral",
    "confidence": 0.94
  },
  "keywords": ["kw1", "kw2", "kw3", "kw4", "kw5", "kw6", "kw7", "kw8", "kw9", "kw10"],
  "classification": {
    "category": "News" | "Business" | "Technology" | "Entertainment" | "Sports" | "Personal" | "Other",
    "confidence": 0.95
  },
  "explanation": "Deep reasoning explaining sentiment and classification rationale."
}

Do not include any text, notes, markdown formatting, or wrappers outside the raw JSON object.
"""

def extract_clean_json(text: str) -> str:
    """Strip markdown fences or extraneous text to isolate the JSON string."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return cleaned[first_brace:last_brace + 1]
    return cleaned

# Domain Taxonomies for Advanced Mock Classifier
DOMAIN_TAXONOMY = {
    "Technology": [
        "ai", "software", "hardware", "algorithm", "cloud", "api", "gpu", "chip", "code",
        "developer", "platform", "robotics", "cybersecurity", "compute", "dataset", "llm",
        "neural", "model", "tech", "computer", "digital", "app", "system", "infrastructure",
        "benchmark", "automation", "framework", "programming", "server", "data", "monitor",
        "display", "screen", "refresh rate", "device", "specs", "electronics", "setup"
    ],
    "Business": [
        "revenue", "profit", "acquisition", "quarterly", "shares", "stock", "dividend",
        "merger", "fiscal", "earnings", "market cap", "executive", "ceo", "finance",
        "investment", "investor", "sales", "enterprise", "industry", "commerce", "growth",
        "valuation", "commercial", "margin", "forecast", "balance sheet", "economic"
    ],
    "Sports": [
        "championship", "tournament", "match", "team", "league", "score", "athlete",
        "coach", "victory", "playoffs", "quarterback", "striker", "mvp", "finals", "stadium",
        "player", "win", "won", "defeat", "points", "trophy", "racing", "medal", "olympics"
    ],
    "Entertainment": [
        "film", "movie", "actor", "actress", "cinema", "album", "music", "celebrity",
        "concert", "director", "trailer", "streaming", "hollywood", "series", "television",
        "song", "theater", "show", "artist", "premiere", "box office", "soundtrack", "gaming"
    ],
    "News": [
        "government", "parliament", "minister", "president", "election", "legislation",
        "official", "investigation", "treaty", "policy", "authorities", "broadcast",
        "spokesperson", "diplomatic", "sanctions", "court", "ruling", "public", "state"
    ],
    "Personal": [
        "my", "myself", "i felt", "my day", "family", "friend", "childhood", "personal",
        "feeling", "diary", "vacation", "hobby", "reflection", "heartfelt", "memories",
        "i love", "i think", "i believe", "grateful", "gratefulness", "relationship", "purchased"
    ]
}

def split_into_sentences(text: str) -> List[str]:
    """Split raw text into clean distinct sentences."""
    raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 10]
    return sentences

def extract_smart_summary(text: str, sentences: List[str], dominant_category: str) -> str:
    """
    Produce an information-dense 2-3 sentence summary of the actual input text.
    Uses extractive salience scoring based on position, entities, numbers, and key term density.
    """
    if not sentences:
        return text[:200].strip() + ("..." if len(text) > 200 else "")

    if len(sentences) <= 3:
        return " ".join(sentences)

    # Score sentences based on salience features
    scores: List[Tuple[int, float]] = []
    total_sents = len(sentences)

    for idx, sentence in enumerate(sentences):
        score = 0.0
        # Position weight (first and concluding sentences are typically most salient)
        if idx == 0:
            score += 3.5
        elif idx == 1:
            score += 2.0
        elif idx == total_sents - 1:
            score += 2.5

        # Quantitative/factual weight (numbers, percentages, dates often carry hard information)
        num_matches = len(re.findall(r'\b\d+(?:\.\d+)?%?|\b(?:first|second|quarter|million|billion)\b', sentence, re.IGNORECASE))
        score += num_matches * 1.5

        # Capitalized entity weight
        entities = len(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', sentence))
        score += entities * 0.8

        # Length normalization (favor substantive sentences, penalize extremes)
        words_count = len(sentence.split())
        if 12 <= words_count <= 35:
            score += 1.5

        scores.append((idx, score))

    # Pick top 2 or 3 sentences, ordered by original text flow
    sorted_by_score = sorted(scores, key=lambda x: x[1], reverse=True)
    top_indices = sorted([item[0] for item in sorted_by_score[:3]])
    selected_sentences = [sentences[i] for i in top_indices]

    return " ".join(selected_sentences)

def compute_mock_sentiment(text: str) -> Tuple[str, float, str]:
    """
    Computes sentiment label and calibrated confidence score using contextual valence analysis.
    """
    text_lower = text.lower()
    words = re.findall(r'\b[a-z\'-]+\b', text_lower)

    strong_pos = {
        "exceptional", "breakthrough", "outstanding", "triumph", "revolutionary",
        "magnificent", "masterpiece", "breathtaking", "unprecedented", "flawless",
        "delighted", "exceeded", "stellar", "thrilling", "superb"
    }
    moderate_pos = {
        "good", "great", "positive", "success", "improved", "valuable", "efficient",
        "beneficial", "smooth", "reliable", "happy", "love", "solid", "promising",
        "advantage", "growth", "gain", "worth", "vivid", "resolved"
    }

    strong_neg = {
        "catastrophic", "disaster", "horrible", "awful", "terrible", "devastating",
        "fraud", "ruined", "bankrupt", "crisis", "worst", "unacceptable", "scandal"
    }
    moderate_neg = {
        "bad", "negative", "problem", "issue", "drop", "decline", "fell", "loss",
        "failed", "delay", "risk", "concern", "weak", "downward", "volatility",
        "difficult", "poor", "deficit", "caution"
    }

    negators = {"not", "no", "never", "neither", "hardly", "barely", "scarcely", "without", "failed"}
    intensifiers = {"very", "extremely", "deeply", "highly", "exceptionally", "significantly", "truly"}
    contrast_words = {"however", "although", "despite", "but", "yet", "nevertheless", "nonetheless"}

    pos_score = 0.0
    neg_score = 0.0
    contrast_count = sum(1 for w in words if w in contrast_words)

    for i, word in enumerate(words):
        multiplier = 1.0
        # Check preceding 2 tokens for negation or intensifier
        window = words[max(0, i - 2):i]
        is_negated = any(nw in negators for nw in window)
        is_intensified = any(iw in intensifiers for iw in window)

        if is_intensified:
            multiplier *= 1.5

        if word in strong_pos:
            val = 2.0 * multiplier
            if is_negated:
                neg_score += val
            else:
                pos_score += val
        elif word in moderate_pos:
            val = 1.0 * multiplier
            if is_negated:
                neg_score += val
            else:
                pos_score += val
        elif word in strong_neg:
            val = 2.0 * multiplier
            if is_negated:
                pos_score += val
            else:
                neg_score += val
        elif word in moderate_neg:
            val = 1.0 * multiplier
            if is_negated:
                pos_score += val
            else:
                neg_score += val

    net = pos_score - neg_score
    total_sentiment_density = pos_score + neg_score

    if total_sentiment_density == 0:
        label = "neutral"
        confidence = 0.88
        reason = "Objective reporting tone with factual delivery and absence of strong emotional markers."
    elif net > 0.8:
        label = "positive"
        # Calibrate confidence based on polarization ratio and absence of conflicting markers
        ratio = pos_score / total_sentiment_density
        confidence = min(0.98, max(0.68, 0.70 + (ratio * 0.25) - (contrast_count * 0.06)))
        reason = f"Predominantly affirmative and constructive vocabulary with a positive-to-negative polarity balance of {round(pos_score, 1)} to {round(neg_score, 1)}."
    elif net < -0.8:
        label = "negative"
        ratio = neg_score / total_sentiment_density
        confidence = min(0.98, max(0.68, 0.70 + (ratio * 0.25) - (contrast_count * 0.06)))
        reason = f"Prominent critical, adverse, or declining indicators with an adverse polarity score of {round(neg_score, 1)} versus {round(pos_score, 1)} positive mentions."
    else:
        label = "neutral"
        confidence = max(0.62, 0.85 - (contrast_count * 0.08))
        reason = "Balanced or nuanced statements where positive and negative elements counterbalance each other."

    return label, round(confidence, 2), reason

def compute_mock_classification(text: str) -> Tuple[str, float, str]:
    """
    Computes best-fit category and calibrated confidence score using domain match density.
    """
    text_lower = text.lower()
    scores = {}

    for category, terms in DOMAIN_TAXONOMY.items():
        cat_score = 0.0
        for term in terms:
            # Word boundary regex search
            matches = len(re.findall(r'\b' + re.escape(term) + r'\b', text_lower))
            cat_score += matches * (1.5 if len(term) > 4 else 1.0)
        scores[category] = cat_score

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_cat, top_score = sorted_scores[0]
    runner_up_cat, runner_up_score = sorted_scores[1]

    if top_score < 1.0:
        category = "Other"
        confidence = 0.72
        reason = "General context that does not exhibit a dominant match with specific vertical categories."
    else:
        category = top_cat
        # Calculate confidence based on lead over runner up
        margin = (top_score - runner_up_score) / (top_score + 0.1)
        if margin > 0.5:
            confidence = min(0.96, 0.82 + (margin * 0.15))
            reason = f"High-density domain vocabulary specific to {category} (score: {top_score}) with clear thematic dominance over {runner_up_cat}."
        else:
            confidence = max(0.65, 0.74 + (margin * 0.12))
            reason = f"Classified as {category} based on lead topic indicators, though overlapping with aspects of {runner_up_cat}."

    return category, round(confidence, 2), reason

def extract_top_keywords(text: str) -> List[str]:
    """Extract top 10 keywords and key phrases."""
    stop_words = {
        "this", "that", "with", "from", "have", "were", "been", "they", "their",
        "what", "when", "where", "which", "will", "would", "could", "should",
        "about", "into", "over", "after", "then", "them", "some", "more", "most",
        "than", "also", "very", "just", "such", "only", "even", "made", "make"
    }

    # Extract 2-word proper noun phrases first (e.g., Claude 3.5, Net Earnings)
    phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z0-9][a-z0-9\.]+)\b', text)
    cleaned_phrases = [p for p in phrases if len(p.split()) == 2]

    # Extract single words
    words = re.findall(r'\b[A-Za-z0-9\'-]{4,}\b', text)
    filtered_words = [w for w in words if w.lower() not in stop_words]

    # Count frequencies
    freq = {}
    for p in cleaned_phrases:
        freq[p] = freq.get(p, 0) + 3
    for w in filtered_words:
        freq[w] = freq.get(w, 0) + 1

    sorted_keywords = sorted(freq.keys(), key=lambda k: freq[k], reverse=True)
    results = sorted_keywords[:10]
    while len(results) < 5:
        results.append("insight")
    return results[:10]

def generate_mock_analysis(text: str) -> AnalyzeResponse:
    """Generate high-quality, calibrated analysis response when no API key is provided."""
    sentences = split_into_sentences(text)
    
    # 1. Classification & Calibrated Confidence
    category, cat_confidence, cat_reason = compute_mock_classification(text)

    # 2. Executive Summary
    summary = extract_smart_summary(text, sentences, category)

    # 3. Sentiment & Calibrated Confidence
    sentiment_label, sent_confidence, sent_reason = compute_mock_sentiment(text)

    # 4. Top Keywords
    keywords = extract_top_keywords(text)

    # 5. Composite Explanation
    explanation = (
        f"Sentiment is evaluated as {sentiment_label} with {int(sent_confidence * 100)}% confidence: {sent_reason} "
        f"The content is classified under '{category}' ({int(cat_confidence * 100)}% confidence): {cat_reason}"
    )

    return AnalyzeResponse(
        summary=summary,
        sentiment=SentimentResult(label=sentiment_label, confidence=sent_confidence),
        keywords=keywords,
        classification=ClassificationResult(category=category, confidence=cat_confidence),
        explanation=explanation
    )

async def analyze_text(text: str) -> AnalyzeResponse:
    """
    Analyzes text using the Anthropic Claude API.
    Uses a single structured prompt returning JSON, validates via Pydantic,
    retries once if parsing or validation fails, and returns a clean 500 error if unsuccessful.
    """
    if settings.is_mock_enabled:
        logger.info("MOCK_MODE enabled: Producing high-precision simulated analysis.")
        return generate_mock_analysis(text)

    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY is not configured. Please set ANTHROPIC_API_KEY in backend/.env"
        )

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Anthropic client: {e}")
        raise HTTPException(status_code=500, detail=f"Anthropic client error: {str(e)}")

    user_message = f"Please analyze the following text:\n\n{text}"
    messages = [{"role": "user", "content": user_message}]

    last_error: Optional[str] = None
    max_attempts = 2

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"Sending analysis request to Anthropic Claude (attempt {attempt}/{max_attempts})")
            response = client.messages.create(
                model=settings.anthropic_model,
                max_tokens=1500,
                temperature=0.15,
                system=SYSTEM_PROMPT,
                messages=messages
            )

            raw_text = response.content[0].text if response.content else ""
            cleaned_json_str = extract_clean_json(raw_text)

            # Validate against Pydantic model
            validated_response = AnalyzeResponse.model_validate_json(cleaned_json_str)
            return validated_response

        except Exception as err:
            last_error = str(err)
            logger.warning(f"Attempt {attempt} failed validation/parsing: {last_error}")

            if attempt < max_attempts:
                messages.append({"role": "assistant", "content": raw_text if 'raw_text' in locals() else ""})
                messages.append({
                    "role": "user",
                    "content": (
                        f"Your previous response failed validation with error:\n{last_error}\n\n"
                        "Please regenerate the response as strictly valid JSON matching the exact schema."
                    )
                })

    logger.error(f"All {max_attempts} attempts failed. Returning clean 500 error.")
    raise HTTPException(
        status_code=500,
        detail=f"Failed to parse and validate LLM analysis response after retry. Error: {last_error}"
    )
