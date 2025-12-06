# Template Sense Performance Analysis

**Date:** 2025-12-05
**Test File:** `tests/fixtures/live_test_invoice.xlsx`
**Field Dictionary:** Tako header fields (21) + column fields (19)

---

## Executive Summary

**Total Processing Time:** 32.80 seconds
**API Time:** 9.89 seconds (30.1% of total)
**Non-API Time:** 22.92 seconds (69.9% of total)
**Number of API Calls:** 3

### Key Finding
The system makes **3 identical API calls** to OpenAI, each with the exact same payload (9,363 chars). This is the primary optimization opportunity.

---

## Detailed Breakdown

### API Calls (9.89s total, 30.1% of processing time)

| Call # | Function | Duration | Payload Size | Notes |
|--------|----------|----------|--------------|-------|
| 1 | `classify_fields` | 3.05s | 9,363 chars | Header classification |
| 2 | `classify_fields` | 3.39s | 9,363 chars | Column classification |
| 3 | `classify_fields` | 3.45s | 9,363 chars | Line item extraction |

**Issue:** All three calls send the **exact same payload** to the AI provider.

### Non-API Processing Time (22.92s, 69.9% of total)

This includes:
- Excel file loading (openpyxl)
- Heuristic header detection
- Heuristic table detection
- Sheet structure analysis
- Fuzzy matching
- Translation
- Output serialization

---

## Root Cause Analysis

### Where the 3 API Calls Originate

**File:** `src/template_sense/pipeline/stages/ai_classification.py`

The AI Classification stage executes 3 **sequential** calls:

```python
# Stage 6a: Classify header fields
context.classified_headers = classify_header_fields(
    context.ai_provider, context.ai_payload
)

# Stage 6b: Classify table columns
context.classified_columns = classify_table_columns(
    context.ai_provider, context.ai_payload
)

# Stage 6c: Extract line items
context.extracted_line_items = extract_line_items(
    context.ai_provider, context.ai_payload
)
```

Each function uses `AIClassificationOrchestrator` which calls:
```python
response = ai_provider.classify_fields(payload, context=self.context)
```

**The Problem:**
- Same `ai_payload` sent 3 times
- Same `classify_fields` method called 3 times
- Only difference is the `context` parameter ("headers", "columns", "line_items")
- The AI must parse the entire payload 3 times separately

---

## Optimization Opportunities

### 🎯 Priority 1: Combine API Calls (HIGHEST IMPACT)

**Current State:** 3 sequential API calls
**Proposed State:** 1 combined API call

**Expected Savings:**
- **Network overhead:** ~400-600ms (eliminating 2 round-trips)
- **AI processing:** ~2-4s (AI parses payload once instead of 3 times)
- **Total estimated savings:** ~2.4-4.6 seconds (7-14% of total time)

**Implementation Strategy:**

**Option A: Batch Request Format**
```python
# Instead of 3 separate calls, make 1 call:
response = ai_provider.classify_all_fields(
    payload=context.ai_payload,
    tasks=["headers", "columns", "line_items"]
)

# Response structure:
{
    "headers": [...],
    "columns": [...],
    "line_items": [...]
}
```

**Option B: Enhanced classify_fields with Multiple Contexts**
```python
response = ai_provider.classify_fields(
    payload=context.ai_payload,
    contexts=["headers", "columns", "line_items"]  # List instead of single string
)
```

**Recommendation:** Option A is cleaner and more explicit.

**Files to Modify:**
1. `src/template_sense/ai_providers/interface.py` - Add `classify_all_fields` method
2. `src/template_sense/ai_providers/openai_provider.py` - Implement batching
3. `src/template_sense/ai_providers/anthropic_provider.py` - Implement batching
4. `src/template_sense/pipeline/stages/ai_classification.py` - Use batch method
5. Update AI prompt templates to handle batch classification

---

### 🎯 Priority 2: Optimize Non-API Processing (22.92s)

**Current State:** 69.9% of time spent on non-AI operations

**Investigation Needed:**
1. **Excel Loading:** How long does openpyxl take?
2. **Heuristic Detection:** How long for header/table detection?
3. **Fuzzy Matching:** How many comparisons are being made?
4. **Serialization:** Is JSON serialization slow?

**Action Items:**
- Add timing instrumentation to each pipeline stage
- Profile hot paths with cProfile
- Consider caching common patterns

**Potential Optimizations:**
```python
# Profile each stage
with TimingContext("Excel Loading"):
    workbook = load_workbook(...)

with TimingContext("Header Detection"):
    headers = detect_headers(...)

with TimingContext("Fuzzy Matching"):
    matched = fuzzy_match(...)
```

---

### 🎯 Priority 3: Reduce Payload Size

**Current State:** 9,363 characters sent 3 times

**Opportunities:**
1. **Remove duplicate data** - Field dictionary sent in full each time
2. **Compress cell values** - Only send necessary cell data
3. **Smart sampling** - For large sheets, sample instead of full data

**Estimated Savings:** 10-20% reduction in API time (1-2 seconds)

---

### 🎯 Priority 4: Parallel Processing

**Current State:** Sequential API calls (even if kept separate)

**Proposed State:** Parallel execution
```python
import asyncio

async def classify_all():
    results = await asyncio.gather(
        classify_header_fields_async(...),
        classify_table_columns_async(...),
        extract_line_items_async(...)
    )
    return results
```

**Expected Savings:** 6-7 seconds (only pay for longest call, not sum of all)

**Note:** This is **less impactful** than combining calls, but easier to implement.

---

## Recommended Implementation Plan

### Phase 1: Quick Wins (1-2 days)
1. ✅ **Add detailed timing instrumentation** to all pipeline stages
2. 🎯 **Implement batch API call** to reduce 3 calls to 1
3. 📊 **Measure impact** and validate savings

**Expected Result:** 2-5 second reduction (6-15% faster)

### Phase 2: Deep Optimization (3-5 days)
1. 🔍 **Profile non-API processing** to find bottlenecks
2. 🗜️ **Optimize payload size** by removing redundant data
3. ⚡ **Cache common patterns** (e.g., field dictionary translations)

**Expected Result:** Additional 2-4 second reduction (total 10-20% faster)

### Phase 3: Advanced (if needed)
1. 🔄 **Implement async/parallel processing** for independent operations
2. 📦 **Add result caching** for repeated template analyses
3. 🎯 **Smart sampling** for very large spreadsheets

**Expected Result:** Additional 3-5 second reduction (total 20-30% faster)

---

## Metrics to Track

### Current Baseline
- Total time: **32.80s**
- API time: **9.89s** (30.1%)
- Non-API time: **22.92s** (69.9%)
- API calls: **3**

### Target After Phase 1
- Total time: **~28-30s** (10-15% improvement)
- API time: **~5-7s** (1 call instead of 3)
- Non-API time: **22-23s** (unchanged)
- API calls: **1**

### Target After Phase 2
- Total time: **~23-26s** (20-30% improvement)
- API time: **~4-5s** (optimized payload)
- Non-API time: **~18-20s** (optimized processing)
- API calls: **1**

---

## Test Results

### Extraction Results
- **Header fields detected:** 2
- **Table columns detected:** 0
- **Line items extracted:** 0
- **Recovery events:** 11

**Note:** Low detection rate suggests potential issues with:
1. Heuristic detection algorithms
2. AI classification prompts
3. Confidence thresholds

This should be investigated separately from performance optimization.

---

## Files to Review

### Critical Path (Performance Impact)
1. `src/template_sense/pipeline/stages/ai_classification.py` - **3 API calls here**
2. `src/template_sense/ai_providers/openai_provider.py` - API implementation
3. `src/template_sense/ai/base_classification.py` - Orchestrator
4. `src/template_sense/adapters/excel_adapter.py` - Excel loading (22s mystery)

### Supporting Files
- `src/template_sense/ai/header_classification.py`
- `src/template_sense/ai/table_column_classification.py`
- `src/template_sense/ai/line_item_extraction.py`
- `src/template_sense/mapping/fuzzy_field_matching.py`

---

## Conclusion

**Primary Issue:** The system makes **3 separate API calls with identical payloads** when it could make 1 combined call.

**Quick Win:** Implement batch API classification to reduce from 3 calls to 1.

**Expected Impact:** 2-5 second reduction (6-15% faster) with minimal code changes.

**Next Steps:**
1. Implement `classify_all_fields` batch method
2. Update pipeline to use batch method
3. Profile non-API processing to understand the 22.92s mystery
