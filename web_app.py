import csv

import streamlit as st

import main as reports

import os


st.set_page_config(
    page_title="FactoryPilot AI",
    layout="centered",
)

st.title("FactoryPilot AI")
st.markdown("## Factory Production Dashboard")
st.caption("Daily production performance at a glance")
st.caption("Daily production reports for your factory")

st.subheader("Add a daily report")

with st.form("production_report_form"):
    factory_name = st.text_input("Factory name")
    daily_quantity = st.number_input(
        "Today's production (units)",
        min_value=0,
        value=0,
        step=1,
    )
    daily_target = st.number_input(
        "Daily production target (units)",
        min_value=1,
        value=1,
        step=1,
    )
    submitted = st.form_submit_button(
        "Save report",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if not factory_name.strip():
        st.error("Enter a factory name before saving the report.")
    else:
        try:
            new_report = reports.build_report(
                factory_name,
                int(daily_quantity),
                int(daily_target),
            )
            reports.save_report(new_report)
        except ValueError as error:
            st.error(str(error))
        except (OSError, csv.Error) as error:
            st.error(f"Could not save the report: {error}")
        else:
            st.success("Daily production report saved.")

st.divider()
st.subheader("Previous reports")

try:
    saved_reports = reports.read_saved_reports()
except (OSError, csv.Error, UnicodeError) as error:
    st.error(f"Could not read saved reports: {error}")
else:
    if not saved_reports:
        st.info("No saved reports yet. Add a report above to get started.")
    else:
        table_rows = []

        for report in saved_reports:
            achieved = report.get("achieved_percentage") or "-"
            if achieved != "-" and not achieved.endswith("%"):
                achieved += "%"

            table_rows.append(
                {
                    "Date": report.get("date") or "-",
                    "Factory": report.get("factory_name") or "-",
                    "Production (units)": report.get("production_quantity") or "-",
                    "Target (units)": report.get("daily_target") or "-",
                    "Achieved": achieved,
                    "Target met": report.get("target_met") or "-",
                }
            )

        st.dataframe(
            table_rows,
            width="stretch",
            hide_index=True,
        )

        st.divider()
        st.subheader("Production Summary")

        total_production = sum(
            int(report.get("production_quantity") or 0)
            for report in saved_reports
        )
        total_target = sum(
            int(report.get("daily_target") or 0)
            for report in saved_reports
        )

        achievement = (
            total_production / total_target * 100
            if total_target > 0
            else 0
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Production", total_production)
        col2.metric("Total Target", total_target)
        col3.metric("Achievement", f"{achievement:.1f}%")

        met_count = sum(
            1 for report in saved_reports
            if (report.get("target_met") or "").strip().lower() == "yes"
        )
        missed_count = sum(
            1 for report in saved_reports
            if (report.get("target_met") or "").strip().lower() == "no"
        )

        st.subheader("Target Performance")
        col4, col5 = st.columns(2)
        col4.metric("Target Met", met_count)
        col5.metric("Target Missed", missed_count)

        chart_data = {
            "Production": [
                int(report.get("production_quantity") or 0)
                for report in saved_reports
            ],
            "Target": [
                int(report.get("daily_target") or 0)
                for report in saved_reports
            ],
        }

        st.subheader("Production vs Target")
        st.bar_chart(chart_data, stack=False)
        
        st.divider()

st.header("Employee Performance")
st.caption("Track individual and team production performance")

employee_tab, team_tab = st.tabs(
    ["Individual Employees", "Team Performance"]
)

with employee_tab:
    st.subheader("Individual Employee Report")

    with st.form("employee_performance_form"):
        employee_name = st.text_input("Employee Name")
        employee_id = st.text_input("Employee ID")
        employee_target = st.number_input(
            "Daily Target (units)", min_value=0, step=1
        )
        employee_actual = st.number_input(
            "Actual Production (units)", min_value=0, step=1
        )

        employee_submit = st.form_submit_button(
            "Calculate Performance"
        )
 
        if employee_submit:
                if employee_name.strip() and employee_id.strip():
                    employee_report = {
                        "employee_name": employee_name.strip(),
                        "employee_id": employee_id.strip(),
                        "daily_target": employee_target,
                        "actual_production": employee_actual,
                    }

                    reports.save_performance_report(
                        employee_report,
                        "employee_performance.csv"
                    )

                    percentage = (
                        employee_actual / employee_target * 100
                        if employee_target > 0
                        else 0
                    )

                    st.metric("Achievement", f"{percentage:.1f}%")
                    st.metric("Actual Production", employee_actual)
                    st.metric("Daily Target", employee_target)
                else:
                    st.warning("Please enter Employee Name and Employee ID.")
with team_tab:
    st.subheader("Team Performance Report")

    with st.form("team_performance_form"):
        team_name = st.text_input("Team Name")
        team_target = st.number_input(
            "Team Daily Target (units)", min_value=0, step=1
        )
        team_actual = st.number_input(
            "Team Actual Production (units)", min_value=0, step=1
        )

        team_submit = st.form_submit_button(
            "Calculate Team Performance"
        )

    if team_submit:
        if team_name.strip():
                        team_report = {
                "team_name": team_name.strip(),
                "daily_target": team_target,
                "actual_production": team_actual,
            }

            reports.save_performance_report(
                team_report,
                "team_performance.csv"
            )
            team_percentage = (
                team_actual / team_target * 100
                if team_target > 0
                else 0
            )
            st.metric("Team Achievement", f"{team_percentage:.1f}%")
            st.metric("Team Production", team_actual)
            st.metric("Team Target", team_target)
        else:
            st.warning("Please enter a Team Name.")
