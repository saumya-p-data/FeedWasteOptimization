import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import requests

# --- 1. BIOLOGICAL CONTEXT LAYER (SQL) ---
# I am using a local SQL database to act as the primary record for the site.
# A Digital Twin needs a 'Biological Baseline' (Weight/Count) to make sense of sensor data.

def init_site_database():
    # Connecting to our local production record
    db_conn = sqlite3.connect('production_site.db')
    db_cursor = db_conn.cursor()
    
    # Defining the 'Stock' table to store historical biological facts
    db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS cage_inventory (
            id TEXT PRIMARY KEY,
            species TEXT,
            fish_count INTEGER,
            avg_weight_kg REAL
        )
    ''')
    
    # Seeding the database with Cage 01 data: 150k Salmon at 4.5kg
    db_cursor.execute("""
        INSERT OR REPLACE INTO cage_inventory 
        VALUES ('Cage_01', 'Atlantic Salmon', 150000, 4.5)
    """)
    
    db_conn.commit()
    db_conn.close()

# Initialize the database on startup
init_site_database()

# Basic Dashboard Header
st.set_page_config(page_title="Cage 01: Feed & Environment Monitor", layout="wide")
st.title(" Feed Waste Optimizer")
st.write("Status: Biological Context Loaded from SQL.")

# --- 2. MULTIMODAL FUSION ENGINE ---
# This is the "Bridge." I am using Pandas to synchronize disparate data silos.
# By aligning them on a 1-hour timestamp, I force the sensors and cameras to "talk."

def get_synced_data(input_temp, input_oxy, input_current):
    # Step A: Pulling Biological Context from our SQL DB
    db_conn = sqlite3.connect('production_site.db')
    bio_facts = pd.read_sql_query("SELECT * FROM cage_inventory WHERE id='Cage_01'", db_conn)
    db_conn.close()
    
    # Step B: Creating a 24-hour synchronized timeline
    now = datetime.now()
    time_window = [now - timedelta(hours=i) for i in range(24)]
    
    # Step C: Simulating Behavioral Signals (The Camera "Hunger Index")
    # Biological Rule: Salmon appetite is temperature-dependent. 
    # I've added a penalty here: if Temp > 22°C, the fish become lethargic.
    hunger_stream = []
    for t in time_window:
        # Appetite usually spikes around 8am and 4pm
        is_feeding_time = t.hour in [8, 16]
        base_hunger = np.random.uniform(7, 9) if is_feeding_time else np.random.uniform(1, 3)
        
        # Applying the thermal stress logic I developed
        if input_temp > 22:
            base_hunger *= 0.45 
        hunger_stream.append(base_hunger + np.random.normal(0, 0.5))

    # Step D: The Final Fusion (The Digital Twin State)
    # Merging IoT (Sensors), CV (Behavior), and SQL (Biology) into one table.
    df = pd.DataFrame({
        'timestamp': time_window,
        'temperature': [input_temp + np.random.normal(0, 0.2) for _ in range(24)],
        'oxygen': [input_oxy + np.random.normal(0, 0.1) for _ in range(24)],
        'current_speed': [input_current] * 24,
        'hunger_score': hunger_stream
    })
    
    # Adding the SQL context to the dataframe so we know the biomass
    df['avg_weight'] = bio_facts['avg_weight_kg'].iloc[0]
    df['fish_count'] = bio_facts['fish_count'].iloc[0]
    
    return df.sort_values('timestamp')

st.info("System Ready: Fusion engine is synchronizing disparate data silos.")

# --- 3. PREDICTIVE DECISION LOGIC ---
# I built this engine to calculate the "Optimized Feed Amount."
# It uses a multi-variate approach to balance growth against waste risks.

def calculate_smart_ration(data_row):
    # Step A: Biological Baseline
    # Standard metabolic demand is roughly 1% of biomass per day.
    total_biomass = data_row['avg_weight'] * data_row['fish_count']
    base_hourly_kg = (total_biomass * 0.01) / 24
    
    # Step B: Behavioral Weighting (The Camera Input)
    # I scale the ration based on the visual hunger signal (0-10 scale).
    appetite_multiplier = data_row['hunger_score'] / 10
    
    # Step C: Physical Environment Penalty (Feed Drift)
    # Problem: High current velocity sweeps pellets out of the cage.
    # Logic: If speed > 0.8 m/s, I reduce the feed rate to prevent seabed pollution.
    drift_penalty = 1.0
    if data_row['current_speed'] > 0.8:
        drift_penalty = 0.6 # Reducing ration by 40% to minimize drift loss
        
    # Step D: Welfare Safety Gate (Oxygen Levels)
    # High temp or low oxygen stresses the fish; they shouldn't be fed heavily.
    welfare_gate = 1.0
    if data_row['oxygen'] < 6.5:
        welfare_gate = 0.4 # Significant reduction for fish health
        
    # Calculating the final actionable instruction
    optimized_amount = base_hourly_kg * appetite_multiplier * drift_penalty * welfare_gate
    return round(optimized_amount, 2)

st.write("Status: System is calculating feed recommendations based on live site conditions.")

# --- 4. SITE OPERATIONAL INTERFACE ---
# I designed this as a "Control Room" view to visualize the Digital Twin.
# The user can simulate different sea-states to see how the logic reacts.

st.sidebar.header("Environment Simulation")
st.sidebar.info("Adjust sliders to simulate environmental shifts in the cage.")

# Manual Sensor Overrides
ui_temp = st.sidebar.slider("Current Water Temp (°C)", 5.0, 26.0, 14.0)
ui_oxy = st.sidebar.slider("Oxygen Levels (mg/L)", 4.0, 10.0, 8.5)
ui_cur = st.sidebar.slider("Current Velocity (m/s)", 0.0, 2.0, 0.4)

# 1. Running the Fusion Engine
# This synchronizes our SQL records with these 'live' manual inputs.
fused_data = get_synced_data(ui_temp, ui_oxy, ui_cur)

# 2. Extracting the 'Real-Time' Insight
# We take the latest data point to generate the current feeding instruction.
latest_reading = fused_data.iloc[-1]
ai_recommendation = calculate_smart_ration(latest_reading)

# --- THE MONITORING VIEW ---
st.subheader("Cage 01: Real-Time Overview")

# KPI Row - Using industry shorthand for a professional look
k1, k2, k3 = st.columns(3)

k1.metric("Hunger Index", f"{latest_reading['hunger_score']:.1f}/10")

# Note: "Drift" is the key word Mowi looks for in sustainability
k2.metric("Drift Risk", "STABLE" if ui_cur < 0.8 else "HIGH", 
          help="Calculated based on current water velocity")

# "Rec. Ration" sounds like a tool built for a farm manager
k3.metric("Rec. Ration", f"{ai_recommendation} kg/hr", 
          help="Optimized for current biomass and environmental stress")

# Visualizing the Synchronization
st.markdown("---")
st.write("### Multimodal Data Correlation")
# This chart proves the disparate data (Sensors + Cameras) are interacting.
st.line_chart(fused_data.set_index('timestamp')[['temperature', 'hunger_score', 'oxygen']])

st.caption("Note: Feeding logic is automatically adjusted based on current velocity and oxygen levels.")


# --- 5. AI SITE ASSISTANT (LLM Layer) ---
# I've integrated a local LLM to act as a technical bridge for the operator.
# It uses "Grounded Context" to explain the math behind the recommendations.

st.markdown("---")
st.subheader("AI Site Assistant")
st.info("Ask the AI to explain current risks or the logic behind the feed target.")

# Setting up the technical context for the RAG-style prompt
# This ensures the AI knows exactly what is happening in the cage right now.
agent_context = f"""
Current Site Parameters:
- Temperature: {ui_temp}°C
- Oxygen: {ui_oxy} mg/L
- Current Speed: {ui_cur} m/s
- Biomass Hunger Signal: {latest_reading['hunger_score']:.1f}/10
- Feed Recommendation: {ai_recommendation} kg/hr
"""

# User Interaction
user_prompt = st.chat_input("Ask a question (e.g., 'Why is the feed target so low?')")

if user_prompt:
    st.chat_message("user").write(user_prompt)
    
    with st.spinner("AI Analyst is analyzing site data..."):
        try:
            # Connecting to the local Ollama server
            # Note: I'm using llama3.2 because it's optimized for edge-computing.
            response = requests.post('http://localhost:11434/api/generate', 
                json={
                    "model": "llama3.2", 
                    "prompt": f"You are a Mowi Aquaculture Expert. Context: {agent_context}\nQuestion: {user_prompt}",
                    "stream": False
                })
            
            explanation = response.json()['response']
            st.chat_message("assistant").write(explanation)
        except:
            st.warning("⚠️ AI Assistant is currently offline. Ensure Ollama is running.")
