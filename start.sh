#!/bin/bash
echo "Starting Flask backend..."
cd app/backend
nohup python3 app.py > flask.log 2>&1 &
echo "Flask PID: $!"

sleep 2

echo "Starting Streamlit frontend..."
cd ../frontend
nohup streamlit run streamlit_app.py > streamlit.log 2>&1 &
echo "Streamlit PID: $!"

echo "Both servers starting. Check flask.log and streamlit.log if issues occur."