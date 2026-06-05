from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
import base64
import json
from typing import Dict, List, Tuple
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse


@dataclass
class PatientProfile:
    """Store and manage patient health profile"""
    age: int
    bmi: float
    family_history: bool
    exercise_frequency: int  # days per week
    diet_quality: str  # poor, fair, good
    blood_pressure_systolic: int
    blood_glucose_fasting: float
    stress_level: int  # 1-10 scale
    sleep_hours: float
    medications: bool
    name: str = ""


class DiabetesRiskCalculator:
    """Advanced diabetes risk assessment with multiple factors"""
    
    # Weighted scoring factors
    WEIGHTS = {
        "age": 0.20,
        "bmi": 0.25,
        "family_history": 0.15,
        "exercise": 0.15,
        "diet": 0.10,
        "blood_pressure": 0.08,
        "glucose": 0.05,
        "lifestyle": 0.02
    }
    
    RISK_THRESHOLDS = {
        "high": 0.70,
        "moderate": 0.50,
        "low": 0.30
    }
    
    def calculate_age_risk(self, age: int) -> float:
        """Age-based risk scoring"""
        if age < 30:
            return 0.1
        elif age < 40:
            return 0.3
        elif age < 50:
            return 0.5
        elif age < 60:
            return 0.7
        else:
            return 0.9
    
    def calculate_bmi_risk(self, bmi: float) -> float:
        """BMI-based risk scoring"""
        if bmi < 18.5:
            return 0.1
        elif bmi < 25:
            return 0.2
        elif bmi < 30:
            return 0.5
        elif bmi < 35:
            return 0.75
        else:
            return 1.0
    
    def calculate_exercise_risk(self, days: int) -> float:
        """Exercise frequency risk scoring"""
        if days >= 5:
            return 0.1
        elif days >= 3:
            return 0.3
        elif days >= 1:
            return 0.6
        else:
            return 1.0
    
    def calculate_diet_risk(self, diet_quality: str) -> float:
        """Diet quality risk scoring"""
        return {"good": 0.2, "fair": 0.6, "poor": 1.0}.get(diet_quality, 0.5)
    
    def calculate_overall_risk(self, profile: PatientProfile) -> Tuple[float, Dict]:
        """Calculate comprehensive risk score"""
        scores = {
            "Age": self.calculate_age_risk(profile.age),
            "BMI": self.calculate_bmi_risk(profile.bmi),
            "Family History": 0.7 if profile.family_history else 0.1,
            "Exercise": self.calculate_exercise_risk(profile.exercise_frequency),
            "Diet": self.calculate_diet_risk(profile.diet_quality),
            "Blood Pressure": 0.8 if profile.blood_pressure_systolic > 140 else 0.4 if profile.blood_pressure_systolic > 120 else 0.2,
            "Blood Glucose": 0.9 if profile.blood_glucose_fasting > 126 else 0.6 if profile.blood_glucose_fasting > 100 else 0.2,
            "Lifestyle": (profile.stress_level / 10) * 0.5 + (abs(profile.sleep_hours - 7) / 7) * 0.5
        }
        
        factor_weight_keys = {
            "Age": "age",
            "BMI": "bmi",
            "Family History": "family_history",
            "Exercise": "exercise",
            "Diet": "diet",
            "Blood Pressure": "blood_pressure",
            "Blood Glucose": "glucose",
            "Lifestyle": "lifestyle"
        }
        weighted_score = sum(
            scores[factor] * self.WEIGHTS[factor_weight_keys[factor]]
            for factor in scores
        )
        
        return weighted_score, scores
    
    def get_risk_category(self, score: float) -> str:
        """Categorize risk level"""
        if score >= self.RISK_THRESHOLDS["high"]:
            return "HIGH RISK"
        elif score >= self.RISK_THRESHOLDS["moderate"]:
            return "MODERATE RISK"
        else:
            return "LOW RISK"
    
    def get_recommendations(self, profile: PatientProfile, score: float) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if profile.bmi >= 30:
            recommendations.append("• Aim to reduce BMI through diet and exercise")
        if profile.exercise_frequency < 5:
            recommendations.append("• Increase physical activity to at least 150 minutes/week")
        if profile.diet_quality != "good":
            recommendations.append("• Improve diet quality - focus on whole grains, vegetables, and lean proteins")
        if profile.blood_pressure_systolic > 120:
            recommendations.append("• Monitor and manage blood pressure")
        if profile.blood_glucose_fasting > 100:
            recommendations.append("• Get blood glucose tested regularly")
        if profile.stress_level > 7:
            recommendations.append("• Implement stress reduction techniques (meditation, yoga)")
        if profile.sleep_hours < 6 or profile.sleep_hours > 9:
            recommendations.append("• Aim for 7-9 hours of quality sleep per night")
        if profile.family_history and score > 0.5:
            recommendations.append("• Consult with healthcare provider for preventive screening")
        
        if not recommendations:
            recommendations.append("• Maintain current healthy lifestyle habits")
        
        return recommendations
    
    def generate_plot_base64(self, factor_scores: Dict) -> str:
        """Render the factor score chart as an inline base64 image."""
        fig, ax = plt.subplots(figsize=(9, 5))
        factors = list(factor_scores.keys())
        scores = list(factor_scores.values())
        colors = ['#dc3545' if s > 0.7 else '#fd7e14' if s > 0.4 else '#28a745' for s in scores]

        ax.bar(factors, scores, color=colors, alpha=0.8)
        ax.set_title('Risk Factor Scores', fontsize=14, fontweight='bold')
        ax.set_ylabel('Risk Score (0-1)')
        ax.set_ylim(0, 1)
        ax.axhline(0.7, color='#dc3545', linestyle='--', alpha=0.7, label='High Risk')
        ax.axhline(0.4, color='#fd7e14', linestyle='--', alpha=0.7, label='Moderate Risk')
        ax.legend()
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=40, ha='right')
        plt.tight_layout()

        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=100)
        plt.close(fig)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')

    def generate_gauge_base64(self, score: float, risk_category: str) -> str:
        """Render the overall risk gauge as an inline base64 image."""
        fig, ax = plt.subplots(figsize=(9, 2.5))
        ax.barh([0], [1], color='#e9ecef', height=0.6, alpha=0.3)
        ax.barh([0], [score], color='#667eea', height=0.6)
        ax.set_xlim(0, 1)
        ax.set_yticks([])
        ax.set_xlabel('Overall risk score')
        ax.set_title(f'Overall Risk Gauge — {risk_category}', fontsize=12, fontweight='bold')
        ax.text(score + 0.02, 0, f'{score:.1%}', va='center', fontsize=11, fontweight='600')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#dee2e6')
        plt.tight_layout()

        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=100)
        plt.close(fig)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')

    def get_top_risk_factors(self, factor_scores: Dict, count: int = 3) -> List[Tuple[str, float]]:
        return sorted(factor_scores.items(), key=lambda x: x[1], reverse=True)[:count]

app = FastAPI()
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Diabetes Risk Assessment</title>
        <meta name="description" content="Interactive diabetes risk assessment with personalized recommendations, charts, and history storage.">
        <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='45' fill='%23667eea'/%3E%3Cpath d='M50 20v60M35 50h30' stroke='%23fff' stroke-width='10' stroke-linecap='round'/%3E%3C/svg%3E">
        <style>
            :root {
                color-scheme: light;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #e8f3ff;
            }
            * { box-sizing: border-box; }
            body {
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #e8f3ff 0%, #cde7ff 100%);
                min-height: 100vh;
                color: #2d3b4f;
            }
            .page-shell {
                padding: 30px 20px;
                max-width: 1200px;
                margin: 0 auto;
            }
            .hero {
                background: rgba(244,249,255,0.98);
                border-radius: 24px;
                box-shadow: 0 25px 60px rgba(28, 63, 109, 0.12);
                padding: 30px;
                margin-bottom: 24px;
            }
            .hero h1 {
                margin: 0 0 12px;
                font-size: clamp(2rem, 3vw, 3rem);
                letter-spacing: -0.04em;
            }
            .hero p {
                margin: 0;
                color: #4b4b63;
                line-height: 1.75;
            }
            .pill-buttons {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin: 24px 0 0;
            }
            .pill-buttons button {
                border-radius: 999px;
                padding: 12px 18px;
                border: 1px solid rgba(90,131,238,0.28);
                background: #ffffff;
                color: #1f314b;
                font-weight: 600;
                min-width: 170px;
            }
            .grid {
                display: grid;
                gap: 24px;
                grid-template-columns: 1.4fr 1fr;
            }
            .card {
                background: rgba(245,250,255,0.98);
                border-radius: 22px;
                padding: 26px;
                box-shadow: 0 18px 40px rgba(45, 81, 127, 0.12);
            }
            .card h2 {
                margin-top: 0;
                font-size: 1.6rem;
            }
            .form-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 18px;
            }
            .form-grid.full-width {
                grid-column: span 2;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 700;
                color: #1f314b;
            }
            input, select {
                width: 100%;
                padding: 14px 16px;
                border: 1px solid #cbd7ed;
                border-radius: 14px;
                font-size: 1rem;
                background: #fbfdff;
                color: #2d3b53;
            }
            input:focus, select:focus {
                outline: none;
                box-shadow: 0 0 0 4px rgba(90,131,238,0.16);
                border-color: #5a83ee;
            }
            .helper-text {
                font-size: 0.92rem;
                color: #475b77;
                margin-top: 6px;
            }
            .radio-group {
                display: grid;
                gap: 10px;
            }
            .radio-group label {
                font-weight: 500;
            }
            .radio-row {
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
            }
            .radio-row input {
                margin-right: 8px;
            }
            .warning-box {
                background: #eff6ff;
                border-left: 4px solid #74a5ff;
                padding: 16px;
                border-radius: 14px;
                color: #1f3d7a;
                display: none;
                margin-bottom: 20px;
            }
            .history-table {
                width: 100%;
                border-collapse: collapse;
            }
            .history-table th, .history-table td {
                text-align: left;
                padding: 12px 14px;
                border-bottom: 1px solid #eef0f6;
            }
            .history-table th {
                color: #5f5f74;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.02em;
            }
            .history-empty {
                margin: 14px 0 0;
                color: #676777;
            }
            .section-footer {
                display: flex;
                justify-content: space-between;
                gap: 12px;
                flex-wrap: wrap;
                align-items: center;
            }
            .small-button {
                background: #f8f9ff;
                color: #2d2d39;
                border: 1px solid #d6dbf5;
                padding: 10px 16px;
                border-radius: 12px;
                min-width: 160px;
            }
            .learn-more ul {
                padding-left: 20px;
                margin: 16px 0 0;
            }
            .learn-more li {
                margin-bottom: 10px;
                color: #4d4d5f;
            }
            .disclaimer {
                font-size: 0.95rem;
                color: #66697d;
                margin-top: 18px;
                line-height: 1.65;
            }
            @media (max-width: 900px) {
                .grid {
                    grid-template-columns: 1fr;
                }
                .form-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="page-shell">
            <div class="hero">
                <h1>Diabetes Risk Assessment</h1>
                <p>Get personalized risk insights, expert recommendations, and a fullscreen-ready report. Use the full assessment or switch to quick mode for faster results.</p>
                <div class="pill-buttons">
                    <button type="button" id="show-full">Full assessment</button>
                    <button type="button" id="show-quick">Quick assessment</button>
                </div>
            </div>

            <div class="grid">
                <section class="card">
                    <h2>Advanced assessment</h2>
                    <div class="warning-box" id="warning-box"></div>
                    <form id="full-form" action="/submit" method="post" onsubmit="return validateForm(this);">
                        <div class="form-grid">
                            <div>
                                <label for="name">Your name (optional)</label>
                                <input type="text" id="name" name="name" placeholder="e.g. Sam" autocomplete="name">
                                <p class="helper-text">Add a name so you can save and identify later assessments.</p>
                            </div>
                            <div>
                                <label for="age">Age</label>
                                <input type="number" id="age" name="age" min="18" max="120" required>
                                <p class="helper-text">Enter age between 18 and 120 years.</p>
                            </div>
                            <div>
                                <label for="bmi">BMI</label>
                                <input type="number" id="bmi" name="bmi" step="0.1" min="10" max="60" required>
                                <p class="helper-text">Body Mass Index helps estimate metabolic risk.</p>
                            </div>
                            <div class="form-grid full-width">
                                <label>Family history of diabetes</label>
                                <div class="radio-row">
                                    <label><input type="radio" name="family_history" value="yes"> Yes</label>
                                    <label><input type="radio" name="family_history" value="no" checked> No</label>
                                </div>
                            </div>
                            <div>
                                <label for="exercise_frequency">Exercise per week</label>
                                <input type="number" id="exercise_frequency" name="exercise_frequency" min="0" max="7" required>
                                <p class="helper-text">Days of exercise help assess lifestyle risk.</p>
                            </div>
                            <div>
                                <label for="diet_quality">Diet quality</label>
                                <select id="diet_quality" name="diet_quality" required>
                                    <option value="good">Good</option>
                                    <option value="fair">Fair</option>
                                    <option value="poor">Poor</option>
                                </select>
                            </div>
                            <div>
                                <label for="blood_pressure_systolic">Blood pressure</label>
                                <input type="number" id="blood_pressure_systolic" name="blood_pressure_systolic" min="80" max="200" required>
                                <p class="helper-text">Systolic pressure is a key cardiovascular risk factor.</p>
                            </div>
                            <div>
                                <label for="blood_glucose_fasting">Fasting glucose</label>
                                <input type="number" id="blood_glucose_fasting" name="blood_glucose_fasting" min="60" max="300" required>
                                <p class="helper-text">Use your latest fasting glucose reading.</p>
                            </div>
                            <div>
                                <label for="stress_level">Stress level</label>
                                <input type="number" id="stress_level" name="stress_level" min="1" max="10" required>
                                <p class="helper-text">Higher stress increases metabolic risk.</p>
                            </div>
                            <div>
                                <label for="sleep_hours">Sleep hours</label>
                                <input type="number" id="sleep_hours" name="sleep_hours" step="0.1" min="3" max="12" required>
                                <p class="helper-text">Aim for 7–9 hours of quality sleep.</p>
                            </div>
                            <div class="form-grid full-width">
                                <label>Medications for hypertension/cholesterol</label>
                                <div class="radio-row">
                                    <label><input type="radio" name="medications" value="yes"> Yes</label>
                                    <label><input type="radio" name="medications" value="no" checked> No</label>
                                </div>
                            </div>
                        </div>
                        <button type="submit">Get full assessment</button>
                    </form>
                </section>

                <section class="card">
                    <h2>Quick assessment</h2>
                    <form id="quick-form" action="/quick_submit" method="post" onsubmit="return validateForm(this);" style="display:none;">
                        <div class="form-grid">
                            <div>
                                <label for="quick-name">Name</label>
                                <input type="text" id="quick-name" name="name" placeholder="Optional">
                            </div>
                            <div>
                                <label for="quick-age">Age</label>
                                <input type="number" id="quick-age" name="age" min="18" max="120" required>
                            </div>
                            <div>
                                <label for="quick-bmi">BMI</label>
                                <input type="number" id="quick-bmi" name="bmi" step="0.1" min="10" max="60" required>
                            </div>
                            <div class="form-grid full-width">
                                <label>Family history</label>
                                <div class="radio-row">
                                    <label><input type="radio" name="family_history" value="yes"> Yes</label>
                                    <label><input type="radio" name="family_history" value="no" checked> No</label>
                                </div>
                            </div>
                            <div>
                                <label for="quick-exercise_frequency">Exercise</label>
                                <input type="number" id="quick-exercise_frequency" name="exercise_frequency" min="0" max="7" required>
                            </div>
                            <div>
                                <label for="quick-diet_quality">Diet</label>
                                <select id="quick-diet_quality" name="diet_quality" required>
                                    <option value="good">Good</option>
                                    <option value="fair">Fair</option>
                                    <option value="poor">Poor</option>
                                </select>
                            </div>
                        </div>
                        <button type="submit">Get quick assessment</button>
                    </form>
                    <p class="helper-text">Quick mode uses fewer inputs and default health assumptions for a fast assessment.</p>
                </section>
            </div>

            <section class="card">
                <div class="section-footer">
                    <h2>Saved assessment history</h2>
                    <button type="button" class="small-button" onclick="clearHistory();">Clear history</button>
                </div>
                <table class="history-table" id="history-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Age</th>
                            <th>Risk</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
                <p class="history-empty" id="history-empty">No saved assessments yet.</p>
            </section>

            <section class="card learn-more">
                <h2>Learn more</h2>
                <p>Understanding diabetes risk helps you make better lifestyle decisions. These factors matter most:</p>
                <ul>
                    <li><strong>Body weight:</strong> High BMI increases insulin resistance.</li>
                    <li><strong>Blood pressure:</strong> Hypertension raises diabetes and heart risk.</li>
                    <li><strong>Glucose levels:</strong> Fasting readings signal metabolic health.</li>
                    <li><strong>Diet and exercise:</strong> Small daily habits have big long-term impact.</li>
                </ul>
                <p class="disclaimer">This tool provides informational guidance only and is not a medical diagnosis. Consult a healthcare professional for clinical advice.</p>
            </section>
        </div>

        <script>
            const storageKey = 'ebhaanDiabetesAssessments';
            const warningBox = document.getElementById('warning-box');
            const fullForm = document.getElementById('full-form');
            const quickForm = document.getElementById('quick-form');
            const showFullButton = document.getElementById('show-full');
            const showQuickButton = document.getElementById('show-quick');

            function loadHistory() {
                const raw = window.localStorage.getItem(storageKey) || '[]';
                const stored = JSON.parse(raw);
                const tbody = document.querySelector('#history-table tbody');
                const empty = document.getElementById('history-empty');
                tbody.innerHTML = '';
                if (!stored.length) {
                    empty.style.display = 'block';
                    return;
                }
                empty.style.display = 'none';
                stored.slice().reverse().forEach(item => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${item.name || 'Guest'}</td>
                        <td>${item.age}</td>
                        <td>${item.risk_category}</td>
                        <td>${item.date}</td>
                    `;
                    tbody.appendChild(tr);
                });
            }

            function saveAssessment(data) {
                const raw = window.localStorage.getItem(storageKey) || '[]';
                const stored = JSON.parse(raw);
                stored.push(data);
                window.localStorage.setItem(storageKey, JSON.stringify(stored.slice(-10)));
                loadHistory();
            }

            function clearHistory() {
                window.localStorage.removeItem(storageKey);
                loadHistory();
            }

            function toggleForms(showQuick) {
                quickForm.style.display = showQuick ? 'block' : 'none';
                fullForm.style.display = showQuick ? 'none' : 'block';
            }

            function validateForm(form) {
                const age = Number(form.age.value);
                const bmi = Number(form.bmi.value);
                const glucose = Number(form.blood_glucose_fasting?.value || 0);
                const pressure = Number(form.blood_pressure_systolic?.value || 0);
                const sleep = Number(form.sleep_hours?.value || 7);
                const stress = Number(form.stress_level?.value || 5);
                let message = '';

                if (age < 18 || age > 120) message += 'Age must be between 18 and 120. ';
                if (bmi < 10 || bmi > 60) message += 'BMI should be between 10 and 60. ';
                if (glucose && (glucose < 60 || glucose > 300)) message += 'Glucose must be between 60 and 300. ';
                if (pressure && (pressure < 80 || pressure > 200)) message += 'Blood pressure should be between 80 and 200. ';
                if (sleep && (sleep < 3 || sleep > 12)) message += 'Sleep hours should be between 3 and 12. ';
                if (stress && (stress < 1 || stress > 10)) message += 'Stress level must be 1-10. ';

                if (message) {
                    warningBox.textContent = message;
                    warningBox.style.display = 'block';
                    return false;
                }

                warningBox.style.display = 'none';
                return true;
            }

            showFullButton.addEventListener('click', () => toggleForms(false));
            showQuickButton.addEventListener('click', () => toggleForms(true));

            document.addEventListener('DOMContentLoaded', () => {
                loadHistory();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
@app.post("/submit", response_class=HTMLResponse)
async def handle_form(
    request: Request,
    name: str = Form(""),
    age: int = Form(...),
    bmi: float = Form(...),
    family_history: str = Form(...),
    exercise_frequency: int = Form(...),
    diet_quality: str = Form(...),
    blood_pressure_systolic: int = Form(...),
    blood_glucose_fasting: float = Form(...),
    stress_level: int = Form(...),
    sleep_hours: float = Form(...),
    medications: str = Form(...)
):
    def html_escape(value):
        return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    try:
        family_history_bool = family_history == "yes"
        medications_bool = medications == "yes"
        
        profile = PatientProfile(
            age=age,
            bmi=bmi,
            family_history=family_history_bool,
            exercise_frequency=exercise_frequency,
            diet_quality=diet_quality,
            blood_pressure_systolic=blood_pressure_systolic,
            blood_glucose_fasting=blood_glucose_fasting,
            stress_level=stress_level,
            sleep_hours=sleep_hours,
            medications=medications_bool,
            name=name.strip()
        )
        
        calculator = DiabetesRiskCalculator()
        risk_score, factor_scores = calculator.calculate_overall_risk(profile)
        risk_category = calculator.get_risk_category(risk_score)
        recommendations = calculator.get_recommendations(profile, risk_score)
        risk_plot = calculator.generate_plot_base64(factor_scores)
        gauge_plot = calculator.generate_gauge_base64(risk_score, risk_category)
        top_factors = calculator.get_top_risk_factors(factor_scores)
        age_group = 'Young adult' if age < 30 else 'Adult' if age < 45 else 'Mature adult' if age < 60 else 'Senior'
        assessment_data = {
            'name': profile.name or 'Guest',
            'age': age,
            'risk_category': risk_category,
            'risk_score': f"{risk_score:.1%}",
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        assessment_json = json.dumps(assessment_data)
        
        risk_class = 'high' if 'HIGH' in risk_category else 'moderate' if 'MODERATE' in risk_category else 'low'
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Diabetes Risk Assessment Results</title>
            <meta name="description" content="Personalized diabetes risk assessment results with charts and expert-guided recommendations.">
            <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='45' fill='%23667eea'/%3E%3Cpath d='M50 20v60M35 50h30' stroke='%23fff' stroke-width='10' stroke-linecap='round'/%3E%3C/svg%3E">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #e8f3ff 0%, #cde7ff 100%);
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    color: #2f3b54;
                }}
                .page-shell {{
                    max-width: 1120px;
                    margin: 0 auto;
                    padding: 24px 18px 40px;
                }}
                .header-card, .summary-card, .chart-card, .tips-card {{
                    background: rgba(245,250,255,0.96);
                    border-radius: 24px;
                    box-shadow: 0 24px 50px rgba(45, 81, 127, 0.12);
                    padding: 28px;
                    margin-bottom: 24px;
                }}
                .header-card h1 {{
                    margin: 0 0 12px;
                    font-size: clamp(2rem, 2.8vw, 3rem);
                }}
                .header-card p {{
                    margin: 0;
                    color: #545768;
                    line-height: 1.75;
                }}
                .badge {{
                    display: inline-flex;
                    padding: 10px 18px;
                    border-radius: 999px;
                    font-weight: 700;
                    letter-spacing: 0.02em;
                    margin-top: 16px;
                }}
                .badge.high {{ background: #ffe5e5; color: #c92a2a; }}
                .badge.moderate {{ background: #fff4e5; color: #c15c0d; }}
                .badge.low {{ background: #e6f8ea; color: #1f7a3d; }}
                .hero-actions {{
                    margin-top: 22px;
                    display: flex;
                    flex-wrap: wrap;
                    gap: 12px;
                }}
                .hero-actions button, .hero-actions a {{
                    border: none;
                    border-radius: 999px;
                    padding: 12px 22px;
                    cursor: pointer;
                    font-weight: 700;
                    text-decoration: none;
                }}
                .hero-actions button {{ background: #667eea; color: white; }}
                .hero-actions a {{ background: #f4f5ff; color: #2f2f44; }}
                .grid {{
                    display: grid;
                    gap: 24px;
                    grid-template-columns: 1fr 1fr;
                }}
                .grid .inner-card {{ background: #f8faff; border-radius: 20px; padding: 22px; }}
                .chart-image {{ width: 100%; border-radius: 18px; display: block; }}
                .summary-list, .recommendation-list {{
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }}
                .summary-list li, .recommendation-list li {{
                    margin-bottom: 11px;
                    color: #4f506a;
                }}
                .summary-list li::before {{ content: '•'; color: #667eea; display: inline-block; width: 1em; margin-left: -1em; }}
                .tips-card h3 {{ margin-top: 0; }}
                .tips-card ul {{ padding-left: 20px; }}
                .tips-card li {{ margin-bottom: 12px; color: #4e4e62; }}
                .footer-note {{ color: #5f6173; margin-top: 18px; line-height: 1.75; }}
                @media (max-width: 900px) {{
                    .grid {{ grid-template-columns: 1fr; }}
                }}
            </style>
        </head>
        <body>
            <div class="page-shell">
                <section class="header-card">
                    <h1>Assessment complete</h1>
                    <p>Thank you, {html_escape(profile.name or 'Guest')} — your personalized diabetes risk report is ready. Save it, share it, or print it as a PDF.</p>
                    <div class="hero-actions">
                        <button type="button" onclick="window.print();">Download report</button>
                        <a href="/">Start new assessment</a>
                    </div>
                    <span class="badge {risk_class}">{risk_category}</span>
                </section>

                <section class="summary-card">
                    <div class="grid">
                        <div class="inner-card">
                            <strong>Profile</strong>
                            <p>Name: {html_escape(profile.name or 'Guest')}</p>
                            <p>Age: {age} ({age_group})</p>
                            <p>BMI: {bmi:.1f}</p>
                            <p>Exercise days/week: {exercise_frequency}</p>
                        </div>
                        <div class="inner-card">
                            <strong>Health snapshot</strong>
                            <p>Family history: {'Yes' if family_history_bool else 'No'}</p>
                            <p>Diet quality: {html_escape(diet_quality.title())}</p>
                            <p>Blood pressure: {blood_pressure_systolic} mmHg</p>
                            <p>Fasting glucose: {blood_glucose_fasting:.1f} mg/dL</p>
                        </div>
                        <div class="inner-card">
                            <strong>Guidance</strong>
                            <p>{'Speak with your doctor soon if your risk is high.' if 'HIGH' in risk_category else 'Continue healthy habits and review again in a few months.' if 'MODERATE' in risk_category else 'Great work — maintain your healthy lifestyle.'}</p>
                        </div>
                    </div>

                </section>

                <section class="chart-card">
                    <h2>Risk charts</h2>
                    <img class="chart-image" src="data:image/png;base64,{risk_plot}" alt="Risk factor chart">
                    <img class="chart-image" src="data:image/png;base64,{gauge_plot}" alt="Risk gauge" style="margin-top:22px;">
                </section>

                <section class="chart-card">
                    <div class="grid">
                        <div class="inner-card">
                            <strong>Top risk factors</strong>
                            <ul class="summary-list">
                                {''.join(f'<li>{html_escape(name)}: {value:.2f}</li>' for name, value in top_factors)}
                            </ul>
                        </div>
                        <div class="inner-card">
                            <strong>Recommendations</strong>
                            <ul class="recommendation-list">
                                {''.join(f'<li>{html_escape(rec)}</li>' for rec in recommendations)}
                            </ul>
                        </div>
                    </div>
                </section>

                <section class="tips-card">
                    <h3>Improve your diabetes risk</h3>
                    <ul>
                        <li>Eat more whole foods, vegetables, lean protein, and fiber.</li>
                        <li>Aim for 150 minutes of moderate activity each week.</li>
                        <li>Reduce stress with meditation, breathing, or walking.</li>
                        <li>Keep sleep consistent between 7 and 9 hours nightly.</li>
                    </ul>
                    <p class="footer-note">If you experience fatigue, thirst, blurred vision, or other symptoms, contact a healthcare provider promptly.</p>
                </section>
            </div>
            <script>
                const assessmentData = {assessment_json};
                const storageKey = 'ebhaanDiabetesAssessments';
                function loadHistory() {{
                    const raw = window.localStorage.getItem(storageKey) || '[]';
                    return JSON.parse(raw);
                }}
                function saveAssessment(data) {{
                    const stored = loadHistory();
                    stored.push(data);
                    window.localStorage.setItem(storageKey, JSON.stringify(stored.slice(-10)));
                }}
                saveAssessment(assessmentData);
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html)
    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
        </head>
        <body>
            <h1>An error occurred: {str(e)}</h1>
            <a href="/">Go back</a>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)


@app.post("/quick_submit", response_class=HTMLResponse)
async def quick_submit(
    request: Request,
    name: str = Form(""),
    age: int = Form(...),
    bmi: float = Form(...),
    family_history: str = Form(...),
    exercise_frequency: int = Form(...),
    diet_quality: str = Form(...)
):
    def html_escape(value):
        return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    try:
        family_history_bool = family_history == "yes"

        profile = PatientProfile(
            age=age,
            bmi=bmi,
            family_history=family_history_bool,
            exercise_frequency=exercise_frequency,
            diet_quality=diet_quality,
            blood_pressure_systolic=120,
            blood_glucose_fasting=95.0,
            stress_level=5,
            sleep_hours=7.0,
            medications=False,
            name=name.strip()
        )

        calculator = DiabetesRiskCalculator()
        risk_score, factor_scores = calculator.calculate_overall_risk(profile)
        risk_category = calculator.get_risk_category(risk_score)
        recommendations = calculator.get_recommendations(profile, risk_score)
        risk_plot = calculator.generate_plot_base64(factor_scores)
        gauge_plot = calculator.generate_gauge_base64(risk_score, risk_category)
        top_factors = calculator.get_top_risk_factors(factor_scores)
        age_group = 'Young adult' if age < 30 else 'Adult' if age < 45 else 'Mature adult' if age < 60 else 'Senior'
        assessment_data = {
            'name': profile.name or 'Guest',
            'age': age,
            'risk_category': risk_category,
            'risk_score': f"{risk_score:.1%}",
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        assessment_json = json.dumps(assessment_data)
        risk_class = 'high' if 'HIGH' in risk_category else 'moderate' if 'MODERATE' in risk_category else 'low'

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Quick Diabetes Risk Result</title>
            <meta name="description" content="Quick diabetes risk assessment result with default health assumptions.">
            <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='45' fill='%23667eea'/%3E%3Cpath d='M50 20v60M35 50h30' stroke='%23fff' stroke-width='10' stroke-linecap='round'/%3E%3C/svg%3E">
            <style>
                body {{ margin:0; padding:0; background: linear-gradient(135deg, #e8f3ff 0%, #cde7ff 100%); font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color:#2f3b54; }}
                .page-shell {{ max-width: 1100px; margin:0 auto; padding:28px 18px 36px; }}
                .card {{ background: rgba(245,250,255,0.96); border-radius: 24px; padding: 28px; box-shadow: 0 24px 50px rgba(45, 81, 127, 0.12); margin-bottom:24px; }}
                .card h1 {{ margin-top: 0; font-size: clamp(2rem, 2.8vw, 3rem); }}
                .card p {{ margin:0; color:#475467; line-height:1.75; }}
                .badge {{ display:inline-flex; padding:10px 18px; border-radius:999px; font-weight:700; margin-top:16px; }}
                .badge.high {{ background:#fff0f2; color:#bf3f49; }}
                .badge.moderate {{ background:#fffbeb; color:#974a10; }}
                .badge.low {{ background:#e6f8ea; color:#1f7a3d; }}
                .hero-actions {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:18px; }}
                .hero-actions button, .hero-actions a {{ padding: 12px 20px; border-radius:999px; font-weight:700; text-decoration:none; border:none; cursor:pointer; }}
                .hero-actions button {{ background:#5a83ee; color:white; }}
                .hero-actions a {{ background:#eff5ff; color:#2f3b54; }}
                .grid {{ display:grid; gap:22px; grid-template-columns:1fr 1fr; margin-top:24px; }}
                .summary-list, .recommendation-list {{ list-style:none; padding:0; margin:0; }}
                .summary-list li, .recommendation-list li {{ margin-bottom:10px; color:#4e4e62; }}
                @media(max-width:900px){{ .grid{{grid-template-columns:1fr;}} }}
            </style>
        </head>
        <body>
            <div class="page-shell">
                <section class="card">
                    <h1>Quick assessment result</h1>
                    <p>Quick mode used standard defaults for blood pressure, glucose, sleep, and stress when values were omitted.</p>
                    <div class="hero-actions">
                        <button type="button" onclick="window.print();">Download report</button>
                        <a href="/">Start new assessment</a>
                    </div>
                    <span class="badge {risk_class}">{risk_category}</span>
                </section>
                <section class="card">
                    <div class="grid">
                        <div>
                            <strong>Name:</strong> {html_escape(profile.name or 'Guest')}<br>
                            <strong>Age:</strong> {age} ({age_group})<br>
                            <strong>BMI:</strong> {bmi:.1f}
                        </div>
                        <div>
                            <strong>Family history:</strong> {'Yes' if family_history_bool else 'No'}<br>
                            <strong>Exercise:</strong> {exercise_frequency} days/week<br>
                            <strong>Diet quality:</strong> {html_escape(diet_quality.title())}
                        </div>
                    </div>
                </section>
                <section class="card">
                    <img src="data:image/png;base64,{risk_plot}" alt="Risk factor chart" style="width:100%; border-radius:18px;">
                    <img src="data:image/png;base64,{gauge_plot}" alt="Risk gauge" style="width:100%; border-radius:18px; margin-top:24px;">
                </section>
                <section class="card">
                    <div class="grid">
                        <div>
                            <strong>Top risk factors</strong>
                            <ul class="summary-list">
                                {''.join(f'<li>{html_escape(name)}: {value:.2f}</li>' for name, value in top_factors)}
                            </ul>
                        </div>
                        <div>
                            <strong>Recommendations</strong>
                            <ul class="recommendation-list">
                                {''.join(f'<li>{html_escape(rec)}</li>' for rec in recommendations)}
                            </ul>
                        </div>
                    </div>
                </section>
                <section class="card">
                    <h3>Remember</h3>
                    <p>If you experience symptoms such as fatigue, thirst, blurred vision, or frequent urination, please consult a healthcare professional.</p>
                </section>
            </div>
            <script>
                const assessmentData = {assessment_json};
                const storageKey = 'ebhaanDiabetesAssessments';
                function loadHistory() {{
                    const raw = window.localStorage.getItem(storageKey) || '[]';
                    return JSON.parse(raw);
                }}
                function saveAssessment(data) {{
                    const stored = loadHistory();
                    stored.push(data);
                    window.localStorage.setItem(storageKey, JSON.stringify(stored.slice(-10)));
                }}
                saveAssessment(assessmentData);
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html)
    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
        </head>
        <body>
            <h1>An error occurred: {html_escape(str(e))}</h1>
            <a href=\"/\">Go back</a>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)
