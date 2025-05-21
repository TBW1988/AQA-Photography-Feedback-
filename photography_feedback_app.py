
import streamlit as st
import openai
from fpdf import FPDF
import os

# --- CONFIG ---
openai.api_key = st.secrets["OPENAI_API_KEY"]

feedback_templates = {
    "AO1": {
        (1, 6): "Basic development of ideas. More research into contextual sources needed.",
        (7, 12): "Ideas are developing. Deepen contextual connections.",
        (13, 18): "Solid development with relevant research.",
        (19, 24): "Highly focused, sustained development with strong contextual links."
    },
    "AO2": {
        (1, 6): "Limited experimentation with techniques.",
        (7, 12): "Some exploration; continue refining your media use.",
        (13, 18): "Competent technique and review processes.",
        (19, 24): "Excellent control and exploration of media and processes."
    },
    "AO3": {
        (1, 6): "Recording is basic; develop technical and critical skills.",
        (7, 12): "Developing ideas with some reflection.",
        (13, 18): "Confident recording of relevant observations.",
        (19, 24): "Excellent recording with technical and critical insight."
    },
    "AO4": {
        (1, 6): "Limited personal response.",
        (7, 12): "Some engagement; develop final outcome further.",
        (13, 18): "Personal, generally meaningful response.",
        (19, 24): "Highly personal, resolved and meaningful outcome."
    }
}

def get_template_feedback(ao, score):
    for range_tuple, comment in feedback_templates[ao].items():
        if range_tuple[0] <= score <= range_tuple[1]:
            return comment
    return "Invalid score."

def generate_gpt_feedback(ao_scores, teacher_comments):
    prompt = f'''
    You are an AQA A-Level Photography teacher. Based on the following marks and optional teacher notes, write constructive, student-facing feedback for each AO.

    Marks:
    AO1: {ao_scores['AO1']}
    AO2: {ao_scores['AO2']}
    AO3: {ao_scores['AO3']}
    AO4: {ao_scores['AO4']}

    Teacher notes (optional):
    AO1: {teacher_comments.get('AO1', '')}
    AO2: {teacher_comments.get('AO2', '')}
    AO3: {teacher_comments.get('AO3', '')}
    AO4: {teacher_comments.get('AO4', '')}

    Use formal, positive, and developmental language. Provide one paragraph per AO.
    '''

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response['choices'][0]['message']['content']

def export_to_pdf(student_name, feedback_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, f"Photography Feedback for {student_name}\n", align='L')

    for line in feedback_text.split('\n'):
        pdf.multi_cell(0, 10, line.strip(), align='L')

    filename = f"{student_name.replace(' ', '_')}_photography_feedback.pdf"
    pdf.output(filename)
    return filename

# --- STREAMLIT UI ---
st.title("📸 AQA A-Level Photography Feedback Generator")

student_name = st.text_input("Student Name", "")
st.markdown("### Enter Marks (0–24)")
ao_scores = {
    "AO1": st.slider("AO1: Develop ideas", 0, 24, 12),
    "AO2": st.slider("AO2: Explore techniques", 0, 24, 12),
    "AO3": st.slider("AO3: Record ideas", 0, 24, 12),
    "AO4": st.slider("AO4: Final response", 0, 24, 12),
}

st.markdown("### Optional Teacher Notes")
teacher_comments = {
    "AO1": st.text_area("AO1 Comment", ""),
    "AO2": st.text_area("AO2 Comment", ""),
    "AO3": st.text_area("AO3 Comment", ""),
    "AO4": st.text_area("AO4 Comment", ""),
}

if st.button("Generate Feedback"):
    with st.spinner("Generating GPT-enhanced feedback..."):
        feedback = generate_gpt_feedback(ao_scores, teacher_comments)
        st.subheader("📋 Student Feedback")
        st.markdown(feedback)

        if student_name:
            filename = export_to_pdf(student_name, feedback)
            with open(filename, "rb") as f:
                st.download_button(
                    label="📄 Download Feedback as PDF",
                    data=f,
                    file_name=filename,
                    mime="application/pdf"
                )
