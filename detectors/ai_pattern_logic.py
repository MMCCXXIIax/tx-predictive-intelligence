
```python
# ai_pattern_logic.py

from pattern_registry import pattern_registry

def detect_all_patterns(candles):
    results = []

    # Enhanced pattern detection logic using GPT-4o
    for detect in pattern_registry:
        try:
            result = detect(candles)

            if result and result.get("detected", False):
                pattern_name = (
                    result.get("pattern") or
                    result.get("pattern_name") or
                    result.get("pattern_type") or
                    "Unknown GPT-4o Pattern"
                )
                category = result.get("pattern_category", "Unknown")
                index = result.get("index", len(candles) - 1)
                confidence = result.get("confidence", None)
                explanation = result.get("explanation", "No explanation provided.")
                candle_time = (
                    candles[index]["time"]
                    if 0 <= index < len(candles) and "time" in candles[index]
                    else None
                )

                results.append({
                    "name": pattern_name,
                    "category": category,
                    "index": index,
                    "confidence": confidence,
                    "explanation": explanation,
                    "candle_time": candle_time
                })

        except Exception as e:
            # Log or handle exception
            continue

    return results
```
