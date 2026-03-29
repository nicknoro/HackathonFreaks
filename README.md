# DriveWise Pro

> **Your car, your route, your real MPG — DriveWise Pro turns vehicle specs into fuel intelligence across every road you drive.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-Random%20Forest-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-02A8A8?style=flat-square)](LICENSE)

---

## What is DriveWise Pro?

Fuel has shaped wars, recessions, and empires — yet most drivers, mechanics, and fleet managers make fuel decisions completely blind. DriveWise Pro is an AI-powered cockpit that predicts your real-world MPG across five driving environments, calculates the ROI of any car modification before you spend a dollar, and explains every prediction in plain English.

---

## Features

### Route Planner
Predicts your MPG across 5 real-world driving environments on an interactive Folium map.

| Route | Multiplier |
|---|---|
| Highway (Optimal) | 1.10× |
| Suburban (Mixed) | 0.90× |
| City (Stop-and-Go) | 0.75× |
| Mountainous (Incline) | 0.65× |
| Off-Road / Dirt | 0.55× |

### ROI Calculator
Enter any modification's cost and expected MPG gain. Instantly get the break-even month, annual savings, and a colour-coded payback verdict — across all 5 route types.

### AI Explainer
Feature importance cards, a plain-English verdict, and 4 live what-if sensitivity scenarios — so users always understand *why* their number is what it is.

### My Digital Garage
Save, name, compare, and export unlimited vehicle configurations as CSV.

---

## How It Works

The core prediction pipeline:

```
Base MPG  →  ML Model (Random Forest)  →  × Route Multiplier  →  Adjusted MPG  →  Fuel Cost
```

The model trains on the [UCI Auto-MPG dataset](https://archive.ics.uci.edu/dataset/9/auto+mpg) using four inputs: **cylinders, weight, horsepower, and acceleration**. It is cached locally after the first run — zero external APIs, works fully offline.

---

## Project Structure

```
drivewise/
├── Home.py                        # Home dashboard & entry point
├── pages/
│   ├── 1_Route_Planner.py    # Interactive map + route metrics
│   └── 2_ROI_Calculator.py   # Modification break-even calculator
├── tables/
│   ├── 3_AI_Explainer.py     # Feature importance + what-if analysis
│   └── 4_My_Garage.py        # Save, compare, export configurations
├── utils/
│   ├── calculations.py           # Core ML + business logic (single source of truth)
│   ├── model_loader.py           # Random Forest training & caching
│   └── sidebar.py                # Shared vehicle/fuel input controls
├── drivewise_model.pkl           # Pre-trained model (auto-generated if missing)
├── garage_data.csv               # Persisted garage configurations
└── requirements.txt
```

---

## Getting Started

```bash
# 1. Clone the repo
git clone https://github.com/your-username/drivewise-pro.git
cd drivewise-pro

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run Home.py
```

On first launch the app downloads the UCI dataset and trains the model automatically — this takes about 10–15 seconds. After that it runs from the cached `.pkl` file.

---

## Who Is This For?

| User | Use Case |
|---|---|
| Everyday Drivers | Know your real monthly fuel cost before choosing a route |
| Mechanics & Tuners | Show customers a break-even timeline before pitching an upgrade |
| Fleet Managers | Compare all vehicles across environments, export as CSV |
| City Planners | Model urban vs highway fleet costs at scale |
| Automotive Students | Learn which vehicle specs matter most via the AI Explainer |
| Auto Parts Retailers | Help customers justify purchases with ROI data |

---

## Tech Stack

- **[Streamlit](https://streamlit.io)** — multi-page app framework
- **[scikit-learn](https://scikit-learn.org)** — Random Forest Regressor
- **[Folium](https://python-visualization.github.io/folium/) + [streamlit-folium](https://folium.streamlit.app)** — interactive maps
- **[pandas](https://pandas.pydata.org)** — data handling & CSV export
- **[joblib](https://joblib.readthedocs.io)** — model serialization

---

## Contributing

Pull requests are welcome. For major changes please open an issue first.

1. Fork the repo
2. Create your branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push and open a Pull Request

---

## License

MIT — see [`LICENSE`](LICENSE) for details.

---

<div align="center">

Built with ⚡ by **HackathonFreaks**

</div>
