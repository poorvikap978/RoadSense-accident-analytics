cat > README.md << 'EOF'
 RoadSense: Accident Severity Classification and Hotspot Clustering

A DWDM course project applying classification, clustering, and association rule mining to the US Accidents dataset.

## Features
- **Classification**: Naive Bayes, Decision Tree, SVM — predicting accident severity
- **Clustering**: K-Means, DBSCAN — identifying accident hotspots
- **Association Rules**: Apriori, FP-Growth — finding condition patterns linked to severity

## Tech Stack
- Python, scikit-learn, mlxtend
- Streamlit (frontend), Flask (middleware), SQLite (backend)

## Key Findings
- Decision Tree achieved 78.4% accuracy, outperforming Naive Bayes and SVM
- K-Means outperformed DBSCAN for hotspot clustering (silhouette 0.340 vs 0.139)
- Night-time + low temperature conditions showed 3.6x higher likelihood of major severity accidents

## Setup
1. Clone this repo
2. Install dependencies: pip install -r requirements.txt
3. Download the US Accidents dataset from Kaggle and place it in the project root
4. Run notebooks in order: explore → preprocess → classification → clustering → association
5. Start the app: ./start.sh
EOF

git add README.md
git commit -m "Add README"
git push
