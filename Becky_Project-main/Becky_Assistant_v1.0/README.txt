🧠 Becky Assistant GM v1.0 – Voice Assistant for OOTP

🎯 Features:
- Voice interaction via ElevenLabs
- Reads team exports from OOTP
- Gives coaching insight, commentary, and feedback

📂 Folder Structure:
- assistant_gm.py → main logic
- becky_voice.py → ElevenLabs speech
- data_adapter.py → loads CSV team data
- exports/ → place your OOTP team export (team_roster.csv)
- launcher.py → start the app
- assets/ → UI, avatar, etc. (empty for now)

🛠️ Setup:
1. Install Python 3.10+
2. pip install -r requirements.txt
3. Add your ElevenLabs API key in becky_voice.py
4. Run via: python launcher.py
5. (Optional) Build launcher.exe with: build_exe.bat
