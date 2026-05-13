import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Tuple
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import jinja2


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
    
    def __init__(self):
        self.assessment_history = []
    
    def validate_input(self, value, input_type, min_val=None, max_val=None):
        """Validate user input with range checking"""
        try:
            if input_type == "int":
                val = int(value)
            else:
                val = float(value)
            
            if min_val is not None and val < min_val:
                raise ValueError(f"Value must be at least {min_val}")
            if max_val is not None and val > max_val:
                raise ValueError(f"Value must not exceed {max_val}")
            return val
        except ValueError as e:
            raise ValueError(f"Invalid input: {e}")
    
    def get_patient_data(self) -> PatientProfile:
        """Collect comprehensive patient health data"""
        print("\n" + "="*50)
        print("COMPREHENSIVE DIABETES RISK ASSESSMENT")
        print("="*50 + "\n")
        
        while True:
            try:
                age = self.validate_input(
                    input("Enter your age (18-120): "), "int", 18, 120
                )
                break
            except ValueError as e:
                print(f"Error: {e}. Please try again.")
        
        while True:
            try:
                bmi = self.validate_input(
                    input("Enter your BMI (10-60): "), "float", 10, 60
                )
                break
            except ValueError as e:
                print(f"Error: {e}. Please try again.")
        
        family_history = input("Family history of diabetes? (yes/no): ").lower() == "yes"
        
        while True:
            try:
                exercise = self.validate_input(
                    input("Exercise days per week (0-7): "), "int", 0, 7
                )
                break
            except ValueError as e:
                print(f"Error: {e}. Please try again.")
        
        diet_quality = input("Diet quality (poor/fair/good): ").lower()
        while diet_quality not in ["poor", "fair", "good"]:
            diet_quality = input("Please enter 'poor', 'fair', or 'good': ").lower()
        
        while True:
            try:
                bp_systolic = self.validate_input(
                    input("Blood pressure systolic (80-200): "), "int", 80, 200
                )
                break
            except ValueError as e:
                print(f"Error: {e}. Please try again.")
        
        while True:
            try:
                glucose = self.validate_input(
                    input("Fasting blood glucose mg/dL (60-300): "), "float", 60, 300
                )
                break
            except ValueError as e:
                print(f"Error: {e}. Please try again.")
        
        while True:
            try:
                stress = self.validate_input(
                    input("Stress level (1-10): "), "int", 1, 10
                )
                break
            except ValueError as e:
                print(f"Error: {e}. Please try again.")
        
        while True:
            try:
                sleep = self.validate_input(
                    input("Average sleep hours per night (3-12): "), "float", 3, 12
                )
                break
            except ValueError as e:
                print(f"Error: {e}. Please try again.")
        
        medications = input("Currently on medications for hypertension/cholesterol? (yes/no): ").lower() == "yes"
        
        return PatientProfile(
            age=age,
            bmi=bmi,
            family_history=family_history,
            exercise_frequency=exercise,
            diet_quality=diet_quality,
            blood_pressure_systolic=bp_systolic,
            blood_glucose_fasting=glucose,
            stress_level=stress,
            sleep_hours=sleep,
            medications=medications
        )
    
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
        
        weighted_score = sum(scores[factor] * self.WEIGHTS[factor.lower().replace(" ", "_")] for factor in scores)
        
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
    
    def visualize_results(self, factor_scores: Dict, risk_category: str):
        """Create comprehensive visualizations"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # Bar chart of risk factors
        factors = list(factor_scores.keys())
        scores = list(factor_scores.values())
        colors = ['red' if s > 0.7 else 'orange' if s > 0.4 else 'green' for s in scores]
        
        ax1.bar(factors, scores, color=colors, alpha=0.7)
        ax1.set_title("Risk Factor Scores", fontsize=12, fontweight='bold')
        ax1.set_ylabel("Risk Score (0-1)")
        ax1.set_ylim(0, 1)
        ax1.axhline(y=0.7, color='red', linestyle='--', alpha=0.5, label='High Risk')
        ax1.axhline(y=0.4, color='orange', linestyle='--', alpha=0.5, label='Moderate Risk')
        ax1.legend()
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Overall risk gauge
        risk_values = {'Low': 0.2, 'Moderate': 0.5, 'High': 0.8}
        risk_type = risk_category.split()[0]
        ax2.barh(['Risk Level'], [risk_values.get(risk_type, 0.5)], color={
            'Low': 'green', 'Moderate': 'orange', 'High': 'red'
        }.get(risk_type, 'gray'))
        ax2.set_xlim(0, 1)
        ax2.set_title(f"Overall Assessment: {risk_category}", fontsize=12, fontweight='bold')
        ax2.set_xlabel("Risk Level")
        
        # Pie chart of weighted contributions
        weighted_contributions = {k: v * self.WEIGHTS.get(k.lower().replace(" ", "_"), 0.05) for k, v in factor_scores.items()}
        ax3.pie(weighted_contributions.values(), labels=weighted_contributions.keys(), autopct='%1.1f%%')
        ax3.set_title("Weighted Risk Distribution", fontsize=12, fontweight='bold')
        
        # Summary text
        ax4.axis('off')
        summary_text = f"""
ASSESSMENT SUMMARY
━━━━━━━━━━━━━━━━━━━━━━
Risk Category: {risk_category}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Top Risk Factors:
"""
        sorted_factors = sorted(factor_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        for factor, score in sorted_factors:
            summary_text += f"\n  • {factor}: {score:.2f}"
        
        ax4.text(0.1, 0.5, summary_text, fontsize=10, family='monospace', verticalalignment='center')
        
        plt.tight_layout()
        plt.show()
    
    def run_assessment(self):
        """Run complete assessment"""
        profile = self.get_patient_data()
        risk_score, factor_scores = self.calculate_overall_risk(profile)
        risk_category = self.get_risk_category(risk_score)
        recommendations = self.get_recommendations(profile, risk_score)
        
        # Store assessment
        self.assessment_history.append({
            "timestamp": datetime.now(),
            "risk_score": risk_score,
            "category": risk_category,
            "profile": profile
        })
        
        # Display results
        print("\n" + "="*50)
        print("ASSESSMENT RESULTS")
        print("="*50)
        print(f"\nOverall Risk Score: {risk_score:.2%}")
        print(f"Risk Category: {risk_category}\n")
        
        print("Individual Factor Scores:")
        for factor, score in sorted(factor_scores.items(), key=lambda x: x[1], reverse=True):
            print(f"  {factor:.<30} {score:.2%}")
        
        print("\nPersonalized Recommendations:")
        for rec in recommendations:
            print(rec)
        
        self.visualize_results(factor_scores, risk_category)


def main():
    """Main application loop"""
    calculator = DiabetesRiskCalculator()
    
    while True:
        try:
            calculator.run_assessment()
            again = input("\n\nRun another assessment? (yes/no): ").lower()
            if again != "yes":
                print("\nThank you for using the Diabetes Risk Calculator. Stay healthy!")
                break
        except KeyboardInterrupt:
            print("\n\nAssessment cancelled.")
            break
        except Exception as e:
            print(f"An error occurred: {e}. Please try again.")

if __name__ == "__main__":
    main()
app = FastAPI()
env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")), cache_size=0)
env.cache = {}
templates = Jinja2Templates(env=env) 
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.post("/submit", response_class=HTMLResponse)
async def handle_form(
    request: Request,
    age: int = Form(...),
    bmi: float = Form(...),
    family_history: str = Form(None),
    exercise_frequency: int = Form(...),
    diet_quality: str = Form(...),
    blood_pressure_systolic: int = Form(...),
    blood_glucose_fasting: float = Form(...),
    stress_level: int = Form(...),
    sleep_hours: float = Form(...),
    medications: str = Form(None)
):
    family_history_bool = family_history == "on"
    medications_bool = medications == "on"
    
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
        medications=medications_bool
    )
    
    calculator = DiabetesRiskCalculator()
    risk_score, _ = calculator.calculate_overall_risk(profile)
    risk_category = calculator.get_risk_category(risk_score)
    recommendations = calculator.get_recommendations(profile, risk_score)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": {
            "risk_score": f"{risk_score:.1%}",
            "category": risk_category,
            "recommendations": recommendations
        }
    })



