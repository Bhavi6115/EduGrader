import streamlit as st
from utils.grader import call_grader
from utils.report_generator import generate_pdf
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="EduGrader AI", page_icon="🎓", layout="wide")

# --- LOAD CUSTOM CSS ---
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- HIDE DEFAULT STREAMLIT FOOTER/MENU ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE INIT (For Sample Essay pre-fill) ---
if 'submission' not in st.session_state:
    st.session_state['submission'] = ''
if 'rubric' not in st.session_state:
    st.session_state['rubric'] = ''

# --- MAIN UI HEADER (HIGH CONTRAST FIXED) ---
st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0 1.5rem 0;">
        <h1 style="color: #6366f1; font-size: 3.5rem; font-weight: 900; margin: 0;">🎓 EduGrader</h1>
        <p style="color: #1e293b; font-size: 1.2rem; margin: 0; font-weight: 500;">Instant Feedback Machine • Track 2</p>
        <p style="color: #475569; font-size: 0.95rem;">Paste the student submission and rubric to get AI-powered, actionable feedback.</p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# --- SAMPLE ESSAY BUTTON (Above the inputs) ---
col_sample_btn, col_sample_space = st.columns([1, 5])
with col_sample_btn:
    if st.button("📝 Load Sample Essay", use_container_width=True):
        st.session_state['submission'] = """The ocean is filled with plastic pollution and this is a big problem for marine life. Animals like turtles and whales often eat plastic bags thinking they are jellyfish or food, which makes them very sick and sometimes causes death. We should reduce our use of single-use plastics like straws and water bottles to help save the ocean. If we don't act now, future generations will see a ocean full of trash instead of fish, which is sad. So we must recycle more and tell others to do the same."""
        st.session_state['rubric'] = "Grammar & Sentence Structure: 30%, Argument & Persuasion: 30%, Vocabulary & Clarity: 25%, Conclusion Strength: 15%"
        st.rerun()

# --- INPUT SECTION ---
col_input_left, col_input_right = st.columns(2, gap="large")

with col_input_left:
    st.markdown('<p style="font-weight: 600; color: #1e293b;">📝 Student Submission</p>', unsafe_allow_html=True)
    submission = st.text_area(
        "", 
        height=280, 
        value=st.session_state['submission'],
        placeholder="Paste the student's essay, math solution, or answer here...", 
        label_visibility="collapsed"
    )

with col_input_right:
    st.markdown('<p style="font-weight: 600; color: #1e293b;">📋 Quick Rubric Templates</p>', unsafe_allow_html=True)
    rubric_preset = st.selectbox(
        "Choose a preset or select 'Custom'",
        ["Custom", "Standard Essay (Grammar 40%, Clarity 30%, Relevance 30%)", 
         "Math Problem (Accuracy 50%, Steps 30%, Presentation 20%)", 
         "Science Report (Hypothesis 30%, Data 40%, Conclusion 30%)"],
        label_visibility="collapsed"
    )
    
    if rubric_preset != "Custom":
        default_rubric = rubric_preset.split("(", 1)[1].rstrip(")")
    else:
        default_rubric = "Grammar 40%, Clarity 30%, Relevance 30%"
    
    st.markdown('<p style="font-weight: 600; color: #1e293b; margin-top: 10px;">📋 Grading Rubric</p>', unsafe_allow_html=True)
    rubric = st.text_area(
        "", 
        height=200, 
        value=st.session_state['rubric'] or default_rubric,
        label_visibility="collapsed",
        help="Define the criteria and weightage for grading."
    )

# --- CENTERED GRADE BUTTON ---
col_center, _ = st.columns([1, 1])
with col_center:
    grade_button = st.button("🚀 Grade Submission Now", use_container_width=True, type="primary")

# --- OUTPUT SECTION ---
if grade_button and submission:
    if not rubric:
        st.warning("⚠️ Please define a rubric.")
    else:
        with st.spinner("🧠 Analyzing submission... (This takes ~2 seconds)"):
            result = call_grader(rubric, submission, translate=False)
            time.sleep(0.5)

        # 1. The BIG Score
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #eef2ff, #ffffff); 
                        border-radius: 20px; padding: 1.5rem; text-align: center; 
                        border: 1px solid #e0e7ff; margin-bottom: 2rem;">
                <p style="color: #475569; margin: 0; text-transform: uppercase; letter-spacing: 2px; font-size: 0.8rem; font-weight: 600;">Total Score</p>
                <h1 style="color: #4f46e5; font-size: 4.5rem; margin: -5px 0; font-weight: 800;">{result['score']}</h1>
            </div>
        """, unsafe_allow_html=True)

        # 2. STRENGTHS & WEAKNESSES (Side by Side)
        col_str, col_weak = st.columns(2, gap="large")
        
        with col_str:
            st.markdown('<p style="font-weight: 700; color: #065f46; font-size: 1.1rem;">✅ Strengths</p>', unsafe_allow_html=True)
            if result['strengths']:
                html_strengths = "".join([f'<span class="pill-green">{s}</span>' for s in result['strengths']])
                st.markdown(f'<div style="display: flex; flex-wrap: wrap; gap: 8px;">{html_strengths}</div>', unsafe_allow_html=True)
            else:
                st.caption("No specific strengths detected.")

        with col_weak:
            st.markdown('<p style="font-weight: 700; color: #991b1b; font-size: 1.1rem;">⚠️ Areas to Improve</p>', unsafe_allow_html=True)
            if result['weaknesses']:
                html_weaknesses = "".join([f'<span class="pill-red">{w}</span>' for w in result['weaknesses']])
                st.markdown(f'<div style="display: flex; flex-wrap: wrap; gap: 8px;">{html_weaknesses}</div>', unsafe_allow_html=True)
            else:
                st.caption("No major weaknesses found.")

        # 3. NEXT STEPS (Full Width)
        st.markdown('<p style="font-weight: 700; color: #1e3a8a; font-size: 1.1rem; margin-top: 1.5rem;">🚀 Next Steps (Actionable Feedback)</p>', unsafe_allow_html=True)
        if result['feedback']:
            html_feedback = "".join([f'<div class="card-feedback">💡 {f}</div>' for f in result['feedback']])
            st.markdown(f'<div style="display: flex; flex-direction: column; gap: 10px; max-width: 100%;">{html_feedback}</div>', unsafe_allow_html=True)
        else:
            st.caption("No actionable steps provided.")

        st.divider()

        # 4. COPY & DOWNLOAD SECTION (100% RELIABLE)
        st.subheader("📋 Share & Export Feedback")
        
        # Prepare the formatted text
        copy_text = f"🎓 EduGrader Feedback Report\n"
        copy_text += f"{'='*40}\n\n"
        copy_text += f"📊 Total Score: {result['score']}\n\n"
        
        copy_text += "✅ Strengths:\n"
        for s in result['strengths']:
            copy_text += f"  - {s}\n"
        
        copy_text += "\n⚠️ Areas for Improvement:\n"
        for w in result['weaknesses']:
            copy_text += f"  - {w}\n"
        
        copy_text += "\n🚀 Next Steps (Actionable Feedback):\n"
        for f in result['feedback']:
            copy_text += f"  - {f}\n"
        
        copy_text += f"\n{'='*40}\n"
        copy_text += "Generated by EduGrader • Built with ❤️ for students by Bhavii"
        
        # Two columns: Left = Code block + TXT download, Right = PDF download
        col_left, col_right = st.columns(2, gap="large")
        
        with col_left:
            st.markdown("**📝 Copy Feedback Manually or Download as TXT**")
            
            # Display the text in a clean code block
            st.code(copy_text, language="text")
            
            # Download as TXT button
            st.download_button(
                label="📄 Download as TXT File",
                data=copy_text,
                file_name="feedback_report.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_txt"
            )
        
        with col_right:
            st.markdown("**📥 Download PDF Report**")
            
            # PDF Download Button
            try:
                pdf_buffer = generate_pdf(result)
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=pdf_buffer,
                    file_name="student_feedback_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="download_pdf"
                )
            except Exception as e:
                st.error(f"❌ Could not generate PDF: {e}")

# --- FOOTER (HIGH CONTRAST FIXED) ---
st.divider()
st.markdown("""
    <div style="text-align: center; padding: 1rem 0 0.5rem 0;">
        <p style="color: #475569; font-size: 0.9rem; font-weight: 500;">Built with ❤️ for students by Bhavii</p>
    </div>
""", unsafe_allow_html=True)