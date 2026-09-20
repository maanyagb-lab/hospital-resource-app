Hospital Resource Manager



A hospital resource management simulator built for \[Innov8].


\## Features



\- Dashboard with real-time metrics

\- Priority queue for patients

\- Resource tracking (beds, ICU, doctors)

\- Simulation mode with surge handling




### Interactive Prototype (Glide)
The main user interface is built as a no-code prototype in Glide:
- same as features but without additional simulator and priority queue

### Coded Version (Streamlit)
A Python implementation using Streamlit showing the same logic


## How It Works

### Priority Algorithm
Patients are prioritized using:
Priority Score = (Urgency × 10) + (Wait Time × 0.1)



Higher urgency and longer wait times increase priority.

### Resource Allocation
1. Patients are sorted by priority score
2. ICU patients get ICU beds + doctors first
3. Regular patients get regular beds + doctors
4. Resources are tracked in real-time




## Running Locally


### Streamlit App
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Priority Logic
```bash
python priority_simulator.py
```


## Technology Stack

- **Frontend:** Glide (no-code prototype)
- **Backend:** Python, Streamlit
- **Data:** CSV exports


## GitHub

[Your repo link]




**Live Demo:** []


\## Innov8

- Annapoorneshwari R
- Diya S Shetty
- Maanya Guruprasad Bhat
