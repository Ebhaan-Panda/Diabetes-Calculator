



### **Diabetes Risk Predictor**
**Overview**
This project focuses on building a machine learning model to predict an individual’s risk of developing diabetes based on key health indicators. By analyzing patterns in medical data, the model identifies which factors contribute most significantly to diabetes risk.

**Motivation**
Diabetes is a widespread and growing health issue, affecting millions of people worldwide. With a personal family history of diabetes, I was motivated to better understand the condition and explore how data and technology can be used to support early detection and prevention.

**Features**
Predicts diabetes risk using supervised machine learning
Identifies and ranks the most influential health factors
Provides data visualizations for better interpretation of results
Evaluates model performance using standard metrics (accuracy, precision, recall)

**Dataset**
The dataset used in this project includes medical and demographic information such as:

- Glucose levels
- Blood pressure
- BMI
- Age
- Insulin levels

(Source: Publicly available healthcare dataset)

**Technologies Used**

- Python
- pandas
- numpy
- scikit-learn
- matplotlib / seaborn
- Methodology
- Data cleaning and preprocessing
- Exploratory data analysis (EDA)
- Feature selection and engineering
- Model training (e.g., logistic regression, decision trees)
- Model evaluation and optimization

**Results**

The model was able to identify key predictors of diabetes risk, with glucose levels, BMI, and age emerging as some of the most significant factors. Performance was evaluated using accuracy and other classification metrics.
(Add your actual accuracy here once you have it — don’t leave this vague long-term.)

**How to Run**

1. Clone the repository
- Install required dependencies:
- pip install -r requirements.txt
2.  Run the main script or notebook to train and test the model
## Run locally

```bash
cd "/Users/dcpanda/Desktop/Ebhaan Project"
python -m uvicorn DiabetesRiskCalc:app --host 127.0.0.1 --port 8001
```

Then open:

- `http://127.0.0.1:8001/`

**Future Improvements**

Incorporate larger and more diverse datasets
Experiment with advanced models (e.g., random forests, neural networks)
Deploy as a web application for real-time predictions
Improve model accuracy and generalization

**Author**

_Ebhaan Panda
High school student interested in computer science and biomedical engineering_
```
