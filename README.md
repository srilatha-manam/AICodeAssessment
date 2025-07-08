# AICodeAssessment
This application will evaluate the code using Judge0 API and Generate feedback using gemini 1.5
Note:  create your own accounts for Judge0API and Gemini to get API keys

Run commands:
**Backend :**
uvicorn Backend.main:app --reload 
or
uvicorn main:app --host 0.0.0.0 --port 10000

**Frontend:**
streamlit run Frontend/app.py
or
streamlit run Frontend/app.py --server.address=0.0.0.0

