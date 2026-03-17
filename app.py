import streamlit as st
import datetime
from planner import calculate_priority, generate_study_plan
from reportlab.pdfgen import canvas
import io

st.title("📚 AI Study Planner")

st.write("Enter your subjects to generate a smart study plan.")

subjects = []

num_subjects = st.number_input("How many subjects?", min_value=1, max_value=10)

for i in range(num_subjects):
    st.subheader(f"Subject {i+1}")

    name = st.text_input("Subject Name", key=f"name{i}")
    difficulty = st.slider("Difficulty (1-5)", 1, 5, key=f"diff{i}")
    exam_date = st.date_input("Exam Date", key=f"date{i}")

    if name:
        priority = calculate_priority(difficulty, exam_date)
        subjects.append({
            "name": name,
            "priority": priority
        })

hours = st.number_input("Study hours per day", min_value=1, max_value=12)

start_time = st.time_input("Study Start Time")

# -------- BUTTON --------
if st.button("Generate Study Plan"):

    plan = generate_study_plan(subjects, hours)

    st.subheader("📅 Your Study Schedule")

    schedule_data = []

    current_time = datetime.datetime.combine(datetime.date.today(), start_time)

    for i, subject in enumerate(plan):

        total_minutes = int(subject["study_time"] * 60)

        # Convert to hours + minutes
        hrs = total_minutes // 60
        mins = total_minutes % 60

        duration_text = f"({hrs} hr {mins} min)"

        end_time = current_time + datetime.timedelta(minutes=total_minutes)

        start_str = current_time.strftime('%H:%M')
        end_str = end_time.strftime('%H:%M')

        # Display study block
        st.write(f"{subject['name']} → {start_str} - {end_str} {duration_text}")

        schedule_data.append(f"{subject['name']} → {start_str} - {end_str} {duration_text}")


        # -------- BREAK LOGIC --------
        break_minutes = 0

        if total_minutes >= 120:
            break_minutes = 15
        elif total_minutes >= 60:
            break_minutes = 10

        # Add break if not last subject
        if break_minutes > 0 and i != len(plan) - 1:
            break_end = current_time + datetime.timedelta(minutes=break_minutes)

            break_text = f"(Break {break_minutes} min) {current_time.strftime('%H:%M')} - {break_end.strftime('%H:%M')}"

            st.write(f"🟢 {break_text}")

            schedule_data.append(break_text)

            current_time = break_end


    # -------- PDF DOWNLOAD --------

    pdf_buffer = io.BytesIO()
    pdf = canvas.Canvas(pdf_buffer)

    y = 800
    pdf.drawString(180, y, "AI Study Planner Timetable")

    y -= 40

    for row in schedule_data:
        pdf.drawString(80, y, row)
        y -= 25

    pdf.save()
    pdf_buffer.seek(0)

    st.download_button(
        label="Download Timetable (PDF)",
        data=pdf_buffer,
        file_name="study_timetable.pdf",
        mime="application/pdf"
    )