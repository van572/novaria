#!/bin/bash
streamlit run streamlit_app.py \
  --server.headless true \
  --server.port $PORT \
  --server.address 0.0.0.0 \
  --browser.gatherUsageStats false
