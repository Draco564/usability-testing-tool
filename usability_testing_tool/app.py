
import streamlit as st
import pandas as pd
import time
import os

DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

CONSENT_CSV = os.path.join(DATA_FOLDER, "consent_data.csv")
DEMOGRAPHIC_CSV = os.path.join(DATA_FOLDER, "demographic_data.csv")
TASK_CSV = os.path.join(DATA_FOLDER, "task_data.csv")
EXIT_CSV = os.path.join(DATA_FOLDER, "exit_data.csv")

def save_to_csv(data_dict, csv_file):
    df_new = pd.DataFrame([data_dict])
    if not os.path.isfile(csv_file):
        df_new.to_csv(csv_file, mode='w', header=True, index=False)
    else:
        df_new.to_csv(csv_file, mode='a', header=False, index=False)

def load_from_csv(csv_file):
    if os.path.isfile(csv_file):
        return pd.read_csv(csv_file)
    else:
        return pd.DataFrame()

def main():
    st.title("Usability Testing Tool")
    home, consent, demographics, tasks_tab, exit_tab, report = st.tabs(
        ["Home", "Consent", "Demographics", "Task", "Exit Questionnaire", "Report"]
    )

    with home:
        st.header("Introduction")
        st.write(
            """Welcome to the automated Usability Testing Tool. This application will guide participants through consent, demographics, tasks, and feedback collection, and then aggregate results into a report."""
        )
        st.subheader("Opening Script")
        st.write(
            """Hi, thank you for participating in this usability test. We are testing the interface, not you. Please think aloud as you perform each step. If you get stuck, try to explore the interface; we'll answer any questions after the session."""
        )

    with consent:
        st.header("Consent Form")
        st.write(
            """I, _________________________, consent to the use of the information collected during this usability test for the purpose of improving the product. I understand that my personal information will be kept confidential and will not be used for any commercial purpose."""
        )
        name_consent = st.text_input("Your Name")
        consent_given = st.checkbox("I have read and agree to the consent form")
        if st.button("Submit Consent"):
            if not name_consent or not consent_given:
                st.warning("Please enter your name and agree to the consent form before proceeding.")
            else:
                save_to_csv(
                    {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "name": name_consent,
                        "consent_given": True,
                    },
                    CONSENT_CSV,
                )
                st.success("Consent recorded. You may proceed to the demographics section.")

    with demographics:
        st.header("Demographic Questionnaire")
        with st.form("demographic_form"):
            name = st.text_input("Name")
            age = st.number_input("Age", min_value=18, max_value=120, step=1)
            occupation = st.text_input("Occupation")
            familiarity = st.selectbox(
                "How familiar are you with similar tools?",
                ["Not at all familiar", "Somewhat familiar", "Very familiar"],
            )
            submitted = st.form_submit_button("Submit Demographics")
            if submitted:
                save_to_csv(
                    {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "name": name,
                        "age": age,
                        "occupation": occupation,
                        "familiarity": familiarity,
                    },
                    DEMOGRAPHIC_CSV,
                )
                st.success("Demographic information recorded.")

    with tasks_tab:
        st.header("Task Page")
        tasks = [
            {
                "name": "Finding the Lesson Plans",
                "description": "You need to incorporate censorship and art into your curriculum next month. You have heard that the Blanton Museum has some TEKS aligned activities for students. How would you find this resource?",
            },
            {
                "name": "TEKS Objectives Check",
                "description": "Will the objectives and activities related to 'Overcoming Censorship Through Art' meet the XY & Z TEKS you need to cover this month?",
            },
            {
                "name": "Materials Preparation",
                "description": "What do you need to do to prepare to use 'Overcoming Censorship Through Art'?",
            },
            {
                "name": "Access Student Version",
                "description": "How would you access the online student activities related to 'Overcoming Censorship Through Art'?",
            },
        ]
        task_names = [t["name"] for t in tasks]
        selected = st.selectbox("Select Task", task_names)
        idx = task_names.index(selected)
        st.write("**Task Description:**")
        st.write(tasks[idx]["description"])

        if st.button("Start Task Timer"):
            st.session_state["start_time"] = time.time()

        if st.button("Stop Task Timer") and "start_time" in st.session_state:
            st.session_state["duration"] = time.time() - st.session_state["start_time"]

        success = st.radio(
            "Was the task completed successfully?", ["Yes", "No", "Partial"]
        )
        notes = st.text_area("Observer Notes (e.g., click paths, verbal comments)")

        if st.button("Save Task Results"):
            duration = st.session_state.get("duration", "")
            save_to_csv(
                {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "task_name": selected,
                    "success": success,
                    "duration_seconds": duration,
                    "notes": notes,
                },
                TASK_CSV,
            )
            for key in ["start_time", "duration"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("Task results saved.")

    with exit_tab:
        st.header("Exit Questionnaire")
        with st.form("exit_form"):
            satisfaction = st.slider(
                "Overall satisfaction (1=Low, 5=High):", 1, 5, 3
            )
            difficulty = st.slider(
                "Overall difficulty (1=Easy, 5=Hard):", 1, 5, 3
            )
            q1 = st.text_area(
                "What features of the product were vague or confusing to you, if any?"
            )
            q2 = st.text_area(
                "What is your impression about navigating the product? What makes it easy or difficult?"
            )
            q3 = st.text_area("What else should be included in the product?")
            submitted_exit = st.form_submit_button("Submit Exit Questionnaire")
            if submitted_exit:
                save_to_csv(
                    {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "satisfaction": satisfaction,
                        "difficulty": difficulty,
                        "q1": q1,
                        "q2": q2,
                        "q3": q3,
                    },
                    EXIT_CSV,
                )
                st.success("Exit questionnaire data saved.")

    with report:
        st.header("Usability Report - Aggregated Results")
        st.write("**Consent Data**")
        consent_df = load_from_csv(CONSENT_CSV)
        if not consent_df.empty:
            st.dataframe(consent_df)
        else:
            st.info("No consent data available yet.")

        st.write("**Demographic Data**")
        dem_df = load_from_csv(DEMOGRAPHIC_CSV)
        if not dem_df.empty:
            st.dataframe(dem_df)
        else:
            st.info("No demographic data available yet.")

        st.write("**Task Performance Data**")
        task_df = load_from_csv(TASK_CSV)
        if not task_df.empty:
            st.dataframe(task_df)
            st.subheader("Task Success Rate")
            st.bar_chart(task_df["success"].value_counts())
        else:
            st.info("No task data available yet.")

        st.write("**Exit Questionnaire Data**")
        exit_df = load_from_csv(EXIT_CSV)
        if not exit_df.empty:
            st.dataframe(exit_df)
            st.subheader("Exit Questionnaire Averages")
            st.write(f"**Avg Satisfaction**: {exit_df['satisfaction'].mean():.2f}")
            st.write(f"**Avg Difficulty**: {exit_df['difficulty'].mean():.2f}")
        else:
            st.info("No exit questionnaire data available yet.")

if __name__ == "__main__":
    main()
