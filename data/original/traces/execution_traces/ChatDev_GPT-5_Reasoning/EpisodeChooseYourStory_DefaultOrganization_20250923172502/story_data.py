'''
Structured story data defining nodes, narrative text, choices, conditions, and effects.
'''
STORY = {
    "start": "intro",
    "nodes": {
        "intro": {
            "text": (
                "You awaken within the ancient castle of Aster. Rumors speak of a hidden artifact "
                "and a guard who can be friend or foe. Your choices will shape your fate."
            ),
            "choices": [
                {
                    "text": "Explore the courtyard.",
                    "target": "courtyard",
                    "effects": {"vars_delta": {"bravery": 1}}
                },
                {
                    "text": "Approach the castle guard.",
                    "target": "guard",
                }
            ]
        },
        "courtyard": {
            "text": (
                "Moonlight paints the courtyard silver. Near the ivy, something gleams beneath fallen leaves."
            ),
            "choices": [
                {
                    "text": "Pick up the old key and head inside.",
                    "target": "hall",
                    "effects": {"add_items": ["Old Key"]}
                },
                {
                    "text": "Ignore it and enter the great hall.",
                    "target": "hall"
                }
            ]
        },
        "guard": {
            "text": (
                "The guard eyes you cautiously. His stance softens as you speak. How do you address him?"
            ),
            "choices": [
                {
                    "text": "Be friendly and respectful.",
                    "target": "hall",
                    "effects": {"relationships_delta": {"Guard": 2}}
                },
                {
                    "text": "Be rude and demanding.",
                    "target": "hall",
                    "effects": {
                        "relationships_delta": {"Guard": -2},
                        "set_flags": {"watchlisted": True}
                    }
                }
            ]
        },
        "hall": {
            "text": (
                "The Great Hall bustles with life. Arched doors lead in every direction. The guard watches from afar."
            ),
            "choices": [
                {
                    "text": "Unlock the secret door with the old key.",
                    "target": "secret_passage",
                    "conditions": {"items_have": ["Old Key"]}
                },
                {
                    "text": "Ask the guard to let you into the restricted wing.",
                    "target": "restricted_wing",
                    "conditions": {"relationships_min": {"Guard": 2}}
                },
                {
                    "text": "Join the feast and rest a while.",
                    "target": "feast"
                },
                {
                    "text": "Sneak toward the treasury.",
                    "target": "sneak_attempt"
                }
            ]
        },
        "sneak_attempt": {
            "text": (
                "You move in the shadows, steps measured and breath held. A shout could end it all..."
            ),
            "choices": [
                {
                    "text": "Continue.",
                    "target": "jail",
                    "conditions": {"flags_set": ["watchlisted"]},
                    "effects": {"vars_delta": {"bravery": 1}}
                },
                {
                    "text": "Continue.",
                    "target": "treasury",
                    "conditions": {"flags_not_set": ["watchlisted"]},
                    "effects": {"vars_delta": {"bravery": 1}}
                }
            ]
        },
        "jail": {
            "text": (
                "A whistle pierces the night. Rough hands seize you. The cell door slams—the castle remembers its enemies."
            ),
            "choices": []
        },
        "treasury": {
            "text": (
                "Vaulted ceilings arch above rows of gilded chests. A pedestal bears an ancient artifact pulsing faintly."
            ),
            "choices": [
                {
                    "text": "Take the artifact and leave quietly.",
                    "target": "escape",
                    "effects": {
                        "add_items": ["Ancient Artifact"],
                        "vars_delta": {"bravery": 1}
                    }
                },
                {
                    "text": "Leave it untouched and slip away.",
                    "target": "escape"
                }
            ]
        },
        "secret_passage": {
            "text": (
                "Behind the door, a narrow stair spirals down. Cool air whispers secrets from the depths."
            ),
            "choices": [
                {
                    "text": "Descend into the darkness.",
                    "target": "underground_lake",
                    "effects": {"vars_delta": {"bravery": 1}}
                },
                {
                    "text": "Return to the Great Hall.",
                    "target": "hall"
                }
            ]
        },
        "underground_lake": {
            "text": (
                "An underground lake glows with blue light. A small boat waits, tethered to a weathered post."
            ),
            "choices": [
                {
                    "text": "Sail across the lake.",
                    "target": "ending_mystic",
                    "conditions": {"items_have": ["Ancient Artifact"]}
                },
                {
                    "text": "Sail across the lake.",
                    "target": "ending_lost",
                    "conditions": {"items_not_have": ["Ancient Artifact"]}
                }
            ]
        },
        "restricted_wing": {
            "text": (
                "With a nod, the guard escorts you past the velvet rope. Corridors twist toward the old tower."
            ),
            "choices": [
                {
                    "text": "Ask for help accessing the tower.",
                    "target": "tower",
                    "effects": {"relationships_delta": {"Guard": 1}}
                },
                {
                    "text": "Betray the guard and sprint toward the treasury.",
                    "target": "sneak_attempt",
                    "effects": {
                        "relationships_delta": {"Guard": -3},
                        "set_flags": {"watchlisted": True}
                    }
                }
            ]
        },
        "feast": {
            "text": (
                "Laughter rises with the music. Plates overflow, and cares drift away in the warm candlelight."
            ),
            "choices": [
                {
                    "text": "Eat and rest the night away.",
                    "target": "ending_peace"
                },
                {
                    "text": "Toast the guard for keeping everyone safe.",
                    "target": "ending_popular",
                    "effects": {"relationships_delta": {"Guard": 1}}
                }
            ]
        },
        "tower": {
            "text": (
                "Atop the tower, wind sings across the battlements. A dust-covered chest rests against the wall."
            ),
            "choices": [
                {
                    "text": "Open the chest with the old key.",
                    "target": "ending_hero",
                    "conditions": {"items_have": ["Old Key"]}
                },
                {
                    "text": "Gaze across the lands and return downstairs.",
                    "target": "ending_peace"
                }
            ]
        },
        "escape": {
            "text": (
                "You plan your exit. The gate is guarded, the walls are high, and night deepens."
            ),
            "choices": [
                {
                    "text": "Ask the guard to wave you through the gate.",
                    "target": "ending_assisted_escape",
                    "conditions": {"relationships_min": {"Guard": 2}}
                },
                {
                    "text": "Make a break for it now.",
                    "target": "ending_caught",
                    "conditions": {"flags_set": ["watchlisted"]}
                },
                {
                    "text": "Slip away under moonlight.",
                    "target": "ending_free",
                    "conditions": {"flags_not_set": ["watchlisted"]}
                },
                {
                    "text": "Change your mind and return to the Great Hall.",
                    "target": "hall"
                }
            ]
        },
        "ending_mystic": {
            "text": (
                "Artifact in hand, the lake parts as if obeying your will. You vanish into a realm of shimmering dawns—"
                "a legend reborn."
            ),
            "choices": []
        },
        "ending_lost": {
            "text": (
                "The mist thickens. Your boat turns in circles until the lantern gutters out. When light returns, "
                "the castle—and you—are never seen again."
            ),
            "choices": []
        },
        "ending_hero": {
            "text": (
                "Within the chest lies a seal of kingship. You deliver it to the people, and the castle awakens to justice."
            ),
            "choices": []
        },
        "ending_peace": {
            "text": (
                "You choose a gentle path. In quiet days that follow, the castle becomes a second home."
            ),
            "choices": []
        },
        "ending_popular": {
            "text": (
                "Your praise spreads like firelight. The guard becomes your staunch ally, and doors open before you."
            ),
            "choices": []
        },
        "ending_assisted_escape": {
            "text": (
                "With a discreet nod, the guard lifts the bar. You pass into the cool night, owing a friend a favor."
            ),
            "choices": []
        },
        "ending_caught": {
            "text": (
                "Torches flare and a net drops from above. The castle has long memories, and your face is now among them."
            ),
            "choices": []
        },
        "ending_free": {
            "text": (
                "Hand over hand, you crest the wall and disappear into the wilds. Freedom tastes like starlight."
            ),
            "choices": []
        }
    }
}