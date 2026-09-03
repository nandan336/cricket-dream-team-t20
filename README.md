# 🏏 Cricket Dream Team Selector — ICC Men's T20 World Cup 2022-23

Built by: Nandan Chandrashekar & Himanshu Ravishankar
Live Dashboard: https://project.novypro.com/eU32JC
Tools: Python | Pandas | Power BI | DAX | Power Query | Web Scraping

## 📌 Project Overview

A fully data-driven system to select the Best XII players from the 
ICC Men's T20 World Cup 2022-23 — no bias, no fan favourites. 
Pure performance analytics.

We scraped real match data from ESPN Cricinfo, cleaned and 
transformed it using Python, modelled it in Power BI and built 
an interactive dashboard to explore player performance by role, 
team and KPI threshold.

## 🔧 Tech Stack

| Tool | Purpose |
|---|---|
| Bright Data + ParseHub | Web scraping ESPN Cricinfo |
| Python (Pandas, json, re) | Data preprocessing |
| Jupyter Notebook | Python environment |
| Power BI Desktop | Dashboard development |
| DAX | Custom KPI measures |
| Power Query | Data cleaning |
| NovyPro | Live dashboard publishing |

## 📁 Repository Structure

cricket-dream-team-t20/
├── T20_Data_Rreprocessing.ipynb   ← Python preprocessing
├── T20 Cricket Power BI.pbix      ← Power BI dashboard
├── Openers_Dashboard.png          ← Dashboard screenshot
├── README.md
└── data/
    ├── dim_match_summary.csv
    ├── fact_bating_summary.csv
    ├── fact_bowling_summary.csv
    ├── dim_players.csv
    └── dim_players_no_images.csv

## 🚀 How to Run

1. Clone this repository
2. Open T20_Data_Rreprocessing.ipynb in Jupyter
3. Run all cells to regenerate CSVs
4. Open T20 Cricket Power BI.pbix in Power BI Desktop
5. Update data source paths to your local data/ folder
6. Refresh — or view live dashboard on NovyPro

## 👥 Authors

Nandan Chandrashekar
Master of Data Analytics — QUT Brisbane
LinkedIn: linkedin.com/in/nandan-c-205935212
GitHub: github.com/nandan336

