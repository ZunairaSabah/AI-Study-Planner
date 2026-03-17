import datetime

def calculate_priority(difficulty, exam_date):
    today = datetime.date.today()
    days_left = (exam_date - today).days

    if days_left <= 0:
        days_left = 1

    urgency = 1 / days_left
    priority = difficulty + urgency

    return priority


def generate_study_plan(subjects, hours_per_day):
    total_priority = sum(subject["priority"] for subject in subjects)

    for subject in subjects:
        subject["study_time"] = round(
            (subject["priority"] / total_priority) * hours_per_day, 2
        )

    return subjects