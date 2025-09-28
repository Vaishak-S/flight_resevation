from llm_adapter import generate_response, USE_MOCK_LLM

def run_tests():
    print("=== Testing generate_response ===")
    test_inputs = [
        "I want to book a flight from NYC to LA",
        "Cancel my reservation please",
        "Can I reschedule my ticket to tomorrow?",
        "What's the weather today?",
    ]

    for user_input in test_inputs:
        intent = generate_response(user_input)
        print(f"Input: {user_input}\n -> Intent: {intent}\n")


if __name__ == "__main__":
    run_tests()
