# test_llm_adapter.py
from llm_adapter import generate_intent, llm_extract_slots, USE_MOCK_LLM

tests = [
    "Book flight for Vaishak S from BOM to BLR on 2025-10-10 at 10:30",
    "Please cancel my booking BK-20250928-abc12345",
    "Reschedule BK-20250928-abc12345 to 2025-10-12 08:00",
    "I want to reserve a ticket from DEL to MAA on 2025-11-03 15:15. Name is John Doe"
]

print("USE_MOCK_LLM:", USE_MOCK_LLM)
for t in tests:
    intent = generate_intent(t)
    print(f"Input: {t}\n -> Intent: {intent}")
    slots = llm_extract_slots(t)
    print(" -> Slots:", slots)
    print("----")
