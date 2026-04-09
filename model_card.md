# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

- This system heavily over-prioritizes the initial categorical matching, meaning completely mismatched vibe songs can sometimes outrank a perfect vibe match simply because they lie within the correct umbrella genre.
- Our dataset `songs.csv` only has 1 rock song and 1 edm song. When the user requests a Rock or EDM profile, the scarcity of choices forces the system to recommend unrelated pop or lofi songs that happen to share adjacent mood or energy levels. Thus the system struggles to properly represent niche styles.
- The "Weight Shift Experiment" proved that doubling energy importance caused random high-bpm tracks to dominate over categorical genre fits, showing how sensitive the weights are.  

---

## 7. Evaluation  

- I tested the system against four distinct user profiles: "High-Energy Pop", "Chill Lofi", "Deep Intense Rock", and an edge-case adversarial profile "Edge Case Sad EDM".
- I looked for how well the highest recommended songs aligned with both categorical constraints (genre/mood) and dynamic traits (energy).
- I was surprised to find that the "Gym Hero" pop song consistently showed up across completely unrelated profiles (like Rock and Sad EDM) simply because its high energy stat mathematically overpowered other available tracks that had low energy, due to the tiny size of our catalog.  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
