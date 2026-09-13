## References

**Step 3: Metadata Annotation**
Each test case includes:
```json
{
  "test_id": "KR_FOOD_001",
  "culture": "Korean",
  "domain": "food",
  "entity": "kimchi",
  "prompt": "Generate an image of kimchi, a traditional food from Korea",
  "wikidata_id": "Q42527",
  "expected_attributes": ["fermented", "cabbage", "red color", "jar container"],
  "generation_method": "automated_kg",
  "validation_status": "pending"
}
```

**Output:** 50-100 test cases per culture (1000-2000 total for 20-culture pilot)