import streamlit as st
import datetime
import time
from planner import calculate_priority, generate_study_plan
from reportlab.pdfgen import canvas
import io

# -------- PAGE CONFIG --------
st.set_page_config(page_title="AI Study Planner", layout="wide")

# -------- HEADER --------
st.markdown("## 📚 Zun's AI Study Planner")
st.caption("Generate smart study schedules in seconds")
st.divider()

# -------- LAYOUT --------
col1, col2 = st.columns(2)

# -------- INPUT SECTION --------
with col1:
    st.subheader("📥 Enter Study Details")

    subjects = []

    num_subjects = st.number_input("Number of Subjects", min_value=1, max_value=10)

    for i in range(num_subjects):
        st.markdown(f"### Subject {i+1}")

        name = st.text_input("Subject Name", key=f"name{i}")
        difficulty = st.slider("Difficulty (1-5)", 1, 5, key=f"diff{i}")
        exam_date = st.date_input("Exam Date", key=f"date{i}")

        if name:
            formatted_name = name.strip().title()
            priority = calculate_priority(difficulty, exam_date)

            subjects.append({
                "name": formatted_name,
                "priority": priority
            })

    st.divider()

    hours = st.number_input("Study Hours per Day", min_value=1, max_value=12)
    start_time = st.time_input("Start Time")

    generate_btn = st.button("Generate Study Plan 🚀")

# -------- OUTPUT SECTION --------
with col2:
    st.subheader("Generated Schedule")

    if generate_btn:

        if not subjects:
            st.warning("Please enter at least one subject")

        else:
            # -------- LOADING ANIMATION --------
            with st.spinner("🤖 AI is generating your study plan..."):

                progress = st.progress(0)
                status_text = st.empty()

                messages = [
                    "Analyzing subjects...",
                    "Calculating priorities...",
                    "Generating schedule...",
                    "Finalizing plan..."
                ]

                for i in range(100):
                    time.sleep(0.015)
                    progress.progress(i + 1)

                    if i % 25 == 0 and i // 25 < len(messages):
                        status_text.caption(messages[i // 25])

            st.success("✅ Plan generated successfully!")
            st.divider()

            # -------- GENERATE PLAN --------
            plan = generate_study_plan(subjects, hours)

            schedule_data = []

            current_time = datetime.datetime.combine(datetime.date.today(), start_time)

            for i, subject in enumerate(plan):

                total_minutes = int(subject["study_time"] * 60)

                hrs = total_minutes // 60
                mins = total_minutes % 60

                duration_text = f"{hrs} hr {mins} min"

                end_time = current_time + datetime.timedelta(minutes=total_minutes)

                start_str = current_time.strftime('%H:%M')
                end_str = end_time.strftime('%H:%M')

                # ✅ CLEAN SINGLE-LINE OUTPUT
                st.write(f"{subject['name']} → {start_str} - {end_str} ({duration_text})")

                schedule_data.append(f"{subject['name']} → {start_str} - {end_str} ({duration_text})")

                # -------- BREAK LOGIC --------
                break_minutes = 0

                if total_minutes >= 120:
                    break_minutes = 15
                elif total_minutes >= 60:
                    break_minutes = 10

                if break_minutes > 0 and i != len(plan) - 1:
                    break_end = current_time + datetime.timedelta(minutes=break_minutes)

                    break_text = f"Break ({break_minutes} min): {current_time.strftime('%H:%M')} - {break_end.strftime('%H:%M')}"

                    st.info(f"🟢 {break_text}")

                    schedule_data.append(break_text)

                    current_time = break_end
                else:
                    current_time = end_time

            # -------- PDF DOWNLOAD --------
            pdf_buffer = io.BytesIO()
            pdf = canvas.Canvas(pdf_buffer)

            y = 800
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(140, y, "Zun's AI Study Planner Timetable")

            y -= 40
            pdf.setFont("Helvetica", 10)

            for row in schedule_data:
                pdf.drawString(60, y, row)
                y -= 20

            pdf.save()
            pdf_buffer.seek(0)

            st.download_button(
                label="Download Timetable (PDF)",
                data=pdf_buffer,
                file_name="study_timetable.pdf",
                mime="application/pdf"
            )
