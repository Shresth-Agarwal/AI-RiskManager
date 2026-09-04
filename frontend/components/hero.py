import streamlit as st


def render_hero():
    hero_html = """
    <div class="hero">
        <div class="hero-eyebrow">AI-POWERED PAYMENT RISK</div>
        <div class="hero-title">
            Resolve disputes.<br>
            <span>With confidence.</span>
        </div>
        <div class="hero-subtitle">
            Intelligent risk assessment that analyzes dispute reasons,
            grounds decisions in evidence, and escalates uncertain
            cases for human review.
        </div>
        <div class="hero-pills">
            <div class="hero-pill">✦ Evidence Grounded</div>
            <div class="hero-pill">✦ Human Verified</div>
            <div class="hero-pill">✦ Portfolio Ready</div>
        </div>
    </div>
    """
    
    st.markdown(hero_html, unsafe_allow_html=True)
