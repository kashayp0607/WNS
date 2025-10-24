"""
Sensitive words and topics for content moderation
"""

# Offensive and inappropriate words
BAD_WORDS = [
    # Racial and ethnic slurs
    "nigger", "nigga", "chink", "spic", "kike", "gook", "wetback",
    
    # LGBTQ+ slurs
    "fag", "faggot", "dyke", "tranny", "shemale",
    
    # Gender-based insults
    "bitch", "cunt", "whore", "slut", "skank",
    
    # Severe profanity
    "fuck", "shit", "asshole", "bastard", "motherfucker", "bullshit",
    "piss", "damn", "dick", "cock", "pussy", "twat",
    
    # Disability insults
    "retard", "retarded", "cripple", "midget", "mongoloid",
    
    # Hate speech
    "kill all", "death to", "exterminate", "purge", "white power",
    
    # Self-harm
    "suicide", "kill yourself", "self harm", "cutting", "hang yourself"
]

SENSITIVE_TOPICS = {
    'religion': [
        'god', 'jesus', 'christ', 'allah', 'buddha', 'muhammad', 'prophet',
        'pray', 'prayer', 'church', 'mosque', 'temple', 'synagogue',
        'bible', 'quran', 'torah', 'holy', 'saint', 'angel', 'devil'
    ],
    'tragedy_violence': [
        'death', 'dead', 'kill', 'murder', 'suicide', 'cancer', 'tumor',
        'rape', 'abuse', 'molest', 'pedophile', 'violence', 'assault',
        'holocaust', 'genocide', 'terrorism', 'bomb', 'shoot', 'massacre'
    ],
    'race_ethnicity': [
        'racist', 'racism', 'black', 'white', 'asian', 'hispanic',
        'jew', 'jewish', 'nazi', 'hitler', 'kkk', 'supremacy',
        'ethnic cleansing', 'segregation', 'discrimination'
    ],
    'disability_health': [
        'disabled', 'retarded', 'handicapped', 'autistic', 'down syndrome',
        'mental illness', 'depression', 'anxiety', 'bipolar', 'schizophrenia',
        'aids', 'hiv', 'cancer', 'covid', 'pandemic'
    ],
    'politics': [
        'trump', 'biden', 'republican', 'democrat', 'liberal', 'conservative',
        'socialist', 'communist', 'fascist', 'election', 'government',
        'political party', 'left-wing', 'right-wing'
    ],
    'gender_sexuality': [
        'feminist', 'lgbtq', 'transgender', 'gay', 'lesbian', 'bisexual',
        'homosexual', 'sexist', 'misogynist', 'patriarchy', 'gender',
        'non-binary', 'pansexual', 'queer'
    ]
}

# Contexts where sensitive words might be allowed
ALLOWED_CONTEXTS = {
    'kill': ['time', 'appetite', 'pain', 'bugs', 'process', 'program'],
    'dead': ['battery', 'phone', 'line', 'silence', 'end', 'tired'],
    'shoot': ['photo', 'movie', 'film', 'basketball', 'goal'],
    'virus': ['computer', 'antivirus', 'protection', 'scan'],
    'attack': ['heart', 'panic', 'website', 'network'],
    'crash': ['computer', 'car', 'market', 'website']
}