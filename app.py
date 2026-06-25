import streamlit as st
from utils.grader import call_grader, suggest_rubric
from utils.report_generator import generate_pdf
from PyPDF2 import PdfReader
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

# --- SESSION STATE INIT ---
if 'submission' not in st.session_state:
    st.session_state['submission'] = ''
if 'rubric' not in st.session_state:
    st.session_state['rubric'] = ''
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- MAIN UI HEADER ---
st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0 1.5rem 0;">
        <h1 style="color: #6366f1; font-size: 3.5rem; font-weight: 900; margin: 0;">🎓 EduGrader</h1>
        <p style="color: #1e293b; font-size: 1.2rem; margin: 0; font-weight: 500;">Instant Feedback Machine • Track 2</p>
        <p style="color: #475569; font-size: 0.95rem;">Upload a PDF, paste text, or load a sample essay to get AI-powered, actionable feedback.</p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# --- SAMPLE ESSAY BUTTON ---
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
    
    # --- PDF UPLOADER ---
    uploaded_file = st.file_uploader(
        "📎 Upload PDF (or paste text below)", 
        type=["pdf"], 
        key="pdf_uploader",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        try:
            reader = PdfReader(uploaded_file)
            extracted_text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"
            
            if extracted_text.strip():
                st.session_state['submission'] = extracted_text.strip()
                st.success(f"✅ Extracted {len(extracted_text)} characters from PDF! You can edit the text below if needed.")
            else:
                st.warning("⚠️ Could not extract text from this PDF. Please paste manually.")
        except Exception as e:
            st.error(f"❌ Error reading PDF: {e}")
    
    submission = st.text_area(
        "", 
        height=250, 
        value=st.session_state['submission'],
        placeholder="Paste the student's essay, math solution, or answer here... Or upload a PDF above!", 
        label_visibility="collapsed"
    )
    
    # --- WORD COUNT & READABILITY STATS (NEW) ---
    if submission:
        word_count = len(submission.split())
        char_count = len(submission)
        sentence_count = submission.count('.') + submission.count('?') + submission.count('!')
        reading_time = max(1, round(word_count / 200))
        st.caption(f"📊 {word_count} words • {char_count} characters • {sentence_count} sentences • ~{reading_time} min read")

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
    
    # --- AI RUBRIC SUGGESTER BUTTON (NEW) ---
    col_rubric_btn, col_rubric_space = st.columns([1, 2])
    with col_rubric_btn:
        if st.button("✨ Suggest Rubric", use_container_width=True, help="AI will generate a rubric based on your submission"):
            if submission:
                with st.spinner("🧠 Generating rubric..."):
                    suggested = suggest_rubric(submission)
                    st.session_state['rubric'] = suggested
                    st.rerun()
            else:
                st.warning("⚠️ Please paste a submission first!")
    
    rubric = st.text_area(
        "", 
        height=180, 
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
            
            # Save to history (NEW)
            st.session_state['history'].append({
                "timestamp": time.strftime("%H:%M:%S"),
                "score": result['score'],
                "preview": submission[:60] + "..." if len(submission) > 60 else submission
            })

        # 1. The BIG Score
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #eef2ff, #ffffff); 
                        border-radius: 20px; padding: 1.5rem; text-align: center; 
                        border: 1px solid #e0e7ff; margin-bottom: 2rem;">
                <p style="color: #475569; margin: 0; text-transform: uppercase; letter-spacing: 2px; font-size: 0.8rem; font-weight: 600;">Total Score</p>
                <h1 style="color: #4f46e5; font-size: 4.5rem; margin: -5px 0; font-weight: 800;">{result['score']}</h1>
            </div>
        """, unsafe_allow_html=True)

        # 2. STRENGTHS & WEAKNESSES
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

        # 3. NEXT STEPS
        st.markdown('<p style="font-weight: 700; color: #1e3a8a; font-size: 1.1rem; margin-top: 1.5rem;">🚀 Next Steps (Actionable Feedback)</p>', unsafe_allow_html=True)
        if result['feedback']:
            html_feedback = "".join([f'<div class="card-feedback">💡 {f}</div>' for f in result['feedback']])
            st.markdown(f'<div style="display: flex; flex-direction: column; gap: 10px; max-width: 100%;">{html_feedback}</div>', unsafe_allow_html=True)
        else:
            st.caption("No actionable steps provided.")

        st.divider()

        # 4. EXPORT SECTION
        st.subheader("📋 Share & Export Feedback")
        
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
        
        col_left, col_right = st.columns(2, gap="large")
        
        with col_left:
            st.markdown("**📝 Copy Feedback Manually or Download as TXT**")
            st.code(copy_text, language="text")
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
        
        # 5. GRADING HISTORY (NEW)
        st.divider()
        with st.expander("📜 Grading History (Last 5 Submissions)"):
            if st.session_state['history']:
                for i, item in enumerate(reversed(st.session_state['history'][-5:])):
                    st.write(f"**{i+1}.** Score: **{item['score']}** | {item['preview']} | {item['timestamp']}")
            else:
                st.caption("No submissions graded yet.")

# --- FOOTER ---
st.divider()
st.markdown("""
    <div style="text-align: center; padding: 1rem 0 0.5rem 0;">
        <p style="color: #475569; font-size: 0.9rem; font-weight: 500;">Built with ❤️ for students by Bhavii</p>
    </div>
""", unsafe_allow_html=True)