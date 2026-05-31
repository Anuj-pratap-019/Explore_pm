# Explore PM: AI-Backed Portfolio Manager & Insurance Advisor

Explore PM is a premium, web-based personal wealth management and predictive advisory dashboard. By combining a Machine Learning regressor (Random Forest) for expense modeling with deterministic financial rule engines, the application delivers real-time diagnostics, budget planning, term-insurance gap checks, smart investment advice, and 10-year compounding wealth projections.

Designed with a high-fidelity, responsive dark glassmorphism user interface.

---

## 🚀 Key Features

* **Overview Dashboard (KPIs):** Real-time calculation of key financial health metrics:
  * **Savings Rate (%):** Color-coded savings health diagnostics.
  * **Debt-to-Income (DTI) Ratio:** Leverage and risk checking.
  * **Emergency Runway (Months):** Cash buffer liquidity tracking.
  * **Total Net Worth:** Immediate net worth calculator.
* **Expense Predictor (ML-Driven):** Uses a **Random Forest Regressor** trained on household demographics and asset features to predict expected baseline monthly expenses.
* **Smart Investment Advisory:** Suggests targeted asset allocation recommendations (ELSS tax-saving, equity mutual fund SIPs, fixed deposits/debt preservation, or liquid cash reserves) based on liquidity, income, and debt.
* **Insurance & Health Gap Analyzer:** Computes the **Human Life Value (HLV)** gap using age and income demographics to evaluate underinsurance/overinsurance risks, integrated with lifestyle health risk scoring.
* **Janam Patri (Wealth Projection):** Projects 10-year compounding timelines for income growth (8% p.a.), expense inflation (6% p.a.), cash compounding (4% p.a.), and investments (10% p.a.), accompanied by a dynamic Chart.js timeline graph.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask, Pandas, Scikit-Learn, Joblib
* **Frontend:** HTML5, Vanilla CSS3 (Custom radial gradients, glassmorphism card-blur effects), Bootstrap 5, FontAwesome Icons
* **Data Visualization:** Chart.js (Canvas charting)
* **Dataset:** 148 financial demographic training records (`Merged file.xlsx`)

---

## 📂 Project Structure

```text
├── app.py                             # Flask application backend (Advisory Logic & API Routes)
├── templates/
│   └── index.html                     # Tabbed frontend template, stylesheet, and JS engines
├── static/                            # Static assets (images, icons, etc.)
├── models/                            # Serialized ML files
├── Merged file.xlsx                   # Original demographic training dataset
├── expense_predictor_rf_corrected.pkl # Trained Random Forest Regressor model
├── requirements.txt                   # Project dependencies
├── technical_project_report.md        # Comprehensive technical report & interview guide
├── user_input_guide.md                # Field references, rules of thumb, and test profiles
└── README.md                          # Repository cover page (this file)
```

---

## 💻 Installation & How to Run

### Prerequisites
* Python 3.8+ installed on your system.

### Steps
1. **Clone the Repository**
   ```bash
   git clone https://github.com/Anuj-pratap-019/Explore_pm.git
   cd Explore_pm
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Local Web Server**
   ```bash
   python app.py
   ```

4. **Access the Dashboard**
   Open your browser and navigate to:
   ```text
   http://127.0.0.1:5000
   ```

---

## 📄 Documentation

For deep architectural details, calculations, debugging case studies, and interview preparation, please refer to the following documents:
* [Comprehensive Technical Project Report](technical_project_report.md)
* [User Input & Advisory Guide](user_input_guide.md)
