import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# =========================
# Page config & session init
# =========================
st.set_page_config(page_title="Hospital Resource Manager", layout="wide")

if "initialized" not in st.session_state:
    # Initialize patients
    patients_data = [
        {
            "PatientID": 1,
            "Name": "Arun Gupta",
            "Age": 48,
            "Gender": "Male",
            "Urgency": "Urgent",
            "NeedsICU": "Yes",
            "Assigned Doctor": "Dr Umesh",
            "Assigned Bed": 602,
            "Appointment Time": "Nil",
        },
        {
            "PatientID": 0,
            "Name": "Raj Bannerjee",
            "Age": 26,
            "Gender": "Male",
            "Urgency": "Nil",
            "NeedsICU": "No",
            "Assigned Doctor": "Dr Sashi",
            "Assigned Bed": 602,
            "Appointment Time": "15:30",
        },
        {
            "PatientID": 3,
            "Name": "Jaya Kumar",
            "Age": 35,
            "Gender": "Female",
            "Urgency": "Mild",
            "NeedsICU": "No",
            "Assigned Doctor": "Dr Jyothi",
            "Assigned Bed": 505,
            "Appointment Time": "10:45",

        },
        
          
        
    ]
    st.session_state.patients = pd.DataFrame(patients_data)

    # Initialize resources
    resources_data = [
        {"ResourceType": "Beds", "Total": 3000, "Used": 2500, "Available": 500},
        {"ResourceType": "ICU_Beds", "Total": 1000, "Used": 800, "Available": 200},
        {"ResourceType": "Doctors", "Total": 50, "Used": 32, "Available": 18},
        {"ResourceType": "Nurses", "Total": 100, "Used": 50, "Available": 50},

    ]
    st.session_state.resources = pd.DataFrame(resources_data)

    # For simple simulation over time
    st.session_state.simulation_log = {
        "time": [],
        "queue_length": [],
        "avg_wait_time": [],
        "bed_utilization": [],
        "icu_utilization": [],
        "doctor_utilization": [],
    }

    st.session_state.initialized = True
    st.session_state.page = "Dashboard"


# =========================
# Helper functions
# =========================
def priority_score(row):
    return row["Urgency"] * 10 + row["WaitTimeMin"] * 0.1


def get_waiting_patients():
    df = st.session_state.patients
    waiting = df[df["Status"] == "Waiting"].copy()
    if waiting.empty:
        return waiting
    waiting["Priority"] = waiting.apply(priority_score, axis=1)
    waiting = waiting.sort_values(by="Priority", ascending=False)
    return waiting


def get_resource_row(resource_type):
    df = st.session_state.resources
    return df[df["ResourceType"] == resource_type].iloc[0]


# =========================
# Sidebar navigation
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
# Pages
# =========================
if st.session_state.page == "Dashboard":
    st.title("Hospital Resource Dashboard")

    # Metrics
    total_patients = len(st.session_state.patients)
    waiting_patients = len(st.session_state.patients[st.session_state.patients["Status"] == "Waiting"])

    beds_row = get_resource_row("Beds")
    icu_row = get_resource_row("ICU_Beds")
    docs_row = get_resource_row("Doctors")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Patients", total_patients)
    c2.metric("Waiting Patients", waiting_patients)
    c3.metric("Beds Used / Total", f"{beds_row['Used']} / {beds_row['Total']}")
    c4.metric("ICU Used / Total", f"{icu_row['Used']} / {icu_row['Total']}")
    c5.metric("Doctors Busy / Total", f"{docs_row['Used']} / {docs_row['Total']}")

    st.markdown("### Priority Queue (Waiting Patients)")
    waiting = get_waiting_patients()
    if not waiting.empty:
        display_cols = ["Name", "Urgency", "NeedsICU", "WaitTimeMin", "Priority"]
        st.dataframe(waiting[display_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No waiting patients at the moment.")

    st.markdown("### Resource Utilization")
    res_display = st.session_state.resources.copy()
    res_display["Available"] = res_display["Total"] - res_display["Used"]
    st.dataframe(res_display, use_container_width=True, hide_index=True)


elif st.session_state.page == "Add Patient":
    st.title("Add Patient")

    with st.form("add_patient_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0, max_value=120, value=30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        urgency = st.slider("Urgency (1–5)", 1, 5, 3)
        needs_icu = st.checkbox("Needs ICU")
        arrival_time = st.text_input("Arrival Time (e.g., 10:15)", "10:15")
        wait_time = st.number_input("Wait Time (min)", min_value=0, value=0)
        status = st.selectbox("Status", ["Waiting", "Treated", "Discharged"])

        submitted = st.form_submit_button("Add Patient")

        if submitted and name:
            new_id = int(st.session_state.patients["PatientID"].max()) + 1 if not st.session_state.patients.empty else 1
            new_row = {
                "PatientID": new_id,
                "Name": name,
                "Age": age,
                "Gender": gender,
                "Urgency": urgency,
                "NeedsICU": needs_icu,
                "Status": status,
                "ArrivalTime": arrival_time,
                "WaitTimeMin": wait_time,
            }
            st.session_state.patients = pd.concat(
                [st.session_state.patients, pd.DataFrame([new_row])], ignore_index=True
            )
            st.success("Patient added!")


elif st.session_state.page == "All Patients":
    st.title("All Patients")

    df = st.session_state.patients
    # Optional: add computed priority for waiting patients
    if not df.empty:
        df_display = df.copy()
        if "Waiting" in df_display["Status"].values:
            df_display["Priority"] = df_display.apply(priority_score, axis=1)
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No patients in the system yet.")


elif st.session_state.page == "Update Resources":
    st.title("Update Resources")

    df = st.session_state.resources

    st.markdown("### Edit Used Counts")

    for idx, row in df.iterrows():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**{row['ResourceType']}**")
        with col2:
            new_used = st.number_input(
                "Used",
                min_value=0,
                max_value=int(row["Total"]),
                value=int(row["Used"]),
                key=f"used_{row['ResourceType']}",
            )
            df.loc[idx, "Used"] = new_used

    st.session_state.resources = df
    st.success("Resources updated.")


elif st.session_state.page == "Simulator":
    st.title("Hospital Resource Simulator")

    st.markdown(
        "Simple simulation of patient arrivals, priority-based allocation, and resource utilization."
    )

    # Parameters
    st.markdown("### Parameters")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        arrival_rate = st.slider("Arrival rate (per step)", 0.0, 1.0, 0.3, 0.05)
    with c2:
        total_beds = st.number_input("Total Beds", 5, 100, 20)
    with c3:
        total_icu = st.number_input("Total ICU Beds", 1, 20, 5)
    with c4:
        total_doctors = st.number_input("Total Doctors", 3, 50, 10)

    surge_enabled = st.checkbox("Enable patient surge")
    surge_start = None
    surge_end = None
    if surge_enabled:
        c5, c6 = st.columns(2)
        with c5:
            surge_start = st.number_input("Surge start (step)", 0, 200, 50)
        with c6:
            surge_end = st.number_input("Surge end (step)", 0, 200, 100)

    if st.button("Run Simulation"):
        # Reset simulation log
        log = {
            "time": [],
            "queue_length": [],
            "avg_wait_time": [],
            "bed_utilization": [],
            "icu_utilization": [],
            "doctor_utilization": [],
        }

        # Local copies for simulation
        patients = st.session_state.patients.to_dict("records")
        resources = {
            "Beds": {"total": total_beds, "used": 0},
            "ICU_Beds": {"total": total_icu, "used": 0},
            "Doctors": {"total": total_doctors, "used": 0},
        }

        patient_counter = max((p["PatientID"] for p in patients), default=0) + 1

        def gen_patient(t):
            nonlocal patient_counter
            # Simple urgency distribution
            urgency = random.choices([1, 2, 3, 4, 5], weights=[0.3, 0.3, 0.2, 0.15, 0.05])[0]
            needs_icu = urgency >= 4
            return {
                "PatientID": patient_counter,
                "Name": f"Patient {patient_counter}",
                "Age": random.randint(10, 80),
                "Gender": random.choice(["Male", "Female"]),
                "Urgency": urgency,
                "NeedsICU": needs_icu,
                "Status": "Waiting",
                "ArrivalTime": str(t),
                "WaitTimeMin": 0,
            }

        def priority(p):
            return p["Urgency"] * 10 + p["WaitTimeMin"] * 0.1

        total_steps = 150
        for t in range(total_steps):
            is_surge = (
                surge_start is not None
                and surge_end is not None
                and surge_start <= t <= surge_end
            )
            current_rate = arrival_rate * (2.0 if is_surge else 1.0)

            # Arrivals
            if random.random() < current_rate:
                p = gen_patient(t)
                patients.append(p)
                patient_counter += 1

            # Update wait times
            for p in patients:
                if p["Status"] == "Waiting":
                    p["WaitTimeMin"] = t - int(p["ArrivalTime"]) if p["ArrivalTime"].isdigit() else t

            # Priority queue
            waiting = [p for p in patients if p["Status"] == "Waiting"]
            waiting.sort(key=priority, reverse=True)

            # Allocate resources
            for p in waiting:
                if p["Status"] != "Waiting":
                    continue
                if p["NeedsICU"]:
                    if (
                        resources["ICU_Beds"]["used"] < resources["ICU_Beds"]["total"]
                        and resources["Doctors"]["used"] < resources["Doctors"]["total"]
                    ):
                        resources["ICU_Beds"]["used"] += 1
                        resources["Doctors"]["used"] += 1
                        p["Status"] = "Treated"
                else:
                    if (
                        resources["Beds"]["used"] < resources["Beds"]["total"]
                        and resources["Doctors"]["used"] < resources["Doctors"]["total"]
                    ):
                        resources["Beds"]["used"] += 1
                        resources["Doctors"]["used"] += 1
                        p["Status"] = "Treated"

            # Randomly discharge some treated patients
            for p in patients:
                if p["Status"] == "Treated":
                    if random.random() < 0.1:
                        if p["NeedsICU"]:
                            resources["ICU_Beds"]["used"] -= 1
                        else:
                            resources["Beds"]["used"] -= 1
                        resources["Doctors"]["used"] -= 1
                        p["Status"] = "Discharged"

            # Log stats
            queue_len = sum(1 for p in patients if p["Status"] == "Waiting")
            treated = [p for p in patients if p["Status"] in ("Treated", "Discharged")]
            avg_wait = (
                sum(p["WaitTimeMin"] for p in treated) / len(treated) if treated else 0
            )
            bed_util = resources["Beds"]["used"] / resources["Beds"]["total"]
            icu_util = resources["ICU_Beds"]["used"] / resources["ICU_Beds"]["total"]
            doc_util = resources["Doctors"]["used"] / resources["Doctors"]["total"]

            log["time"].append(t)
            log["queue_length"].append(queue_len)
            log["avg_wait_time"].append(avg_wait)
            log["bed_utilization"].append(bed_util)
            log["icu_utilization"].append(icu_util)
            log["doctor_utilization"].append(doc_util)

        # Save log to session_state for possible further use
        st.session_state.simulation_log = log

        # Show plots
        st.markdown("### Simulation Results")

        fig, axs = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

        ax = axs[0]
        ax.plot(log["time"], log["queue_length"], label="Queue length")
        ax.set_ylabel("Queue length")
        ax.legend()

        ax = axs[1]
        ax.plot(log["time"], log["avg_wait_time"], label="Avg wait time", color="orange")
        ax.set_ylabel("Avg wait time (steps)")
        ax.legend()

        ax = axs[2]
        ax.plot(log["time"], log["bed_utilization"], label="Beds")
        ax.plot(log["time"], log["icu_utilization"], label="ICU")
        ax.plot(log["time"], log["doctor_utilization"], label="Doctors")
        ax.set_ylabel("Utilization")
        ax.set_xlabel("Time step")
        ax.legend()

        st.pyplot(fig)

        # Summary metrics
        max_queue = max(log["queue_length"])
        avg_wait_overall = sum(log["avg_wait_time"]) / len(log["avg_wait_time"])
        st.markdown("### Summary Metrics")
        c1, c2 = st.columns(2)
        c1.metric("Max queue length", max_queue)
        c2.metric("Average waiting time (over time)", f"{avg_wait_overall:.1f} steps")


# =========================
# Footer
# =========================
st.markdown("---")
st.markdown("Hospital Resource Manager – Hackathon Prototype")