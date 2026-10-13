# My agent: PaintPal
One-liner: A conversational agent that helps homeowners and renters choose wall paint colors based on room type and desired mood with a curated catalog of paints.

Tool coverage:
- Memory: Remembers user's room types, preferred moods, and chosen paint colors across sessions
- Tools: Look up matching paints from a Firestore collection (filtered by mood and suitable rooms)
- Catalog/UI: Catalog of ~10 paints (name, hex code, price in INR, mood, suitable rooms) displayed as cards
- Image gen: Optional visualization of the chosen room painted in the selected shade
- Sandbox: Paint quantity and total cost calculation based on room square footage (stretch)

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Room area paint cost calculator, image generation for room previews
