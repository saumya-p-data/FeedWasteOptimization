# Feed Waste Optimization: A Multimodal Data Fusion Project

https://github.com/user-attachments/assets/f4392bc4-bf64-4a81-b790-942cc272b154

### What is this project?
In salmon farming, data comes from many different sources—underwater cameras, oxygen sensors, and production databases. Usually, these systems don't talk to each other. This project is a **Digital Twin prototype** that brings all this different data together into one dashboard.

### The Problem I’m Solving
When a farm manager sees that fish aren't eating, they need to know *why*. 
- Is the water too warm (Thermal Stress)? 
- Is the current too strong (Feed Drift)? 
- Is the oxygen too low?

My project fuses these different data silos so we can see the bigger picture and give a smart feeding recommendation that saves money and protects the environment.

### How it Works
1. **SQL Database:** Stores the "Biological Context" (How many fish and what is their average weight).
2. **Data Fusion:** Uses Python to sync live sensor data (Temp/Oxygen) with camera signals (Hunger Index) on a single timeline.
3. **Logic Engine:** I've programmed biological rules that automatically reduce feed if the current is too fast or the water is too warm.
4. **AI Assistant:** A local AI (Llama 3.2) that explains the data in plain language to the user.

### Tech Used
- **Python** (Pandas, Streamlit, Scikit-learn)
- **SQL** (SQLite)
- **Local AI** (Ollama / Llama 3.2)
