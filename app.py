import streamlit as st
import random
import matplotlib.pyplot as plt

# =========================
# Page config
# =========================
st.set_page_config(page_title="Hospital Resource Manager", layout="wide")

# =========================
# Initialize session state with simple lists
# =========================
if "patients" not in st.session_state:
    st.session_state.patients = [
        {"PatientID": 1, "Name": "Aarav Kumar", "Age": 45, "Gender": "Male", 
         "Urgency": 5, "NeedsICU": True, "Status": "Waiting", 
         "ArrivalTime": "09:30", "WaitTimeMin": 30},
        {"PatientID": 2, "Name": "Ishaan Mehta", "Age": 30, "Gender": "Male", 
         "Urgency": 3, "NeedsICU": False, "Status": "Waiting", 
         "ArrivalTime": "09:40", "WaitTimeMin": 20},
        {"PatientID": 3, "Name": "Priya Singh", "Age": 60, "Gender": "Female", 
         "Urgency": 4, "NeedsICU": True, "Status": "Waiting", 
         "ArrivalTime": "09:15", "WaitTimeMin": 45},
        {"PatientID": 4, "Name": "Neha Reddy", "Age": 25, "Gender": "Female", 
         "Urgency": 2, "NeedsICU": False, "Status": "Treated", 
         "ArrivalTime": "08:50", "WaitTimeMin": 10},
    ]

if "resources" not in st.session_state:
    st.session_state.resources = [
        {"ResourceType": "Beds", "Total": 20, "Used": 12},
        {"ResourceType": "ICU_Beds", "Total": 5, "Used": 3},
        {"ResourceType": "Doctors", "Total": 10, "Used": 6},
    ]

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# =========================
# Helper functions
# =========================
def get_waiting_patients():
    waiting = [p for p in st.session_state.patients if p["Status"] == "Waiting"]
    # Sort by priority: urgency * 10 + wait_time * 0.1
    waiting.sort(key=lambda p: p["Urgency"] * 10 + p["WaitTimeMin"] * 0.1, reverse=True)
    return waiting

def get_resource(resource_type):
    for r in st.session_state.resources:
        if r["ResourceType"] == resource_type:
            return r
    return None

# =========================
# Sidebar
# =========================
st.sidebar.title("Hospital Resource Manager")
st.sidebar.markdown("Navigation")

if st.sidebar.button("Dashboard"):
    st.session_state.page = "Dashboard"
if st.sidebar.button("Add Patient"):
    st.session_state.page = "Add Patient"
if st.sidebar.button("All Patients"):
    st.session_state.page = "All Patients"
if st.sidebar.button("Update Resources"):
    st.session_state.page = "Update Resources"
if st.sidebar.button("Simulator"):
    st.session_state.page = "Simulator"

st.sidebar.markdown("---")
st.sidebar.markdown("Built for hackathon demo")

# =========================
# DASHBOARD PAGE
# =========================
if st.session_state.page == "Dashboard":
    st.title("Hospital Resource Dashboard")
    
    # Count patients
    total_patients = len(st.session_state.patients)
    waiting_patients = len([p for p in st.session_state.patients if p["Status"] == "Waiting"])
    
    # Get resources
    beds = get_resource("Beds")
    icu = get_resource("ICU_Beds")
    docs = get_resource("Doctors")
    
    # Metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Patients", total_patients)
    c2.metric("Waiting Patients", waiting_patients)
    c3.metric("Beds", f"{beds['Used']} / {beds['Total']}")
    c4.metric("ICU Beds", f"{icu['Used']} / {icu['Total']}")
    c5.metric("Doctors", f"{docs['Used']} / {docs['Total']}")
    
    # Priority Queue
    st.markdown("### Priority Queue (Waiting Patients)")
    waiting = get_waiting_patients()
    if waiting:
        # Create a simple table
        table_data = []
        for p in waiting[:10]:  # Show top 10
            table_data.append({
                "Name": p["Name"],
                "Urgency": p["Urgency"],
                "Needs ICU": "Yes" if p["NeedsICU"] else "No",
                "Wait (min)": p["WaitTimeMin"],
                "Priority": round(p["Urgency"] * 10 + p["WaitTimeMin"] * 0.1, 1)
            })
        st.table(table_data)
    else:
        st.info("No waiting patients")
    
    # Resource Utilization
    st.markdown("### Resource Utilization")
    resource_table = []
    for r in st.session_state.resources:
        resource_table.append({
            "Resource": r["ResourceType"],
            "Total": r["Total"],
            "Used": r["Used"],
            "Available": r["Total"] - r["Used"]
        })
    st.table(resource_table)

# =========================
# ADD PATIENT PAGE
# =========================
elif st.session_state.page == "Add Patient":
    st.title("Add Patient")
    
    with st.form("add_patient"):
        name = st.text_input("Name")
        age = st.number_input("Age", 0, 120, 30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        urgency = st.slider("Urgency (1-5)", 1, 5, 3)
        needs_icu = st.checkbox("Needs ICU")
        arrival = st.text_input("Arrival Time", "10:15")
        wait = st.number_input("Wait Time (min)", 0, 1000, 0)
        status = st.selectbox("Status", ["Waiting", "Treated", "Discharged"])
        
        if st.form_submit_button("Add Patient"):
            if name:
                new_id = max(p["PatientID"] for p in st.session_state.patients) + 1
                new_patient = {
                    "PatientID": new_id,
                    "Name": name,
                    "Age": age,
                    "Gender": gender,
                    "Urgency": urgency,
                    "NeedsICU": needs_icu,
                    "Status": status,
                    "ArrivalTime": arrival,
                    "WaitTimeMin": wait
                }
                st.session_state.patients.append(new_patient)
                st.success(f"Added patient: {name}")

# =========================
# ALL PATIENTS PAGE
# =========================
elif st.session_state.page == "All Patients":
    st.title("All Patients")
    
    if st.session_state.patients:
        # Build table data
        table_data = []
        for p in st.session_state.patients:
            priority = p["Urgency"] * 10 + p["WaitTimeMin"] * 0.1 if p["Status"] == "Waiting" else 0
            table_data.append({
                "ID": p["PatientID"],
                "Name": p["Name"],
                "Age": p["Age"],
                "Urgency": p["Urgency"],
                "Status": p["Status"],
                "Wait (min)": p["WaitTimeMin"],
                "Priority": round(priority, 1) if p["Status"] == "Waiting" else "-"
            })
        st.table(table_data)
    else:
        st.info("No patients in the system")

# =========================
# UPDATE RESOURCES PAGE
# =========================
elif st.session_state.page == "Update Resources":
    st.title("Update Resources")
    
    for i, r in enumerate(st.session_state.resources):
        st.markdown(f"### {r['ResourceType']}")
        c1, c2 = st.columns([2, 1])
        with c1:
            st.write(f"**Total:** {r['Total']}")
        with c2:
            new_used = st.number_input(
                "Used",
                0,
                r["Total"],
                r["Used"],
                key=f"used_{i}"
            )
            r["Used"] = new_used
        st.markdown("---")
    
    st.success("Resources updated automatically")

# =========================
# SIMULATOR PAGE
# =========================
elif st.session_state.page == "Simulator":
    st.title("Hospital Resource Simulator")
    st.markdown("Simulate patient arrivals and resource allocation")
    
    # Parameters
    st.markdown("### Parameters")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        arrival_rate = st.slider("Arrival rate", 0.0, 1.0, 0.3, 0.05)
    with c2:
        total_beds = st.number_input("Total Beds", 5, 100, 20)
    with c3:
        total_icu = st.number_input("Total ICU", 1, 20, 5)
    with c4:
        total_docs = st.number_input("Total Doctors", 3, 50, 10)
    
    surge = st.checkbox("Enable surge")
    surge_start = surge_end = None
    if surge:
        c5, c6 = st.columns(2)
        with c5:
            surge_start = st.number_input("Surge start", 0, 200, 50)
        with c6:
            surge_end = st.number_input("Surge end", 0, 200, 100)
    
    if st.button("Run Simulation"):
        # Local simulation state
        sim_patients = [p.copy() for p in st.session_state.patients]
        sim_resources = {
            "Beds": {"total": total_beds, "used": 0},
            "ICU_Beds": {"total": total_icu, "used": 0},
            "Doctors": {"total": total_docs, "used": 0}
        }
        
        patient_counter = max(p["PatientID"] for p in sim_patients) + 1
        log = {"time": [], "queue": [], "wait": [], "bed_util": [], "icu_util": [], "doc_util": []}
        
        for t in range(150):
            # Surge?
            is_surge = surge and surge_start is not None and surge_end is not None and surge_start <= t <= surge_end
            rate = arrival_rate * (2.0 if is_surge else 1.0)
            
            # New patient?
            if random.random() < rate:
                urgency = random.choices([1,2,3,4,5], [0.3,0.3,0.2,0.15,0.05])[0]
                sim_patients.append({
                    "PatientID": patient_counter,
                    "Name": f"Patient {patient_counter}",
                    "Age": random.randint(10,80),
                    "Gender": random.choice(["Male","Female"]),
                    "Urgency": urgency,
                    "NeedsICU": urgency >= 4,
                    "Status": "Waiting",
                    "ArrivalTime": str(t),
                    "WaitTimeMin": 0
                })
                patient_counter += 1
            
            # Update wait times
            for p in sim_patients:
                if p["Status"] == "Waiting":
                    try:
                        p["WaitTimeMin"] = t - int(p["ArrivalTime"])
                    except:
                        p["WaitTimeMin"] = t
            
            # Priority queue
            waiting = [p for p in sim_patients if p["Status"] == "Waiting"]
            waiting.sort(key=lambda x: x["Urgency"]*10 + x["WaitTimeMin"]*0.1, reverse=True)
            
            # Allocate
            for p in waiting:
                if p["NeedsICU"]:
                    if sim_resources["ICU_Beds"]["used"] < sim_resources["ICU_Beds"]["total"] and sim_resources["Doctors"]["used"] < sim_resources["Doctors"]["total"]:
                        sim_resources["ICU_Beds"]["used"] += 1
                        sim_resources["Doctors"]["used"] += 1
                        p["Status"] = "Treated"
                else:
                    if sim_resources["Beds"]["used"] < sim_resources["Beds"]["total"] and sim_resources["Doctors"]["used"] < sim_resources["Doctors"]["total"]:
                        sim_resources["Beds"]["used"] += 1
                        sim_resources["Doctors"]["used"] += 1
                        p["Status"] = "Treated"
            
            # Discharge
            for p in sim_patients:
                if p["Status"] == "Treated" and random.random() < 0.1:
                    if p["NeedsICU"]:
                        sim_resources["ICU_Beds"]["used"] -= 1
                    else:
                        sim_resources["Beds"]["used"] -= 1
                    sim_resources["Doctors"]["used"] -= 1
                    p["Status"] = "Discharged"
            
            # Log
            queue_len = len([p for p in sim_patients if p["Status"] == "Waiting"])
            treated = [p for p in sim_patients if p["Status"] in ["Treated","Discharged"]]
            avg_wait = sum(p["WaitTimeMin"] for p in treated)/len(treated) if treated else 0
            log["time"].append(t)
            log["queue"].append(queue_len)
            log["wait"].append(avg_wait)
            log["bed_util"].append(sim_resources["Beds"]["used"]/sim_resources["Beds"]["total"])
            log["icu_util"].append(sim_resources["ICU_Beds"]["used"]/sim_resources["ICU_Beds"]["total"])
            log["doc_util"].append(sim_resources["Doctors"]["used"]/sim_resources["Doctors"]["total"])
        
        # Show plots
        st.markdown("### Results")
        fig, ax = plt.subplots(3, 1, figsize=(8, 10), sharex=True)
        ax[0].plot(log["time"], log["queue"])
        ax[0].set_ylabel("Queue length")
        ax[1].plot(log["time"], log["wait"], color='orange')
        ax[1].set_ylabel("Avg wait time")
        ax[2].plot(log["time"], log["bed_util"], label='Beds')
        ax[2].plot(log["time"], log["icu_util"], label='ICU')
        ax[2].plot(log["time"], log["doc_util"], label='Doctors')
        ax[2].set_ylabel("Utilization")
        ax[2].legend()
        st.pyplot(fig)
        
        st.metric("Max queue", max(log["queue"]))

# Footer
st.markdown("---")
st.markdown("Hospital Resource Manager – Hackathon Prototype")
