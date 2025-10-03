#!/usr/bin/env python3
"""
Test script to verify the random prize removal functionality
"""

def test_prize_removal():
    """Test the prize removal logic manually"""
    
    # Simulate initial prize lists
    common_prizes = [
        "Plex",
        "Skill Injector (Large)",
        "Random Ship Blueprint"
    ]
    
    configured_prizes = [
        "Thrasher Semiotique Superluminal SKIN (x10) (Kan0666)",
        "Hurricane Blueprint (x3) (Synnistor)",
        "Vexor Navy Issue (Synnistor)",
        "Kikimora (x3) (Synnistor)"
    ]
    
    # Simulate random selection
    import random
    all_prizes = []
    
    # Expand prizes (simplified version)
    for prize in common_prizes:
        all_prizes.append({
            "display": prize,
            "original_full": prize,
            "base_name": prize,
            "donator": None
        })
    
    for prize in configured_prizes:
        all_prizes.append({
            "display": prize,
            "original_full": prize,
            "base_name": prize.split(' (')[0],
            "donator": prize.split('(')[-1].rstrip(')') if '(' in prize else None
        })
    
    print("Available prizes before selection:")
    for i, prize in enumerate(all_prizes):
        print(f"  {i+1}. {prize['original_full']}")
    
    # Random selection
    selected_prize = random.choice(all_prizes)
    print(f"\n🎲 Randomly selected: {selected_prize['original_full']}")
    
    # Simulate confirmation and removal
    prize_to_remove = selected_prize["original_full"]
    
    # Check where to remove from
    if prize_to_remove in common_prizes:
        common_prizes.remove(prize_to_remove)
        print(f"✅ Removed '{prize_to_remove}' from common prizes list")
        print("Updated common prizes:", common_prizes)
    elif prize_to_remove in configured_prizes:
        configured_prizes.remove(prize_to_remove)
        print(f"✅ Removed '{prize_to_remove}' from configured prizes list")
        print("Updated configured prizes:", configured_prizes)
    else:
        print(f"❌ Prize '{prize_to_remove}' not found in any list")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_prize_removal()
