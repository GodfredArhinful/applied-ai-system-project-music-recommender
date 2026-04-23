import sys
import os

# Ensure the src module can be imported from the scripts folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.recommender import load_songs
from src.ai_dj import AIDJ

def main():
    songs = load_songs("data/songs.csv")
    dj = AIDJ(songs)
    
    # 5 Predefined challenging inputs
    test_cases = [
        {"prompt": "I need some happy pop music to dance to.", "expected_genre": "pop"},
        {"prompt": "Give me something super aggressive for lifting weights.", "expected_genre": "metal"},
        {"prompt": "I want to relax with some 1800s strings.", "expected_genre": "classical"},
        {"prompt": "Chill beats for coding.", "expected_genre": "lofi"},
        # This is an impossible query to trigger the Agentic Workflow Fallback
        {"prompt": "Play a polka song featuring a kazoo solo.", "expected_genre": "polka"}
    ]
    
    print("\n" + "="*80)
    print(" 🧪 AI DJ EVALUATION HARNESS 🧪 ")
    print("="*80)
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nRunning Test {i}: '{test['prompt']}'")
        retrieved_items = dj.retrieve(test['prompt'], k=1)
        
        if not retrieved_items:
            print("❌ FAIL: No items retrieved.")
            results.append({"test": i, "status": "FAIL", "confidence": 0.0})
            continue
            
        top_song, confidence = retrieved_items[0]
        
        # Check Agentic Workflow for impossible query
        if test['expected_genre'] == 'polka':
            if confidence < 0.15:
                print(f"✅ PASS: Agentic Fallback correctly triggered. Confidence {confidence:.2f} was below threshold.")
                results.append({"test": i, "status": "PASS", "confidence": confidence})
            else:
                print(f"❌ FAIL: Agentic Fallback did not trigger. Confidence: {confidence:.2f}")
                results.append({"test": i, "status": "FAIL", "confidence": confidence})
            continue
            
        # Standard retrieval check
        if top_song['genre'].lower() == test['expected_genre'].lower():
            print(f"✅ PASS: Correct genre '{test['expected_genre']}' retrieved with confidence {confidence:.2f}")
            results.append({"test": i, "status": "PASS", "confidence": confidence})
        else:
            print(f"❌ FAIL: Expected '{test['expected_genre']}', got '{top_song['genre']}'. Confidence: {confidence:.2f}")
            results.append({"test": i, "status": "FAIL", "confidence": confidence})
            
    print("\n" + "="*80)
    print(" 📊 EVALUATION SUMMARY 📊 ")
    print("="*80)
    print(f"{'Test':<6} | {'Status':<6} | {'Confidence'}")
    print("-" * 35)
    
    passed_count = 0
    total_confidence = 0.0
    
    for res in results:
        status_symbol = "✅" if res['status'] == "PASS" else "❌"
        print(f"{res['test']:<6} | {status_symbol} {res['status']:<4} | {res['confidence']:.2f}")
        if res['status'] == "PASS":
            passed_count += 1
        total_confidence += res['confidence']
        
    avg_confidence = total_confidence / len(results)
    
    print("-" * 35)
    print(f"Total Pass Rate   : {passed_count}/{len(results)} ({(passed_count/len(results))*100:.0f}%)")
    print(f"Average Confidence: {avg_confidence:.2f}")
    
    if passed_count == len(results):
        print("\n🎉 ALL TESTS PASSED! AI DJ IS RELIABLE. 🎉")
    else:
        print("\n⚠️ SOME TESTS FAILED. REVIEW THE LOGS. ⚠️")
        
if __name__ == "__main__":
    main()
