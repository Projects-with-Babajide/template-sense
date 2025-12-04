# AI Semantic Matching Layer - Design Document

**Created:** 2025-12-04
**Author:** Template Sense Team
**Status:** Proposed Enhancement
**Related Issues:** CO.xlsx field matching failures

---

## Problem Statement

### Current Issue

The fuzzy matching layer uses **literal string similarity** (RapidFuzz) to match translated field labels to Tako's canonical field dictionary. This works well for similar strings but fails for **semantically equivalent** but lexically different terms.

**Example from CO.xlsx:**

| Detected Label | Should Match To | Current Match Score | Status |
|----------------|-----------------|---------------------|--------|
| FROM | shipper | 33.3% | ❌ Failed |
| TO | consignee | 40.0% | ❌ Failed |
| SHIPMENT DAY | etd | 52.6% | ❌ Failed |
| TRANSPORTATION | - | 48.0% | ❌ Failed |

These fields are **semantically identical** but fuzzy string matching can't recognize that:
- "FROM" means the same as "shipper" in logistics context
- "TO" means the same as "consignee" in shipping context
- "SHIPMENT DAY" is the estimated time of departure (ETD)

### Impact

- **Match Rate:** Currently 48% header match rate across templates
- **User Experience:** Tako must manually map semantically equivalent fields
- **Lost Value:** AI already correctly extracted the fields, but mapping fails at the last step

---

## Proposed Solution: AI Semantic Matching Layer

Add an **optional AI-powered semantic matching layer** that activates when fuzzy matching fails to meet the threshold.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Current Pipeline                            │
└─────────────────────────────────────────────────────────────────┘

Translation → Fuzzy Matching → Output

┌─────────────────────────────────────────────────────────────────┐
│                     Enhanced Pipeline                           │
└─────────────────────────────────────────────────────────────────┘

Translation → Fuzzy Matching → AI Semantic Matching → Output
                     ↓                    ↑
                  Match?               Fallback
                  (≥80%)               (<80%)
```

### When to Use AI Semantic Matching

**Trigger Conditions:**
1. Fuzzy match score < threshold (default: 80%)
2. Best fuzzy match score > minimum threshold (e.g., 30%) - shows some similarity
3. AI semantic matching is enabled in config
4. Field is a header field (not a column field initially)

**Do NOT Use AI If:**
- Fuzzy match already succeeded (≥80%)
- Best fuzzy score is very low (<30%) - likely a genuinely unmatchable field
- AI semantic matching is disabled
- Already processed by AI semantic matching (prevent infinite loops)

---

## Implementation Design

### 1. New Module: `src/template_sense/mapping/semantic_field_matching.py`

```python
"""
AI-powered semantic field matching for fields that fail fuzzy matching.

This module provides an optional AI-based fallback layer that uses semantic
understanding to match fields when literal string similarity is insufficient.
"""

from dataclasses import dataclass
from typing import Any

from template_sense.ai_providers.interface import AIProvider
from template_sense.mapping.fuzzy_field_matching import FieldMatchResult


@dataclass
class SemanticMatchResult:
    """
    Result of AI semantic matching.

    Attributes:
        original_text: Original field label from template
        translated_text: Translated English label
        canonical_key: Best matched canonical key (or None)
        semantic_confidence: AI's confidence in the match (0.0-1.0)
        reasoning: Brief explanation from AI (optional)
        fuzzy_fallback_score: Original fuzzy match score for comparison
    """
    original_text: str
    translated_text: str
    canonical_key: str | None
    semantic_confidence: float
    reasoning: str | None
    fuzzy_fallback_score: float


def semantic_match_field(
    translated_label: str,
    field_dictionary: dict[str, list[str]],
    ai_provider: AIProvider,
    best_fuzzy_score: float,
    context: dict[str, Any] | None = None,
    confidence_threshold: float = 0.7,
) -> SemanticMatchResult:
    """
    Use AI to semantically match a field label to canonical dictionary.

    This function is called when fuzzy matching fails to meet the threshold.
    It asks the AI to determine if the translated label is semantically
    equivalent to any canonical field in Tako's dictionary.

    Args:
        translated_label: The translated field label to match
        field_dictionary: Tako's canonical field dictionary
        ai_provider: AI provider instance for semantic matching
        best_fuzzy_score: The best fuzzy match score (for context)
        context: Optional context about the field (invoice type, location, etc.)
        confidence_threshold: Minimum AI confidence to accept match (default: 0.7)

    Returns:
        SemanticMatchResult with the AI's best match or None if no match
    """
    pass


def semantic_match_fields_batch(
    unmatched_fields: list[FieldMatchResult],
    field_dictionary: dict[str, list[str]],
    ai_provider: AIProvider,
    confidence_threshold: float = 0.7,
) -> list[SemanticMatchResult]:
    """
    Batch process multiple unmatched fields through semantic matching.

    More efficient than calling semantic_match_field() individually.
    """
    pass
```

### 2. AI Prompt Design

```python
# Prompt for semantic field matching
SEMANTIC_MATCHING_PROMPT = """
You are a field mapping expert for invoice processing. Your task is to determine if a field label from an invoice template is semantically equivalent to any field in Tako's canonical field dictionary.

**Field to Match:**
- Translated Label: "{translated_label}"
- Best Fuzzy Match Score: {fuzzy_score}%
- Context: {context}

**Tako's Canonical Fields:**
{field_dictionary_formatted}

**Instructions:**
1. Determine if the translated label is semantically equivalent to ANY canonical field
2. Consider:
   - Business domain context (invoices, shipping, logistics)
   - Common synonyms and abbreviations
   - Language conventions (e.g., "FROM" = shipper in logistics)
   - Intent and purpose of the field
3. If there's a semantic match, return the canonical key and your confidence (0.0-1.0)
4. If no semantic match exists, return null

**Examples:**
- "FROM" → "shipper" (logistics sender)
- "TO" → "consignee" (logistics receiver)
- "SHIPMENT DAY" → "etd" (estimated time of departure)
- "INV NO" → "invoice_number" (invoice identifier)
- "TRANSPORTATION" → "terms_of_delivery" (shipping method)

**Response Format (JSON):**
{{
  "canonical_key": "shipper" or null,
  "confidence": 0.95,
  "reasoning": "Brief explanation"
}}

**Important:**
- Only match if you're confident (≥0.7)
- When in doubt, return null
- Consider the invoice/logistics domain context
"""
```

### 3. Integration Point

Update `src/template_sense/mapping/fuzzy_field_matching.py`:

```python
def match_fields(
    translated_labels: list[TranslatedLabel],
    field_dictionary: dict[str, list[str]],
    threshold: float = DEFAULT_AUTO_MAPPING_THRESHOLD,
    ai_provider: AIProvider | None = None,  # NEW: Optional AI provider
    enable_semantic_matching: bool = False,  # NEW: Feature flag
    semantic_confidence_threshold: float = 0.7,  # NEW: AI confidence threshold
) -> list[FieldMatchResult]:
    """
    Match translated labels to canonical field keys using fuzzy matching,
    with optional AI semantic matching fallback.

    NEW: If enable_semantic_matching=True and ai_provider is provided,
    fields that fail fuzzy matching will be passed to AI for semantic matching.
    """
    results = []

    for label in translated_labels:
        # Try fuzzy matching first
        fuzzy_result = _fuzzy_match_single(label, field_dictionary, threshold)

        # If fuzzy match succeeded, use it
        if fuzzy_result.canonical_key is not None:
            results.append(fuzzy_result)
            continue

        # If fuzzy match failed and AI semantic matching is enabled
        if (enable_semantic_matching
            and ai_provider is not None
            and fuzzy_result.match_score >= 30.0):  # Has some similarity

            semantic_result = semantic_match_field(
                translated_label=label.translated_text,
                field_dictionary=field_dictionary,
                ai_provider=ai_provider,
                best_fuzzy_score=fuzzy_result.match_score,
                confidence_threshold=semantic_confidence_threshold,
            )

            # If AI found a semantic match, use it
            if (semantic_result.canonical_key is not None
                and semantic_result.semantic_confidence >= semantic_confidence_threshold):

                # Convert to FieldMatchResult format
                enhanced_result = FieldMatchResult(
                    original_text=fuzzy_result.original_text,
                    translated_text=fuzzy_result.translated_text,
                    canonical_key=semantic_result.canonical_key,
                    match_score=semantic_result.semantic_confidence * 100,  # Convert to 0-100 scale
                    matched_variant=f"AI Semantic Match: {semantic_result.reasoning}",
                )
                results.append(enhanced_result)
                logger.info(
                    f"AI semantic match: '{label.translated_text}' → '{semantic_result.canonical_key}' "
                    f"(confidence: {semantic_result.semantic_confidence:.2%})"
                )
                continue

        # No match found (fuzzy or semantic)
        results.append(fuzzy_result)

    return results
```

### 4. Configuration

Add to `src/template_sense/constants.py`:

```python
# AI Semantic Matching Configuration
ENABLE_AI_SEMANTIC_MATCHING = False  # Feature flag (default: disabled)
SEMANTIC_MATCHING_CONFIDENCE_THRESHOLD = 0.7  # Minimum AI confidence (0.7 = 70%)
SEMANTIC_MATCHING_FUZZY_FLOOR = 30.0  # Minimum fuzzy score to attempt semantic match
```

Add environment variables:

```bash
TEMPLATE_SENSE_ENABLE_SEMANTIC_MATCHING=true  # Enable AI semantic matching
TEMPLATE_SENSE_SEMANTIC_CONFIDENCE=0.7         # Confidence threshold
```

---

## Expected Results

### CO.xlsx Example (With AI Semantic Matching)

**Before (Fuzzy Only):**
```json
{
  "detected_label": "FROM",
  "cell_value": "NARITA JAPAN",
  "canonical_key": null,
  "best_match_score": 33.33
}
```

**After (Fuzzy + AI Semantic):**
```json
{
  "detected_label": "FROM",
  "cell_value": "NARITA JAPAN",
  "canonical_key": "shipper",
  "match_score": 95.0,
  "matched_variant": "AI Semantic Match: 'FROM' indicates sender/shipper in logistics context"
}
```

### Expected Match Rate Improvement

| Template | Current Match Rate | With AI Semantic | Improvement |
|----------|-------------------|------------------|-------------|
| 11.15.xlsx | 25% headers | ~40-50% | +15-25% |
| CO.xlsx | 0% headers | ~75-100% | +75-100% |
| Invoice template copy | 100% headers | 100% | No change |
| NA-25078 | 64% headers | ~80-90% | +16-26% |

**Overall Expected:** 48% → **65-75%** header match rate (+35-55% improvement)

---

## Cost & Performance Considerations

### API Cost

- **When Used:** Only for fields that fail fuzzy matching (typically 10-50% of fields)
- **Batch Processing:** Can batch multiple fields in a single API call
- **Typical Usage:** 2-5 unmatched fields per template = 1 AI call
- **Cost per Template:** ~$0.001-0.003 (assuming GPT-4o pricing)

### Performance Impact

- **Additional Time:** ~2-5 seconds per template (1 AI call for batch matching)
- **Total Pipeline Time:** 15-60s → 17-65s (10-15% increase)
- **Acceptable?** Yes - semantic matching significantly improves match rate

### Optimization Options

1. **Caching:** Cache AI semantic matches by (translated_label, field_dict_hash)
2. **Batch Processing:** Send all unmatched fields in a single API call
3. **Progressive Enhancement:** Only enable for templates with <60% match rate
4. **Field Type Filtering:** Only use for header fields initially (not columns)

---

## Implementation Phases

### Phase 1: Core Implementation (Week 1)
- [ ] Create `semantic_field_matching.py` module
- [ ] Implement `semantic_match_field()` function
- [ ] Design and test AI prompt
- [ ] Add configuration constants
- [ ] Write unit tests

### Phase 2: Integration (Week 1-2)
- [ ] Integrate into `fuzzy_field_matching.py`
- [ ] Update `extraction_pipeline.py` to pass AI provider
- [ ] Add feature flag and environment variables
- [ ] Update E2E test scripts

### Phase 3: Testing & Validation (Week 2)
- [ ] Test on CO.xlsx (FROM, TO, SHIPMENT DAY)
- [ ] Test on all 4 E2E templates
- [ ] Measure match rate improvement
- [ ] Measure cost and performance impact
- [ ] Create comparison report

### Phase 4: Optimization (Week 3)
- [ ] Implement caching layer
- [ ] Optimize batch processing
- [ ] Add telemetry and logging
- [ ] Document best practices

---

## Alternative Approaches Considered

### 1. **Expand Field Dictionary with More Variants**
- **Pro:** No AI cost, deterministic
- **Con:** Impossible to cover all synonyms; brittle; maintenance burden
- **Decision:** Do this PLUS AI semantic matching

### 2. **Use Embedding-Based Matching (Vector Search)**
- **Pro:** Fast, no AI calls at runtime
- **Con:** Requires pre-computed embeddings; harder to explain matches; less flexible
- **Decision:** Consider for future optimization

### 3. **Rule-Based Synonym Dictionary**
- **Pro:** Fast, deterministic, no AI cost
- **Con:** Brittle, doesn't handle context; maintenance burden
- **Decision:** Not sufficient alone; AI handles context better

### 4. **LLM-Based Matching with Explanations** ✅ **SELECTED**
- **Pro:** Understands context; handles novel cases; explainable; flexible
- **Con:** AI API cost; slight performance overhead
- **Decision:** Best balance of accuracy, flexibility, and explainability

---

## Success Metrics

### Primary Metrics
- **Header Match Rate:** Target 65-75% (from 48%)
- **Column Match Rate:** Target 65-70% (from 58%)
- **Overall Match Rate:** Target 68-72% (from 53%)

### Secondary Metrics
- **Processing Time:** <20% increase (acceptable)
- **API Cost:** <$0.005 per template (acceptable)
- **False Positive Rate:** <5% (AI incorrectly matches unrelated fields)
- **User Satisfaction:** Reduce manual mapping effort by 30-40%

### Validation
- Run E2E tests on all 4 templates with semantic matching enabled
- Compare before/after match rates
- Review false positives manually
- Measure cost and performance impact

---

## Risks & Mitigations

### Risk 1: AI False Positives
**Description:** AI might incorrectly match semantically different fields
**Mitigation:**
- Set confidence threshold high (≥0.7)
- Require AI to provide reasoning
- Log all semantic matches for audit
- Add validation layer

### Risk 2: Cost Overrun
**Description:** AI API costs could accumulate for high-volume usage
**Mitigation:**
- Cache matches aggressively
- Batch process fields
- Feature flag to disable per-customer
- Monitor costs with alerts

### Risk 3: Performance Degradation
**Description:** Additional AI calls slow down pipeline
**Mitigation:**
- Batch multiple fields in single call
- Async processing where possible
- Timeout limits (5s max)
- Progressive enhancement (only if needed)

### Risk 4: Inconsistent Matching
**Description:** AI might give different results for same input
**Mitigation:**
- Use temperature=0 for deterministic results
- Cache matches
- Log and audit matches
- Fallback to fuzzy match if AI fails

---

## Open Questions

1. **Batch Size:** How many unmatched fields should we batch per AI call? (Recommendation: All unmatched fields per template)

2. **Caching Strategy:** Should we cache by (translated_label) or (translated_label, field_dict_hash)? (Recommendation: Include field_dict_hash)

3. **Column Fields:** Should we enable semantic matching for column fields too, or headers only? (Recommendation: Start with headers, expand to columns in Phase 2)

4. **Confidence Threshold:** Is 0.7 (70%) the right threshold? (Recommendation: Start at 0.7, adjust based on false positive rate)

5. **Provider Support:** Should we implement for both OpenAI and Anthropic? (Recommendation: Yes, use same interface)

---

## Example Implementation: CO.xlsx Test Case

```python
# Test case: Semantic matching for CO.xlsx fields
def test_semantic_matching_co_xlsx():
    # Setup
    field_dict = {
        "shipper": ["Shipper", "Sender", "From", "Consignor"],
        "consignee": ["Consignee", "Receiver", "To", "Recipient"],
        "etd": ["ETD", "Estimated Time of Departure", "Departure Date"],
    }

    unmatched_fields = [
        FieldMatchResult(
            original_text="FROM",
            translated_text="FROM",
            canonical_key=None,
            match_score=33.3,
            matched_variant=None
        ),
        FieldMatchResult(
            original_text="TO",
            translated_text="TO",
            canonical_key=None,
            match_score=40.0,
            matched_variant=None
        ),
        FieldMatchResult(
            original_text="SHIPMENT DAY",
            translated_text="Shipment Day",
            canonical_key=None,
            match_score=52.6,
            matched_variant=None
        ),
    ]

    # Act: Apply semantic matching
    ai_provider = get_ai_provider()
    results = semantic_match_fields_batch(
        unmatched_fields=unmatched_fields,
        field_dictionary=field_dict,
        ai_provider=ai_provider,
        confidence_threshold=0.7
    )

    # Assert
    assert results[0].canonical_key == "shipper"
    assert results[0].semantic_confidence >= 0.9
    assert "FROM" in results[0].reasoning.lower()

    assert results[1].canonical_key == "consignee"
    assert results[1].semantic_confidence >= 0.9
    assert "TO" in results[1].reasoning.lower()

    assert results[2].canonical_key == "etd"
    assert results[2].semantic_confidence >= 0.8
    assert "shipment" in results[2].reasoning.lower()
```

---

## Conclusion

AI semantic matching is a **high-value, low-risk enhancement** that addresses the core limitation of fuzzy string matching. By adding this optional layer, we can:

1. **Improve match rates** from 48% to 65-75% (+35-55% improvement)
2. **Reduce manual mapping** effort for Tako users
3. **Handle novel field names** that aren't in the dictionary
4. **Provide explainability** through AI reasoning

The implementation is **backward compatible** (feature flag), **cost-effective** (<$0.005/template), and **performant** (<20% overhead).

**Recommendation:** Proceed with Phase 1 implementation and validate with CO.xlsx and other E2E templates.

---

## Next Steps

1. **Review this design** with the team
2. **Create Linear ticket** for implementation (e.g., BAT-60)
3. **Implement Phase 1** (core semantic matching module)
4. **Test with CO.xlsx** to validate approach
5. **Measure results** and iterate

---

**End of Design Document**
