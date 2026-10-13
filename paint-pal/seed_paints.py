"""Seed script to populate Firestore 'paints' collection."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-ff10d3da2b21"

PAINTS = [
    {
        "id": "paint-1",
        "name": "Ocean Breeze",
        "hex_code": "#A8D0E6",
        "price_inr": 1250,
        "mood": "calm",
        "suitable_rooms": ["bedroom", "bathroom", "study"],
    },
    {
        "id": "paint-2",
        "name": "Sage Whisper",
        "hex_code": "#B2C9AB",
        "price_inr": 1400,
        "mood": "calm",
        "suitable_rooms": ["bedroom", "living room", "study"],
    },
    {
        "id": "paint-3",
        "name": "Serene Lavender",
        "hex_code": "#C8A2C8",
        "price_inr": 1300,
        "mood": "calm",
        "suitable_rooms": ["bedroom", "nursery", "bathroom"],
    },
    {
        "id": "paint-4",
        "name": "Sunrise Coral",
        "hex_code": "#F28E79",
        "price_inr": 1600,
        "mood": "energetic",
        "suitable_rooms": ["kitchen", "dining room", "living room"],
    },
    {
        "id": "paint-5",
        "name": "Mustard Radiance",
        "hex_code": "#E3A857",
        "price_inr": 1500,
        "mood": "energetic",
        "suitable_rooms": ["living room", "kitchen", "dining room"],
    },
    {
        "id": "paint-6",
        "name": "Electric Teal",
        "hex_code": "#008080",
        "price_inr": 1750,
        "mood": "energetic",
        "suitable_rooms": ["home office", "living room", "study"],
    },
    {
        "id": "paint-7",
        "name": "Warm Terracotta",
        "hex_code": "#D97443",
        "price_inr": 1350,
        "mood": "cozy",
        "suitable_rooms": ["living room", "dining room", "bedroom"],
    },
    {
        "id": "paint-8",
        "name": "Velvet Mocha",
        "hex_code": "#5C4033",
        "price_inr": 1800,
        "mood": "cozy",
        "suitable_rooms": ["bedroom", "study", "living room"],
    },
    {
        "id": "paint-9",
        "name": "Amber Glow",
        "hex_code": "#FFBF00",
        "price_inr": 1450,
        "mood": "cozy",
        "suitable_rooms": ["dining room", "living room", "hallway"],
    },
    {
        "id": "paint-10",
        "name": "Rustic Olive",
        "hex_code": "#556B2F",
        "price_inr": 1650,
        "mood": "cozy",
        "suitable_rooms": ["study", "living room", "dining room"],
    },
]


def seed():
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("paints")
    print(f"Seeding paints into project '{PROJECT_ID}'...")
    for paint in PAINTS:
        doc_id = paint["id"]
        doc_data = {k: v for k, v in paint.items() if k != "id"}
        collection_ref.document(doc_id).set(doc_data)
        print(f"  Added {paint['name']} ({paint['hex_code']})")
    print("Seeding complete! 10 paints added.")


if __name__ == "__main__":
    seed()
