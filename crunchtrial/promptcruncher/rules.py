"""
Rules for promptcruncher's rule-based compression stage.
These are patterns that add tokens but not meaning.
"""

# Exact phrases to strip (case-insensitive)
FILLER_PHRASES = [
    # Pleasantries
    "hello there",
    "sure, ",
    "sure! ",
    "certainly! ",
    "certainly, ",
    "of course! ",
    "of course, ",
    "absolutely! ",
    "absolutely, ",
    "happy to help!",
    "happy to help.",
    "happy to assist!",
    "happy to assist.",
    "glad to help!",
    "glad to help.",
    "i'd be happy to",
    "i'd be glad to",
    "i'd love to help",
    "no problem!",
    "no problem.",
    "great question!",
    "great question.",
    "that's a great question.",
    "that's a good question.",
    "good question!",
    "good question.",
    "thanks for asking!",
    "thanks for reaching out!",
    "thank you for your question.",
    "thank you for asking.",

    # AI self-references
    "as an ai language model,",
    "as an ai,",
    "as a language model,",
    "as an artificial intelligence,",
    "i'm an ai, so",
    "i am an ai, so",

    # Preamble throat-clearing
    "let me help you with that.",
    "let me help you.",
    "let me assist you with that.",
    "i'll help you with that.",
    "i can help you with that.",
    "i can help with that.",
    "i can certainly help with that.",
    "i'll do my best to help.",
    "i would be absolutely more than happy to help",
    "allow me to help.",
    "i understand. ",
    "i understand! ",
    "i see. ",
    "i see! ",
    "of course, i'd be happy to",

    # Closing filler
    "i hope this helps!",
    "i hope this helps.",
    "i hope that helps!",
    "i hope that helps.",
    "let me know if you have any questions!",
    "let me know if you have any other questions!",
    "let me know if you need anything else!",
    "feel free to ask if you have more questions.",
    "please let me know if you need further assistance.",
    "don't hesitate to ask.",
    "is there anything else i can help you with?",
    "is there anything else you'd like to know?",
]

# Regex patterns to strip (filler openers and transitions)
FILLER_PATTERNS = [
    # "In order to X" → "To X"
    r"in order to\b",

    # "It is important to note that" → ""
    r"it(?:'s| is) (?:important|worth(?:while)?) to note that\b,?\s*",
    r"it(?:'s| is) (?:important|worth(?:while)?) to (?:mention|highlight|point out) that\b,?\s*",
    r"it(?:'s| is) (?:also )?worth noting that\b,?\s*",
    r"it should be noted that\b,?\s*",
    r"please note that\b,?\s*",

    # "Basically / essentially / simply"
    r"\bbasically\b,?\s*",
    r"\bessentially\b,?\s*",
    r"\bsimply\b(?! put)",  # keep "simply put" as it changes meaning
    r"\bjust\b(?= \w)",     # "just do X" → "do X" (careful not to strip meaningful uses)

    # "In this case" / "in this scenario"
    r"\bin this (?:case|scenario|situation|context)\b,?\s*",

    # "As I mentioned" / "As stated"
    r"\bas (?:I (?:mentioned|said|noted|discussed)|(?:mentioned|stated|discussed) (?:earlier|above|previously))\b,?\s*",
    r"\bas previously (?:mentioned|noted|stated|discussed)\b,?\s*",

    # "What this means is"
    r"\bwhat this means is\b,?\s*",
    r"\bwhat I mean (?:is|by this) is\b,?\s*",

    # "The fact that"
    r"\bthe fact that\b",

    # Verbose question openers
    r"^(?:could you (?:please )?)?(?:help me |tell me |explain |describe |provide |give me )?(?:a (?:brief |quick |short |detailed )?)?(?:overview|explanation|description|summary) of\b,?\s*",

    # "I would like to" / "I want to"
    r"\bI would like(?: you)? to\b",
    r"\bI am looking(?: for you)? to\b",
]

# Verbose sentence openers that add nothing
REDUNDANT_OPENERS = [
    r"^(?:so,?\s+)?(?:to (?:answer|address) your question,?\s*)",
    r"^(?:first(?:ly)?|to begin(?: with)?),?\s+(?=I|we|let)",
    r"^(?:in conclusion|to summarize|to sum up|in summary),?\s+",
    r"^(?:moving on|furthermore|additionally|moreover),?\s+",
]

# Generic openings
# Targets generic openers: [Greeting] [Helper Phrase] [Today/Now]
GENERIC_OPENERS = [
    r"^(?:hello|hi|hey|greetings|good (?:morning|afternoon|evening))\b.*?[.!?]\s*",
    r"^(?:i(?:'d| would) be|i am) (?:happy|glad|more than happy) to help.*?[.!?]\s*",
]

# Targets generic closers: [Hope this helps] [Let me know] [Have a good day]
GENERIC_CLOSERS = [
    r"(?:i hope|hope) (?:this|that) (?:helps|is helpful).*?[.!?]$",
    r"(?:let me know|feel free to ask) if you (?:have|need).*?[.!?]$",
    r"have a (?:wonderful|great|nice) (?:day|afternoon|evening).*?[.!?]$"
]
