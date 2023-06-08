#!/bin/bash


streamlit run streamlit.py --server.port=8888 --server.address=0.0.0.0 --browser.gatherUsageStats=false --server.enableCORS=false --server.enableXsrfProtection=false

# you need run port-forward outside pod, expose 31000 -> pod inner 8081, see streamlit_export.sh in host machine /root dir
