#!/bin/bash

# Start FastAPI in the background on port 8080
uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8080 &

# Start Streamlit in the foreground on port 8501
streamlit run app/app.py \
  --server.address=0.0.0.0 \
  --server.port=8501
