#!/bin/bash
lsof -ti:9000 | xargs kill -9 2>/dev/null
lsof -ti:8501 | xargs kill -9 2>/dev/null
echo "Stopped Flask and Streamlit"