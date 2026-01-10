# AI_Guru_J
This is Our  final Year Project
members:
1. Vishnu Premarajan
2. Mohammed Ijas p
3. Eshan Fadil
4. Juned


# Frontend Setup:
```bash
cd frontend
npm run dev     

Once frontend is run, open this link in your browser.  http://localhost:5173/
```


# Backend Setup:

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file in the `backend/` directory:
   ```env
   GROQ_API_KEY="your_groq_api_key"
   MONGODB_URI="mongodb://localhost:27017/ai_guru_j_db"
   RHUBARB_BINARY="rhubarb"  # Path to your rhubarb binary
   FFMPEG_PATH="ffmpeg"      # Path to your ffmpeg binary
   ```

3. **Start the server**:
   ```bash
   uvicorn app.main:app --reload
   ```


# Open interactive docs
- Visit: http://127.0.0.1:8000/docs



# Quick debug check (DB + DNS)
- GET debug status:
```bash
curl http://127.0.0.1:8000/debug/db
```
- Response fields: `initialized`, `reachable`, `host`, `srv_records` / `a_records` or error messages.



# Test tutor query endpoint (mock pipeline)
```bash
curl -X POST "http://127.0.0.1:8000/api/tutor/query/" \
  -F "audio_file=@/path/to/sample.wav"
```
- Expected JSON keys: `query`, `explanation_text`, `lip_sync_json`, `audio_url`



# (Optional) Serve / download audio
- If the project exposes `/api/tutor/audio_stream/`, request it:
```bash
curl http://127.0.0.1:8000/api/tutor/audio_stream/ --output response.mp3
```



# Run project tests / helper scripts
```bash

cd backend
# if test_api.py is provided and executable
python test_api.py
# or, if you use pytest
pytest
```