import random
import re

# --- PII and Non-PII Entity Pools ---
ENTITY_POOLS = {
    "TRAIN": {
        "CREDIT_CARD": ["4242424242424242", "5555111122223333", "378282246310005", "6011987654321012", "5105105105105100"],
        "PHONE": ["9876543210", "9123456789", "9098765432", "9988776655", "9112233445", "8005550199"],
        "EMAIL": ["ramesh.sharma@gmail.com", "priyanka.verma@outlook.com", "anil.kumar@yahoo.com", "sita.devi@gmail.com", "neha.gupta@hotmail.com"],
        "PERSON_NAME": ["Ramesh Sharma", "Priyanka Verma", "Anil Kumar", "Sita Devi", "Rajesh Singh", "Neha Gupta"],
        "DATE": ["01/02/2024", "15/08/2023", "25/12/2024", "07/04/2025", "11/11/2023"],
        "CITY": ["Mumbai", "Chennai", "Bangalore", "Delhi", "Hyderabad", "Pune"],
        "LOCATION": ["123 main street, building A", "corner of elm and pine", "behind the blue warehouse", "third floor, office 404"]
    },
    "DEV": {
        # Using a completely separate set of entities for the DEV set to ensure unbiased evaluation
        "CREDIT_CARD": ["4000123456789012", "5432109876543210", "340011223344556", "6221000011112222", "4100000000000000"],
        "PHONE": ["7700112233", "8899001122", "9001122334", "6543210987", "9012345678"],
        "EMAIL": ["john.doe@work.co", "jane.smith@edu.in", "customer.service@app.net", "sales_team@corp.org"],
        "PERSON_NAME": ["Vinay Rao", "Kavita Mehta", "Deepak Kumar", "Tanya Sen", "Arjun Nair", "Sanjana Reddy"],
        "DATE": ["02/03/2026", "20/10/2025", "30/01/2026", "04/06/2024", "22/09/2024"],
        "CITY": ["Kolkata", "Ahmedabad", "Jaipur", "Lucknow", "Surat", "Kanpur"],
        "LOCATION": ["456 oak avenue, side entrance", "near the gas station", "inside the mall food court", "first building on the right"]
    }
}

# Common STT Filler/Noise words
FILLERS = ["uh", "um", "you know", "like", "I mean", "well", "so", "actually"]

# Digit noise mapping for PII
DIGIT_MAP = {
    '0': ['oh', 'zero'],
    '1': ['one', 'wun'],
    '2': ['two', 'too'],
    '3': ['three'],
    '4': ['four', 'for'],
    '5': ['five'],
    '6': ['six'],
    '7': ['seven'],
    '8': ['eight'],
    '9': ['nine']
}

SYMBOL_MAP = {
    '@': [' at ', ' sign ', ' at sign '],
    '.': [' dot ', ' period ', ' full stop '],
    '-': [' dash ', ' hyphen ', ' minus '],
    '/': [' slash ', ' forward slash '],
    ' ': [' space ', ' gap ']
}

# --- Noise Injection Functions ---

def inject_fillers(text: str) -> str:
    """Inserts random STT fillers into the text."""
    tokens = text.split()
    # Inject noise in about 10-20% of spaces
    k = max(1, len(tokens) // 5)
    noise_positions = random.sample(range(len(tokens) + 1), k=k)
    for pos in sorted(noise_positions, reverse=True):
        tokens.insert(pos, random.choice(FILLERS))
    return " ".join(tokens)

def noisify_pii(clean_value: str, entity_type: str) -> str:
    """Applies specialized, heavy noise based on PII entity type."""
    
    noisy_value = clean_value.lower()
    
    # CREDIT_CARD / PHONE: Heavy Digit Spacing and Symbol Replacement
    if entity_type in ["CREDIT_CARD", "PHONE"]:
        temp_chars = []
        for char in noisy_value:
            if char.isdigit():
                # Spelled out or sometimes left as digit (less common in STT)
                if random.random() < 0.8:
                    temp_chars.append(random.choice(DIGIT_MAP.get(char, [char])))
                else:
                    temp_chars.append(char)
                temp_chars.append(random.choice([' ', ' ', ' '])) # Add spaces between digits
            elif char in SYMBOL_MAP:
                temp_chars.append(random.choice(SYMBOL_MAP[char]))
            else:
                temp_chars.append(char)
        noisy_value = "".join(temp_chars).strip()
        
    # EMAIL: Heavy Symbol replacement and character spelling
    elif entity_type == "EMAIL":
        for symbol, spoken_words in SYMBOL_MAP.items():
            noisy_value = noisy_value.replace(symbol, random.choice(spoken_words))
        
        # Sometimes spell out the first part of the email address
        if random.random() < 0.3:
            local_part = noisy_value.split(random.choice([' at ', ' at sign ']))[0]
            if len(local_part) > 5:
                # Spell out part of the user name
                spelled_part = ' '.join(list(local_part.replace('.', '').replace('_', '')))
                noisy_value = noisy_value.replace(local_part, spelled_part, 1)

    # PERSON_NAME: Phonetic errors (very difficult to automate, so use simple misspellings)
    elif entity_type == "PERSON_NAME":
        # Simple phonetic misspellings for common names
        name_map = {"ramesh": "ra mesh", "priyanka": "prianca", "anil": "a nil", "sita": "seeta"}
        for k, v in name_map.items():
            if k in noisy_value:
                noisy_value = noisy_value.replace(k, v)
    
    # DATE: Full spelling or date artifacts
    elif entity_type == "DATE":
        # Convert date format 01/02/2024 to 'january second two thousand twenty four'
        parts = re.split(r'[/.\s-]', clean_value)
        if len(parts) == 3:
            day, month, year = parts
            
            # Simple conversion to spelled-out numbers
            day_str = ' '.join([DIGIT_MAP[d][0] for d in day if d.isdigit()])
            month_str = ' '.join([DIGIT_MAP[d][0] for d in month if d.isdigit()])
            year_str = ' '.join([DIGIT_MAP[d][0] for d in year if d.isdigit()])
            
            # Randomly choose between pure number spelling or month/day words
            date_templates = [
                f"{day_str} {month_str} {year_str}", 
                f"the {day_str} of {month_str} {year_str}"
            ]
            noisy_value = random.choice(date_templates)
            
    # Non-PII (CITY, LOCATION): mostly lowercase and simple misspellings
    elif entity_type in ["CITY", "LOCATION"]:
        # Simple phonetic errors
        if random.random() < 0.2:
            noisy_value = noisy_value.replace('a', 'ah').replace('e', 'eh')
            
    # Final cleanup: ensure it's fully lowercase and normalize whitespace
    noisy_value = re.sub(r'\s+', ' ', noisy_value).strip()
    return noisy_value

def apply_full_stt_noise(text: str) -> str:
    """Applies common STT post-processing (mostly just lowercasing) and filler injection."""
    text = text.lower()
    text = inject_fillers(text)
    text = re.sub(r'\s+', ' ', text).strip() # Normalize spaces
    return text

def find_offset_after_noise(base_text: str, base_entity: str, noisy_entity: str):
    """
    Finds the start and end offsets of the noisy_entity within the final noisy text.
    Assumes the entity is unique or the base_text/base_entity context helps.
    """
    
    # 1. Create a placeholder to guarantee findability
    placeholder = "___ENTITY_PLACEHOLDER___"
    
    # 2. Insert placeholder into base text
    if base_entity not in base_text:
        # This shouldn't happen with correct templates
        return -1, -1 
        
    base_text_with_ph = base_text.replace(base_entity, placeholder, 1)
    
    # 3. Noisify the full text with placeholder
    # NOTE: We can't use apply_full_stt_noise because it calls inject_fillers 
    # which shifts indices randomly. We must apply noise *around* the entity.
    
    # Split around the entity for noise injection in the context
    pre_entity, post_entity = base_text_with_ph.split(placeholder)
    
    # Reconstruct the final noisy text
    noisy_pre = apply_full_stt_noise(pre_entity).strip()
    noisy_post = apply_full_stt_noise(post_entity).strip()
    
    # Handle edge case where entity is at the start or end
    if not noisy_pre:
        final_noisy_text = f"{noisy_entity} {noisy_post}".strip()
        start = 0
    else:
        final_noisy_text = f"{noisy_pre} {noisy_entity} {noisy_post}".strip()
        # Find start index by finding the noisy entity in the final text
        start = final_noisy_text.find(noisy_entity)
        
    end = start + len(noisy_entity)
    
    return final_noisy_text, start, end

# --- Sentence Templates (Different sets for Train and Dev) ---
TEMPLATES = {
    "TRAIN": [
        ("hi this is {PERSON_NAME} my credit card number is {CREDIT_CARD} and email address is {EMAIL}", ["PERSON_NAME", "CREDIT_CARD", "EMAIL"]),
        ("please call me at {PHONE} i am currently in {CITY} traveling on {DATE}", ["PHONE", "CITY", "DATE"]),
        ("my email is {EMAIL} and phone number {PHONE} belongs to my office {LOCATION}", ["EMAIL", "PHONE", "LOCATION"]),
        ("i made a payment using my card {CREDIT_CARD} yesterday on {DATE}", ["CREDIT_CARD", "DATE"]),
        ("contact {PERSON_NAME} by email {EMAIL} or phone {PHONE} for details", ["PERSON_NAME", "EMAIL", "PHONE"]),
        ("i'll be in {CITY} on {DATE} reachable at {PHONE} outside the building {LOCATION}", ["CITY", "DATE", "PHONE", "LOCATION"]),
        ("my card {CREDIT_CARD} will expire on {DATE}", ["CREDIT_CARD", "DATE"]),
        ("the meeting with {PERSON_NAME} is on {DATE} in {CITY}", ["PERSON_NAME", "DATE", "CITY"]),
    ],
    "DEV": [
        ("can you find {PERSON_NAME} email which is {EMAIL} and the number is {PHONE}", ["PERSON_NAME", "EMAIL", "PHONE"]),
        ("the delivery address is {LOCATION} in {CITY} scheduled for {DATE}", ["LOCATION", "CITY", "DATE"]),
        ("i need to block card {CREDIT_CARD} and notify {PERSON_NAME}", ["CREDIT_CARD", "PERSON_NAME"]),
        ("my contact information is {PHONE} and email is {EMAIL}", ["PHONE", "EMAIL"]),
        ("confirm the charge of twenty dollars on {DATE} with card {CREDIT_CARD}", ["DATE", "CREDIT_CARD"]),
        ("the conference is located at {LOCATION} in {CITY}", ["LOCATION", "CITY"]),
        ("i am {PERSON_NAME} and i will be travelling on {DATE}", ["PERSON_NAME", "DATE"]),
    ]
}

def get_pools(mode: str):
    return ENTITY_POOLS[mode], TEMPLATES[mode]