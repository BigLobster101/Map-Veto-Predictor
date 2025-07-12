import pandas as pd
import random

VETO_STRUCTURE = {
    "BO1": ["Ban", "Ban", "Ban", "Ban", "Ban", "Ban", "Decider"],
    "BO3": ["Ban", "Ban", "Ban", "Ban", "Pick", "Pick", "Ban", "Ban", "Decider"]
}

def predict_veto_order(team1, team2, ban_style, maps):
    structure = VETO_STRUCTURE.get(ban_style.upper(), [])
    steps = []
    available = maps.copy()

    for i, action in enumerate(structure):
        team = team1 if i % 2 == 0 else team2
        map_choice = weighted_choice(available, action, team, team1, team2)
        steps.append({
            "Step": i + 1,
            "Team": team,
            "Action": action,
            "Map": map_choice
        })
        if action != "Decider":
            available = available[available["Map"] != map_choice]

    return pd.DataFrame(steps)
