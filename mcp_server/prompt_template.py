
INTENT_PROMPT = """
You are a flight booking assistant. Analyze the user's message below and return **only one** of these intents:
- book
- cancel
- reschedule
- unknown (if the message doesn't match any of the above)

Instructions for the assistant:
1. Always respond with **only the intent**, nothing else—no explanations, punctuation, or extra text.  
2. If the message is unclear or does not relate to flight booking, return "unknown".  
3. Consider variations of words like "change", "modify", "reschedule" as reschedule.  
4. Words like "cancel", "remove", or "delete reservation" should map to cancel.  
5. Words like "book", "reserve", "schedule" should map to book.  
6. Do not infer intents beyond these four categories.  

Here are some examples:

1. "I want to book a flight to New York next Monday." → book  
2. "Please cancel my reservation for flight 123." → cancel  
3. "Can I change my flight from Friday to Sunday?" → reschedule  
4. "What is the weather like in Paris?" → unknown  
5. "I need help with my luggage options." → unknown  

User message: "{user_input}"  
Respond with the intent only, nothing else.
"""


SLOT_PROMPT = """
You are an information extractor. 
Your task is to extract structured flight booking details from the user's message. 

Return **only one JSON object** with the following keys (always include all keys, even if values are unknown):
- passenger_name: string (empty string "" if unknown)
- origin: string (IATA code like "BOM" or city name/short text; "" if unknown)
- destination: string (IATA code like "BLR" or city name/short text; "" if unknown)
- date: string (format "YYYY-MM-DD"; "" if unknown)
- time: string (format "HH:MM"; "" if unknown)
- booking_reference: string ("" if not provided)

⚠️ Rules:
1. Output must be **valid JSON** only, no explanations or extra text.  
2. If multiple dates/times are mentioned, choose the most relevant one for the flight.  
3. Normalize partial inputs:  
   - If only a month/day is mentioned, leave as "" unless a full date can be inferred.  
   - If only "morning/evening" is mentioned, leave time as "".  
4. Do not hallucinate—if unsure, use "".  

Example input and output:

Input: "Book a ticket for Vaishak S from Mumbai to Bangalore on 10th October 2025 at 10:30 AM."  
Output: {{"passenger_name":"Vaishak S","origin":"Mumbai","destination":"Bangalore","date":"2025-10-10","time":"10:30","booking_reference":""}}

Input: "Cancel booking REF1234 for John Doe from BLR to DEL."  
Output: {{"passenger_name":"John Doe","origin":"BLR","destination":"DEL","date":"","time":"","booking_reference":"REF1234"}}

User message:
\"\"\"{user_input}\"\"\"

Respond with the JSON object only.
"""
