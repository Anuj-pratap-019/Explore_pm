from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import os
import traceback

app = Flask(__name__)

# Load the expense model
expense_model_path = 'expense_predictor_rf.pkl'
if not os.path.exists(expense_model_path):
    expense_model_path = os.path.join(os.path.dirname(__file__), 'models', 'expense_predictor_rf.pkl')

try:
    expense_model = joblib.load(expense_model_path)
except Exception as e:
    print(f"Error loading expense model: {e}")
    expense_model = None

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
    income = user_data["Net monthly income"]
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
        f"🔷 Fixed Portion (60%): ₹{round(fixed_expense):,}, 🔶 Variable Portion (40%): ₹{round(variable_expense):,}",
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
def recommend_investment_strategy(user_data):
    income = float(user_data["Gross monthly income"])
    savings = float(user_data["Savings"])
    debt = float(user_data["Debt"])
    emergency_fund = float(user_data["Emergency Fund"])
    expenses = float(user_data["Total Expenses"])
    occupation = user_data.get("Occupation", "").strip().lower()

    advice = []

    # Check emergency fund first - standard financial rule (aim for 3-6 months of expenses)
    emergency_target = expenses * 3
    if emergency_fund < emergency_target:
        recommendation = "Savings Account / Liquid Fund"
        advice.append(f"🚨 Critical Priority: Build your emergency fund first. It is below the 3-month threshold of ₹{emergency_target:,.0f}.")
        advice.append("💡 Avoid locking up your money in long-term plans (like PPF) until your liquid emergency reserves are secure.")
        advice.append("📈 Keep your savings in a high-yield savings account or a liquid mutual fund for instant access.")
    # Recommendation based on high savings and high income with low debt (Wealth building / Tax saving)
    elif savings > 200000 and income > 80000 and debt < 50000:
        recommendation = "ELSS (Equity Linked Savings Scheme)"
        advice.append("✅ Recommendation: ELSS (Tax-saving mutual funds). Suitable for high-income earners with low debt who can digest equity market volatility.")
        advice.append("💡 ELSS qualifies for Section 80C tax deductions and has the shortest lock-in (3 years) among all tax-saving options.")
    # Moderate savings and low debt (Wealth building)
    elif savings > 100000 and debt < 50000:
        recommendation = "SIP (Systematic Investment Plan)"
        advice.append("✅ Recommendation: Systematic Investment Plan (SIP) in equity/hybrid mutual funds.")
        advice.append("💡 Consistent investing via SIPs helps in compounding wealth over the long term and averages out market fluctuations.")
    # Lower income or specific occupations (Capital Preservation)
    elif income < 40000 or occupation in ["student", "retired", "senior citizen"]:
        recommendation = "Fixed Deposit (FD) / Debt Funds"
        advice.append("✅ Recommendation: Fixed Deposits (FD) or conservative Debt Mutual Funds.")
        advice.append("💡 Focus on capital preservation and safety. Perfect for lower-income brackets, students, or retired individuals needing steady/low-risk returns.")
    # Fallback or mixed profile (Diversified Portfolio)
    else:
        recommendation = "Mixed Strategy (SIP + FD)"
        advice.append("✅ Recommendation: A balanced portfolio split across equity SIPs and Fixed Income (FD/PPF).")
        advice.append("💡 This provides a healthy mix of growth (equity) and stability (debt) to manage financial risk.")

    # General advice rules
    if debt > income * 2:
        advice.append("⚠️ Debt Warning: Your total outstanding debt is quite high compared to your monthly income. Prioritize prepaying high-interest debt over aggressive investing.")
    if savings > income * 6:
        advice.append("ℹ️ Idle Cash: You have substantial cash in savings. Consider allocating some of it into investments to beat inflation.")

    return recommendation, advice

# --- Insurance Gap + Health Risk Advice Logic ---
def predict_insurance_gap_with_health(user_data):
    age = float(user_data["Age"])
    income = float(user_data["Gross monthly income"])
    insurance = float(user_data.get("Insurance", 0))
    occupation = user_data.get("Occupation", "").lower()
    lifestyle = int(user_data.get("Lifestyle Score", 5))
    family_history = user_data.get("Family History", "No").lower()

    # Calculate Human Life Value (HLV)
    years_remaining = max(0, 60 - age)
    hlv = income * 12 * years_remaining * 0.5

    # Deterministic Insurance Gap label logic
    if insurance < 0.7 * hlv:
        gap_label = "Underinsured"
    elif insurance > 1.2 * hlv:
        gap_label = "Overinsured"
    else:
        gap_label = "Adequately Insured"

    # Health risk scoring
    risk_score = 0
    if age > 50: risk_score += 2
    if lifestyle <= 5: risk_score += 2
    if "yes" in family_history: risk_score += 3
    if any(word in occupation for word in ["desk", "office", "it", "developer", "software"]):
        risk_score += 1

    if risk_score <= 2:
        health_risk = "Low"
    elif risk_score <= 5:
        health_risk = "Medium"
    else:
        health_risk = "High"

    advice = [f"📊 Your estimated Human Life Value (HLV) is ₹{hlv:,.0f}."]
    if gap_label == "Underinsured":
        gap_amount = hlv - insurance
        advice.append(f"🚨 You are Underinsured. Your current cover is ₹{insurance:,.0f}. You need an additional cover of at least ₹{gap_amount:,.0f} to protect your family's future.")
    elif gap_label == "Overinsured":
        advice.append(f"🟡 You are Overinsured (Current cover: ₹{insurance:,.0f} vs HLV: ₹{hlv:,.0f}). You may be paying higher premiums than necessary.")
    else:
        advice.append(f"✅ Your insurance coverage of ₹{insurance:,.0f} is adequate based on your income and age.")

    if health_risk == "High":
        advice.append("🚨 High Health Risk: Consider critical illness rider and comprehensive health insurance immediately.")
    elif health_risk == "Medium":
        advice.append("🟡 Moderate Health Risk: A family floater plan with wellness/OPD benefits is recommended.")
    else:
        advice.append("✅ Low Health Risk: Maintain your healthy lifestyle and consider a basic term health plan.")

    return gap_label, advice

# --- Financial Projection Logic ---
def generate_janam_patri(user_data, years=[1, 3, 10]):
    income_growth = 0.08
    expense_growth = 0.06
    investment_return = 0.10
    savings_interest_rate = 0.04
    emergency_buffer = 3

    age = float(user_data["Age"])
    income = float(user_data["Net monthly income"])
    expenses = float(user_data["Total Expenses"])
    savings = float(user_data["Savings"])
    investments = float(user_data["Investments"])
    emergency_fund = float(user_data["Emergency Fund"])

    data = []
    for year in range(1, max(years) + 1):
        income *= (1 + income_growth)
        expenses *= (1 + expense_growth)
        
        # Multiply monthly savings by 12 to get annual accumulation
        yearly_savings = (income - expenses) * 12

        event = ""
        if yearly_savings < 0:
            event = "⚠️ Fund Shortage"
            yearly_savings = 0

        # Reallocate 50% of yearly savings to investments, and 50% to cash savings
        savings_addition = yearly_savings * 0.5
        investment_addition = yearly_savings * 0.5

        savings = (savings * (1 + savings_interest_rate)) + savings_addition
        investments = (investments * (1 + investment_return)) + investment_addition
        net_worth = savings + investments + emergency_fund

        if emergency_fund < (expenses * emergency_buffer):
            event += " | ❗ Emergency Fund Risk"

        if year in years:
            data.append({
                "Year": f"{year} year(s)",
                "Projected Annual Income (₹)": round(income * 12),
                "Projected Annual Expenses (₹)": round(expenses * 12),
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
        # Convert numeric fields
        for k in feature_names:
            user_data[k] = float(user_data[k]) if user_data[k] != '' else 0.0
        predicted_expense, advice = analyze_expense_profile(user_data)
        return jsonify({'prediction': [predicted_expense], 'advice': advice})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 400

@app.route('/predict/investment', methods=['POST'])
def predict_investment():
    data = request.get_json()
    feature_names = ["Gross monthly income", "Net monthly income", "Savings", "Investments", "Debt", "Emergency Fund", "Total Expenses"]
    try:
        values = data['features'][0]
        user_data = dict(zip(feature_names, values))
        for k in feature_names:
            user_data[k] = float(user_data[k]) if user_data[k] != '' else 0.0
        prediction, advice = recommend_investment_strategy(user_data)
        return jsonify({'prediction': [prediction], 'advice': advice})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 400

@app.route('/predict/insurance', methods=['POST'])
def predict_insurance():
    data = request.get_json()
    feature_names = [
        "Age", "Gross monthly income", "Net monthly income", "Savings", "Debt", "Emergency Fund", "Investments",
        "Insurance", "Occupation", "Lifestyle Score", "Family History"
    ]
    try:
        values = data['features'][0]
        user_data = dict(zip(feature_names, values))
        for k in ["Age", "Gross monthly income", "Net monthly income", "Savings", "Debt", "Emergency Fund", "Investments", "Insurance"]:
            user_data[k] = float(user_data[k]) if user_data[k] != '' else 0.0
        user_data["Lifestyle Score"] = int(user_data["Lifestyle Score"]) if user_data["Lifestyle Score"] != '' else 5
        user_data["Occupation"] = user_data.get("Occupation") or ""
        user_data["Family History"] = user_data.get("Family History") or "No"

        gap_label, advice = predict_insurance_gap_with_health(user_data)
        return jsonify({'prediction': [gap_label], 'advice': advice})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 400

@app.route('/predict/projection', methods=['POST'])
def predict_projection():
    data = request.get_json()
    feature_names = ["Age", "Net monthly income", "Total Expenses", "Savings", "Investments", "Emergency Fund"]
    try:
        values = data['features'][0]
        user_data = dict(zip(feature_names, values))
        for k in feature_names:
            user_data[k] = float(user_data[k]) if user_data[k] != '' else 0.0
        df = generate_janam_patri(user_data)
        data_table = df.to_dict(orient='records')
        return jsonify({'table': data_table})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
