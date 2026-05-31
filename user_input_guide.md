# AI Backed "Explore PM" (Portfolio Manager) Program - User Input & Advisory Guide

This guide describes all the input parameters used across the various tabs of the **AI Backed "Explore PM" (Portfolio Manager) Program** dashboard. It explains whether the values represent monthly flows or cumulative balances, outlines the financial "rules of thumb" for each metric, and provides sample data profiles to help you test different advisory outcomes.

---

## 1. Input Fields Reference

| Input Field | Type | Description | Financial Rule of Thumb |
| :--- | :--- | :--- | :--- |
| **Age** | Years | The user's current age. Used to calculate working years remaining (up to retirement age 60) and health risk. | Older age (>50) increases health risk scoring; younger age gives longer wealth projection compounding. |
| **Gross Monthly Income** | Monthly | Total pre-tax income earned per month (Salary, Business revenue). | The foundation of all cash flow calculations. |
| **Net Monthly Income** | Monthly | Take-home pay after tax deductions, PF, and other withholdings. | Must always be lower than Gross Income (typically **75% to 85%** of Gross). |
| **Monthly Expenses** | Monthly | Current actual monthly spending (Rent, food, transport, bills, entertainment). | Target to keep this **below 70%** of Net Income to ensure a healthy saving capacity. |
| **Liquid Savings** | Cumulative | Total cash sitting in bank savings accounts, sweep accounts, or short-term fixed deposits. | Keep **1 to 2 months** of expenses here for immediate cash needs; invest the rest. |
| **Emergency Fund** | Cumulative | Cash reserved strictly for emergency coverage (loss of job, medical crises). | Should equal **3 to 6 months** of your average monthly expenses. |
| **Investments** | Cumulative | Total current market value of all investments (Mutual funds, stocks, gold, bonds). | Ideally, this should grow to be **5x to 10x** of your annual income as you progress in your career. |
| **Total Debt** | Cumulative | Sum of all outstanding loans (Car, education, home, credit card dues). | Monthly debt payments (EMIs) should be **less than 36%** of your Gross Monthly Income. |
| **Current Life Cover** | Cumulative | The payout amount (Sum Assured) of your term insurance policy. | Should be **10x to 15x** of your Gross Annual Income. |
| **Lifestyle Score** | Score (1-10) | Rating of your habits (10 = very active & healthy, 1 = smoking, poor sleep, sedentary). | Low score (≤ 5) flags medium/high health risks. |
| **Occupation** | Text | Current job title (e.g. IT Developer, Student, Retired). | Used to check risk factors (office desk jobs have slightly elevated desk-risk flags; student/retired statuses trigger conservative FD alerts). |
| **Family Medical History** | Select | History of major hereditary illnesses. | Select "Yes" to trigger critical illness warnings in the health risk analyzer. |

---

## 2. Recommended Input Profiles for Testing

Use these three complete profiles to check if the advisory engines are functioning correctly:

### Profile A: "The High-Earning Wealth Builder" (Aggressive Growth & Tax-Saving)
Use this profile to test **ELSS** recommendations and adequate insurance coverage.

* **Dashboard Inputs:**
  * `Age`: `32`
  * `Gross Monthly Income`: `₹1,80,000`
  * `Net Monthly Income`: `₹1,45,000`
  * `Monthly Expenses`: `₹55,000`
  * `Liquid Savings`: `₹4,00,000`
  * `Emergency Fund`: `₹2,50,000` *(Safe buffer: ~4.5 months)*
  * `Investments`: `₹8,00,000`
  * `Total Debt`: `₹40,000` *(Very low debt)*
  * `Current Life Cover`: `₹2,50,00,000` *(2.5 Crore term plan)*
  * `Occupation`: `Software Engineer`
  * `Lifestyle Score`: `8`
  * `Family History`: `No`
* **Expected Result:**
  * **Investment Tab:** Recommends **ELSS (Tax-saving mutual funds)** due to high income, low debt, and strong savings.
  * **Insurance Tab:** Flags as **Adequately Insured** (HLV for 28 working years is ~₹3 Crore; a 2.5 Crore cover is well within the 70% threshold). Health risk is marked as **Low**.

---

### Profile B: "The Under-Prepared Spender" (Liquidity Warnings & Underinsurance)
Use this profile to test **emergency fund warnings** and underinsurance gaps.

* **Dashboard Inputs:**
  * `Age`: `42`
  * `Gross Monthly Income`: `₹80,000`
  * `Net Monthly Income`: `₹68,000`
  * `Monthly Expenses`: `₹60,000` *(High spending ratio)*
  * `Liquid Savings`: `₹20,000` *(Vulnerable cash)*
  * `Emergency Fund`: `₹15,000` *(Vulnerable; < 1 month)*
  * `Investments`: `₹30,000`
  * `Total Debt`: `₹4,50,000` *(High credit card & personal debt)*
  * `Current Life Cover`: `₹10,00,000` *(Very low insurance)*
  * `Occupation`: `Office Administrator`
  * `Lifestyle Score`: `4` *(Sedentary/unhealthy habits)*
  * `Family History`: `Yes`
* **Expected Result:**
  * **Investment Tab:** Recommends **Savings Account / Liquid Fund** rather than SIP/PPF. Shows warning about high debt and warns to build a 3-month emergency runway of ₹1,80,000.
  * **Insurance Tab:** Flags as **Underinsured** with a clear calculation of the coverage gap (HLV is ~₹86 Lakhs, meaning the gap is ~₹76 Lakhs). Health risk is marked as **High** due to medical history and lifestyle.

---

### Profile C: "The Conservative Student/Intern" (Capital Preservation & FDs)
Use this profile to test low-income capital preservation logic.

* **Dashboard Inputs:**
  * `Age`: `21`
  * `Gross Monthly Income`: `₹20,000`
  * `Net Monthly Income`: `₹18,000`
  * `Monthly Expenses`: `₹10,000`
  * `Liquid Savings`: `₹35,000`
  * `Emergency Fund`: `₹10,000`
  * `Investments`: `₹5,000`
  * `Total Debt`: `₹0`
  * `Current Life Cover`: `₹0`
  * `Occupation`: `Student / Intern`
  * `Lifestyle Score`: `9`
  * `Family History`: `No`
* **Expected Result:**
  * **Investment Tab:** Recommends **Fixed Deposit (FD) / Debt Funds** for safety and capital preservation because of the student occupation and entry-level income.
  * **Overview Hub:** Displays a high Savings Rate (~44%) and green status indicators.
