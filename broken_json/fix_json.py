from json_repair import repair_json
import json

# 1. Read the corrupted file
with open("broken.json", "r", encoding="utf-8") as f:
    corrupted_data = f.read()

# 2. Repair it (return_objects=False keeps it as a formatted JSON string)
fixed_data = repair_json(corrupted_data, return_objects=False)

# 3. Validate and save
try:
    parsed = json.loads(fixed_data)
    with open("fixed.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2)
    print("✅ Success! JSON is now valid. Submit the contents of fixed.json")
except json.JSONDecodeError as e:
    print(f"❌ Still broken at line {e.lineno}, column {e.colno}: {e.msg}")
    print("👉 Paste lines {} to {} of broken.json in your next prompt so we can surgically fix it.".format(max(1, e.lineno-5), e.lineno+5))