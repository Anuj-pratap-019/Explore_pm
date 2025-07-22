from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import os
import traceback

app = Flask(__name__)

# Load the models
try:
    expense_model = joblib.load('expense_predictor_rf.pkl')
    insurance_model = joblib.load('insurance_gap_model.pkl')
    investment_model = joblib.load('investment_model.pkl')
    insurance_label_encoder = joblib.load('models/insurance_gap_label_encoder.pkl') if os.path.exists('models/insurance_gap_label_encoder.pkl') else None
except FileNotFoundError as e:
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    try:
        expense_model = joblib.load(os.path.join(models_dir, 'expense_predictor_rf.pkl'))
        insurance_model = joblib.load(os.path.join(models_dir, 'insurance_gap_model.pkl'))
        investment_model = joblib.load(os.path.join(models_dir, 'investment_model.pkl'))
        insurance_label_encoder = joblib.load(os.path.join(models_dir, 'insurance_gap_label_encoder.pkl')) if os.path.exists(os.path.join(models_dir, 'insurance_gap_label_encoder.pkl')) else None
    except FileNotFoundError:
        print(f"Error loading models: {e}")
        expense_model, insurance_model, investment_model = None, None, None
        insurance_label_encoder = None

@app.route('/')
def home():
    return render_template('index.html')

# --- Expense Advice Logic ---
def analyze_expense_profile(user_data):
    input_features = [
        "Gross monthly income", "Net monthly income", "Savings",
        "Investments", "Debt", "Emergency Fund"
    ]
    df = pd.DataFrame([user_data])
    X = df[input_features]
    predicted_expense = expense_model.predict(X)[0]
    income = user_data["Gross monthly income"]
    if predicted_expense > income:
        logical_expense = income
        overspending = True
    else:
        logical_expense = predicted_expense
        overspending = False
    fixed_expense = 0.6 * logical_expense
    variable_expense = 0.4 * logical_expense
    future_emi = user_data.get("Debt", 0) / 12
    future_medical = 1000 if user_data.get("Age", 0) > 50 else 0
    future_tuition = 2000 if user_data.get("Age", 100) < 25 else 0
    total_future_liabilities = future_emi + future_medical + future_tuition
    spending_ratio = logical_expense / income if income > 0 else 0
    if spending_ratio > 0.8:
        spending_flag = "⚠️ Overexposed — spending more than 80% of income"
    elif spending_ratio < 0.3:
        spending_flag = "✅ Very conservative spending"
    else:
        spending_flag = "🟡 Moderate spending level"
    advice = [
        f"📊 Predicted Monthly Expense: ₹{round(predicted_expense):,}",
        f"🔷 Fixed Portion: ₹{round(fixed_expense):,}, 🔶 Variable Portion: ₹{round(variable_expense):,}",
        f"💸 Expected Future Liabilities: ₹{round(total_future_liabilities):,} (EMI + Medical + Tuition)",
        f"📉 Spending to Income Ratio: {spending_ratio:.2f}",
        f"📝 Spending Risk Flag: {spending_flag}"
    ]
    if overspending:
        advice.append("🚨 Your predicted expenses exceed your income!")
        advice.append(f"💡 We've capped expenses to ₹{round(logical_expense):,} for realistic analysis.")
        advice.append("📉 Consider reducing variable expenses or increasing income.")
    return round(predicted_expense), advice

# --- Investment Advice Logic ---
def recommend_investment_strategy(user_data, prediction):
    income = user_data["Gross monthly income"]
    savings = user_data["Savings"]
    debt = user_data["Debt"]
    emergency_fund = user_data["Emergency Fund"]
    expenses = user_data["Total Expenses"]
    advice = []
    if emergency_fund < expenses * 3:
        advice.append(f"Your emergency fund is below the 3-month threshold. Aim for ₹{expenses*3:,.0f}.")
    if savings < 100000:
        advice.append("Your savings are on the lower side. Consider increasing them before aggressive investing.")
    if prediction == "ELSS":
        advice.append("ELSS is suitable for high-income individuals comfortable with long lock-in and equity risk.")
    elif prediction == "SIP":
        advice.append("SIP is a smart choice for steady long-term wealth building with moderate risk.")
    elif prediction == "FD":
        advice.append("FD is a safe option if you're risk-averse or need fixed returns.")
    elif prediction == "PPF":
        advice.append("PPF is good when emergency funds are low and you need tax-saving, long-term safety.")
    elif prediction == "Mixed":
        advice.append("A mixed strategy is ideal when no single option dominates — diversify across SIP, FD, and ELSS.")
    return advice

# --- Insurance Gap + Health Risk Advice Logic ---
def predict_insurance_gap_with_health(user_data, pred_encoded):
    age = user_data["Age"]
    income = user_data["Gross monthly income"]
    insurance = user_data.get("Insurance", 0)
    occupation = user_data.get("Occupation", "").lower()
    lifestyle = user_data.get("Lifestyle Score", 5)
    family_history = user_data.get("Family History", "No").lower()
    years_remaining = max(0, 60 - age)
    hlv = income * 12 * years_remaining * 0.5
    if insurance_label_encoder:
        gap_label = insurance_label_encoder.inverse_transform([pred_encoded])[0]
    else:
        gap_label = str(pred_encoded)
    # Health risk scoring
    risk_score = 0
    if age > 50: risk_score += 2
    if lifestyle <= 5: risk_score += 2
    if "yes" in family_history: risk_score += 3
    if any(word in occupation for word in ["desk", "office", "it", "developer"]):
        risk_score += 1
    if risk_score <= 2:
        health_risk = "Low"
    elif risk_score <= 5:
        health_risk = "Medium"
    else:
        health_risk = "High"
    advice = [f"Your estimated Human Life Value (HLV) is ₹{hlv:,.0f}."]
    if gap_label == "Underinsured":
        advice.append(f"You're underinsured. You may need ₹{hlv - insurance:,.0f} more coverage.")
    elif gap_label == "Overinsured":
        advice.append("You may be paying more than needed for life cover.")
    else:
        advice.append("Your insurance appears adequate based on income and age.")
    if health_risk == "High":
        advice.append("You are at high health risk. Consider critical illness and health insurance urgently.")
    elif health_risk == "Medium":
        advice.append("You are at moderate health risk. A health plan with OPD coverage may be beneficial.")
    else:
        advice.append("Your health risk is low. Maintain a good lifestyle and consider wellness-based plans.")
    return gap_label, advice

# --- Financial Projection Logic ---
def generate_janam_patri(user_data, years=[1, 3, 10]):
    income_growth = 0.08
    expense_growth = 0.06
    investment_return = 0.10
    emergency_buffer = 3

    age = user_data["Age"]
    income = user_data["Gross monthly income"]
    expenses = user_data["Total Expenses"]
    savings = user_data["Savings"]
    investments = user_data["Investments"]
    emergency_fund = user_data["Emergency Fund"]

    data = []
    for year in range(1, max(years) + 1):
        income *= (1 + income_growth)
        expenses *= (1 + expense_growth)
        yearly_savings = income - expenses

        event = ""
        if yearly_savings < 0:
            event = "⚠️ Fund Shortage"
            yearly_savings = 0

        savings += yearly_savings
        investments *= (1 + investment_return)
        net_worth = savings + investments + emergency_fund

        if emergency_fund < (expenses * emergency_buffer):
            event += " | ❗ Emergency Fund Risk"

        if year in years:
            data.append({
                "Year": f"{year} year(s)",
                "Projected Income (₹)": round(income),
                "Projected Expenses (₹)": round(expenses),
                "Savings (₹)": round(savings),
                "Investments (₹)": round(investments),
                "Net Worth (₹)": round(net_worth),
                "Event/Advice": event or "✅ Stable"
            })

    return pd.DataFrame(data)

@app.route('/predict/expense', methods=['POST'])
def predict_expense():
    if not expense_model:
        return jsonify({"error": "Expense model is not loaded"}), 500
    data = request.get_json()
    feature_names = ["Gross monthly income", "Net monthly income", "Savings", "Investments", "Debt", "Emergency Fund"]
    try:
        values = data['features'][0]
        user_data = dict(zip(feature_names, values))
        predicted_expense, advice = analyze_expense_profile(user_data)
        return jsonify({'prediction': [predicted_expense], 'advice': advice})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 400

@app.route('/predict/investment', methods=['POST'])
def predict_investment():
    if not investment_model:
        return jsonify({"error": "Investment model is not loaded"}), 500
    data = request.get_json()
    feature_names = ["Gross monthly income", "Net monthly income", "Savings", "Investments", "Debt", "Emergency Fund", "Total Expenses"]
    try:
        values = data['features'][0]
        user_data = dict(zip(feature_names, values))
        df = pd.DataFrame([user_data])
        prediction = investment_model.predict(df)[0]
        advice = recommend_investment_strategy(user_data, prediction)
        return jsonify({'prediction': [prediction], 'advice': advice})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 400

@app.route('/predict/insurance', methods=['POST'])
def predict_insurance():
    if not insurance_model:
        return jsonify({"error": "Insurance model is not loaded"}), 500
    data = request.get_json()
    feature_names = [
        "Age", "Gross monthly income", "Net monthly income", "Savings", "Debt", "Emergency Fund", "Investments",
        "Insurance", "Occupation", "Lifestyle Score", "Family History"
    ]
    try:
        values = data['features'][0]
        user_data = dict(zip(feature_names, values))
        # Convert types for numeric fields
        for k in ["Age", "Gross monthly income", "Net monthly income", "Savings", "Debt", "Emergency Fund", "Investments", "Insurance"]:
            user_data[k] = float(user_data[k]) if user_data[k] != '' else 0
        if "Lifestyle Score" in user_data:
            user_data["Lifestyle Score"] = int(user_data["Lifestyle Score"]) if user_data["Lifestyle Score"] != '' else 5
        else:
            user_data["Lifestyle Score"] = 5
        # For model prediction, only use the original 7 features
        model_features = [
            "Age", "Gross monthly income", "Net monthly income", "Savings", "Debt", "Emergency Fund", "Investments"
        ]
        df = pd.DataFrame([{k: user_data[k] for k in model_features}])
        pred_encoded = insurance_model.predict(df)[0]
        gap_label, advice = predict_insurance_gap_with_health(user_data, pred_encoded)
        return jsonify({'prediction': [gap_label], 'advice': advice})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 400

@app.route('/predict/projection', methods=['POST'])
def predict_projection():
    data = request.get_json()
    feature_names = ["Age", "Gross monthly income", "Total Expenses", "Savings", "Investments", "Emergency Fund"]
    try:
        values = data['features'][0]
        user_data = dict(zip(feature_names, values))
        # Convert all to float
        for k in feature_names:
            user_data[k] = float(user_data[k]) if user_data[k] != '' else 0
        df = generate_janam_patri(user_data)
        data_table = df.to_dict(orient='records')
        return jsonify({'table': data_table})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
