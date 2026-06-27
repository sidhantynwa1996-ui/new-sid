import json
import re

KNOWN_TITLES = {
    1: {
        1: "Rates and Returns",
        2: "Time Value of Money in Finance",
        3: "Statistical Measures of Asset Returns",
        4: "Probability Trees and Conditional Expectations",
        5: "Portfolio Mathematics",
        6: "Simulation Methods",
        7: "Estimation and Inference",
        8: "Hypothesis Testing",
        9: "Parametric and Non-Parametric Tests of Independence",
        10: "Simple Linear Regression",
        11: "Introduction to Big Data Techniques",
        12: "Evaluating Regression Model Fit and Interpreting Model Results",
    },
    2: {
        1: "The Firm and Market Structures",
        2: "Understanding Business Cycles",
        3: "Fiscal Policy",
        4: "Monetary Policy",
        5: "Introduction to Geopolitics",
        6: "International Trade",
        7: "Capital Flows and the FX Market",
        8: "Exchange Rate Calculations",
    },
    3: {
        1: "Organizational Forms, Corporate Issuer Features, and Ownership",
        2: "Investors and Other Stakeholders",
        3: "Corporate Governance: Conflicts, Mechanisms, Risks, and Benefits",
        4: "Working Capital and Liquidity",
        5: "Capital Investments and Capital Allocation",
        6: "Capital Structure",
        7: "Business Models",
    },
    4: {
        1: "Introduction to Financial Statement Analysis",
        2: "Analyzing Income Statements",
        3: "Analyzing Balance Sheets",
        4: "Analyzing Statements of Cash Flows I",
        5: "Analyzing Statements of Cash Flows II",
        6: "Analysis of Inventories",
        7: "Analysis of Long-Term Assets",
        8: "Topics in Long-Term Liabilities and Equity",
        9: "Analysis of Income Taxes",
        10: "Financial Reporting Quality",
        11: "Financial Analysis Techniques",
        12: "Introduction to Financial Statement Modeling",
    },
    5: {
        1: "Market Organization and Structure",
        2: "Security Market Indexes",
        3: "Market Efficiency",
        4: "Overview of Equity Securities",
        5: "Company Analysis: Past and Present",
        6: "Industry and Competitive Analysis",
        7: "Company Analysis: Forecasting",
        8: "Equity Valuation: Concepts and Basic Tools",
    },
    6: {
        1: "Fixed-Income Instrument Features",
        2: "Fixed-Income Cash Flows and Types",
        3: "Fixed-Income Issuance and Trading",
        4: "Fixed-Income Markets for Corporate Issuers",
        5: "Fixed-Income Markets for Government Issuers",
        6: "Fixed-Income Bond Valuation: Prices and Yields",
        7: "Yield and Yield Spread Measures for Fixed-Rate Bonds",
        8: "Yield and Yield Spread Measures for Floating-Rate Instruments",
        9: "The Term Structure of Interest Rates: Spot, Par, and Forward Curves",
        10: "Interest Rate Risk and Return",
        11: "Yield-Based Bond Duration Measures and Properties",
        12: "Yield-Based Bond Convexity and Portfolio Properties",
        13: "Curve-Based and Empirical Fixed-Income Risk Measures",
        14: "Credit Risk",
        15: "Credit Analysis for Government Issuers",
        16: "Credit Analysis for Corporate Issuers",
        17: "Fixed-Income Securitization",
        18: "Asset-Backed Security (ABS) Instrument and Market Features",
        19: "Mortgage-Backed Security (MBS) Instrument and Market Features",
    },
    7: {
        1: "Derivative Instrument and Derivative Market Features",
        2: "Forward Commitment and Contingent Claim Features and Instruments",
        3: "Derivative Benefits, Risks, and Issuer and Investor Uses",
        4: "Arbitrage, Replication, and the Cost of Carry in Pricing Derivatives",
        5: "Pricing and Valuation of Forward Contracts",
        6: "Pricing and Valuation of Futures Contracts",
        7: "Pricing and Valuation of Interest Rates and Other Swaps",
        8: "Pricing and Valuation of Options",
        9: "Option Replication Using Put-Call Parity",
        10: "Valuing a Derivative Using a One-Period Binomial Model",
    },
    8: {
        1: "Alternative Investment Features, Methods, and Structures",
        2: "Alternative Investment Performance and Returns",
        3: "Investments in Private Capital: Equity and Debt",
        4: "Real Estate and Infrastructure",
        5: "Natural Resources",
        6: "Hedge Funds",
        7: "Introduction to Digital Assets",
    },
    9: {
        1: "Portfolio Risk and Return: Part I",
        2: "Portfolio Risk and Return: Part II",
        3: "Portfolio Management: An Overview",
        4: "Basics of Portfolio Planning and Construction",
        5: "The Behavioral Biases of Individuals",
        6: "Introduction to Risk Management",
    },
    10: {
        1: "Ethics and Trust in the Investment Profession",
        2: "Code of Ethics and Standards of Professional Conduct",
        3: "Guidance for Standards I-VII",
        4: "Introduction to the Global Investment Performance Standards (GIPS)",
        5: "Ethics Application",
    },
}

with open(r"C:\Users\siddh\cfa-tutor\cfa_content.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for vol in data:
    vol_num = vol["volume"]
    vol_titles = KNOWN_TITLES.get(vol_num, {})
    for ch in vol["chapters"]:
        ch_num = ch["chapter"]
        if ch_num in vol_titles:
            ch["title"] = vol_titles[ch_num]

with open(r"C:\Users\siddh\cfa-tutor\cfa_content.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

total = sum(len(v["chapters"]) for v in data)
print(f"Fixed titles for {total} modules across {len(data)} volumes.")
for vol in data:
    print(f"\n  Volume {vol['volume']} - {vol['subject']}:")
    for ch in vol["chapters"]:
        print(f"    Module {ch['chapter']}: {ch['title']}")
