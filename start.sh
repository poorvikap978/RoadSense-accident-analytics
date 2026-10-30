pkill -9 -f "python3 app.py"
pkill -9 -f "streamlit run"
lsof -ti:9000 | xargs kill -9 2>/dev/null
lsof -ti:8501 | xargs kill -9 2>/dev/null

cd /Users/poorvikap/Desktop/RoadSense/app/backend
nohup python3 app.py > flask.log 2>&1 &
sleep 2

cd /Users/poorvikap/Desktop/RoadSense/app/frontend
nohup streamlit run streamlit_app.py > streamlit.log 2>&1 &
sleep 2

curl http://localhost:9000/
open http://localhost:9000