
BOT_USER_ID = 7789911596
TARGET_CHANNEL_ID = 2083186778
TEST_TARGET_CHANNEL_ID = 4579383411
DESTINATION_GROUP_ID = "-4576581744" # Specific formatfor groups id

USERNAMES_TO_TRACK = [
    "Wizard Of SoHo",
    "uaiaiaia"
]
WORDS_TO_TRACK = [
    "earl",
    "sibert"
]

def conditions(username, text):
    # Convert text and tracked words to lowercase for case-insensitive comparison
    text_lower = text.lower()
    return (username in USERNAMES_TO_TRACK or 
            any(word.lower() in text_lower for word in WORDS_TO_TRACK))
