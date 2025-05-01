import streamlit as st
import math
import matplotlib.pyplot as plt

st.set_page_config(page_title="PCP-AI Clinical Risk Tool", layout="wide")
st.title("🧬 PCP-AI | Cardio-Renal-Metabolic Risk Calculator")

# Patient Inputs
st.header("🧍 Patient Inputs")
col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", 18, 120, 50)
    sex = st.selectbox("Sex", ["Male", "Female"])
    weight = st.number_input("Weight (kg)", 30.0, 250.0, 80.0)
    height = st.number_input("Height (cm)", 120.0, 220.0, 170.0)
    waist = st.number_input("Waist Circumference (cm)", 50.0, 200.0, 90.0)

with col2:
    sleep = st.number_input("Sleep Hours (per night)", 0.0, 24.0, 7.0)
    exercise = st.number_input("Exercise Minutes per Week", 0, 1000, 90)
    smoking = st.selectbox("Smoker?", ["No", "Yes"])
    systolic_bp = st.number_input("Systolic BP (mmHg)", 90, 250, 130)
    ldl = st.number_input("LDL Cholesterol (mg/dL)", 30, 300, 100)

with col3:
    fasting_glucose = st.number_input("Fasting Glucose (mg/dL)", 60.0, 300.0, 95.0)
    homa_beta = st.number_input("HOMA-Beta (%)", 0.0, 300.0, 100.0)
    gfr = st.number_input("GFR (ml/min/1.73m²)", 5.0, 150.0, 90.0)
    albumin = st.number_input("Urine Albumin (mg/g)", 0.0, 3000.0, 30.0)
    creatinine = st.number_input("Creatinine (mg/dL)", 0.1, 5.0, 1.0)

ast = st.number_input("AST (U/L)", 5.0, 500.0, 20.0)
alt = st.number_input("ALT (U/L)", 5.0, 500.0, 20.0)
platelets = st.number_input("Platelets (10^9/L)", 50.0, 1000.0, 250.0)

# Safety Flags
st.subheader("⚠️ Red Flag History")
col4, col5 = st.columns(2)
with col4:
    thyroid_cancer = st.checkbox("Thyroid Cancer (medullary/MEN)")
    pancreatitis = st.checkbox("Pancreatitis")
with col5:
    gastroparesis = st.checkbox("Gastroparesis")
    recurrent_uti = st.checkbox("Recurrent UTIs")

# Derived Metrics
bmi = weight / ((height / 100) ** 2)
waist_height_ratio = waist / height
mets = exercise / 150
fib4 = (age * ast) / (platelets * math.sqrt(alt)) if platelets > 0 and alt > 0 else 0
acr = albumin / creatinine if creatinine > 0 else 0

# KDIGO
if gfr >= 90:
    kdigo = "G1 - Normal"
elif gfr >= 60:
    kdigo = "G2 - Mild CKD"
elif gfr >= 30:
    kdigo = "G3 - Moderate CKD"
elif gfr >= 15:
    kdigo = "G4 - Severe CKD"
else:
    kdigo = "G5 - Failure"

# CV Risk Stratification
cv_risk = 0
if age > 55: cv_risk += 1
if ldl >= 130: cv_risk += 1
if smoking == "Yes": cv_risk += 1
if systolic_bp >= 140: cv_risk += 1
if fasting_glucose >= 126: cv_risk += 1
if gfr < 60: cv_risk += 1

if cv_risk <= 1:
    cv_risk_label = "Low (<5%)"
elif cv_risk == 2:
    cv_risk_label = "Moderate (5–10%)"
elif cv_risk == 3:
    cv_risk_label = "High (10–20%)"
else:
    cv_risk_label = "Very High (>20%)"

# CRM Staging
risk_factors = 0
if bmi >= 30 or waist_height_ratio >= 0.6: risk_factors += 1
if fasting_glucose >= 100: risk_factors += 1
if gfr < 60 or acr > 30: risk_factors += 1
if ldl >= 100 or smoking == "Yes" or systolic_bp >= 140: risk_factors += 1

if risk_factors == 0:
    crm_stage = "Stage 0 (No risk factors)"
elif risk_factors == 1:
    crm_stage = "Stage 1 (Early risk)"
elif risk_factors == 2:
    crm_stage = "Stage 2 (Moderate risk)"
elif risk_factors == 3:
    crm_stage = "Stage 3 (Advanced risk)"
else:
    crm_stage = "Stage 4 (Overt multi-organ risk)"

# Edmonton Obesity Staging
if bmi < 25:
    edmonton_stage = "Stage 0"
elif bmi < 30 and fasting_glucose < 100 and ldl < 100 and gfr >= 90:
    edmonton_stage = "Stage 1 (Mild risk)"
elif bmi >= 30 and (fasting_glucose >= 100 or ldl >= 130 or gfr < 90 or mets < 0.8):
    edmonton_stage = "Stage 2 (Established metabolic risk)"
elif bmi >= 35 and (fasting_glucose >= 126 or gfr < 60 or recurrent_uti or pancreatitis):
    edmonton_stage = "Stage 3 (End-organ impact)"
elif bmi >= 40 and (gfr < 30 or thyroid_cancer or gastroparesis):
    edmonton_stage = "Stage 4 (Severe functional limitation)"
else:
    edmonton_stage = "Stage 1 (Overweight, subclinical)"

# Therapy Engine
therapies = []
if crm_stage in ["Stage 2 (Moderate risk)", "Stage 3 (Advanced risk)", "Stage 4 (Overt multi-organ risk)"]:
    therapies.append("💉 GLP-1 RA (Semaglutide or Tirzepatide)")
if gfr < 90 and albumin > 30:
    therapies.append("💊 ACE inhibitor or ARB (kidney protection)")
if gfr >= 25 and gfr <= 60:
    therapies.append("💊 SGLT2 inhibitor (heart/kidney benefit)")
if gfr < 60 and albumin > 30:
    therapies.append("💊 Finerenone (CKD + T2D + albuminuria)")
if ldl >= 70 or cv_risk_label in ["High (10–20%)", "Very High (>20%)"]:
    therapies.append("💊 Statin therapy (LDL/CV prevention)")
if cv_risk_label == "Very High (>20%)":
    therapies.append("🩸 Aspirin (CV risk reduction)")

# Warnings
warnings = []
if thyroid_cancer:
    warnings.append("❗ GLP-1 contraindicated (thyroid cancer history)")
if pancreatitis or gastroparesis:
    warnings.append("⚠️ Caution: GLP-1 may aggravate GI risk")
if recurrent_uti:
    warnings.append("⚠️ SGLT2 may increase UTI risk — hygiene counseling needed")

# Charts
st.subheader("📊 Key Clinical Metrics")
metrics = {
    "BMI": round(bmi, 1),
    "METs": round(mets, 2),
    "Fib-4": round(fib4, 2),
    "HOMA-Beta": round(homa_beta, 1),
    "ACR": round(acr, 1)
}
st.bar_chart(metrics)

st.subheader("🧭 5–10 Year CV Risk Meter")
def draw_risk_meter(risk_label):
    fig, ax = plt.subplots(figsize=(6, 1.2))
    colors = ["green", "yellow", "orange", "red"]
    labels = ["Low", "Moderate", "High", "Very High"]
    position = {"Low (<5%)": 0, "Moderate (5–10%)": 1, "High (10–20%)": 2, "Very High (>20%)": 3}
    for i in range(4):
        ax.barh(0, width=1, left=i, color=colors[i])
        ax.text(i + 0.5, 0.3, labels[i], ha='center', va='center', fontsize=10, color="black")
    arrow_x = position.get(risk_label, 0)
    ax.plot([arrow_x + 0.5], [0], marker='v', markersize=12, color='black')
    ax.axis('off')
    return fig

st.pyplot(draw_risk_meter(cv_risk_label))

# Results
st.header("🧠 Risk Results")
colA, colB = st.columns(2)
with colA:
    st.markdown(f"**BMI:** {bmi:.1f}")
    st.markdown(f"**Waist/Height Ratio:** {waist_height_ratio:.2f}")
    st.markdown(f"**METs:** {mets:.2f}")
    st.markdown(f"**Fib-4 Score:** {fib4:.2f}")
    st.markdown(f"**HOMA-Beta:** {homa_beta:.1f}%")
    st.markdown(f"**ACR:** {acr:.1f}")
with colB:
    st.success(f"**CRM Stage:** {crm_stage}")
    st.info(f"**KDIGO CKD Stage:** {kdigo}")
    st.warning(f"**CV Risk (5–10 yrs):** {cv_risk_label}")
    st.markdown(f"**Edmonton Obesity Stage:** {edmonton_stage}")

# Recommendations
st.subheader("💊 Therapy Recommendations")
if therapies:
    for t in therapies:
        st.markdown(f"- {t}")
else:
    st.markdown("No medications currently indicated — optimize lifestyle.")

if warnings:
    st.subheader("⚠️ Safety Warnings")
    for w in warnings:
        st.error(w)

st.caption("© 2025 PCP-AI Tech Inc. | Based on AHA, ADA, KDIGO Guidelines")
