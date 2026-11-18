# Python Mock Assessment Portal 📝

A dynamic assessment system with **3 hierarchical QR codes**. Students scan a QR code with their mobile phone and immediately receive a unique, randomized 10-question assessment paper with **both Scenario and Question**.

## 🚀 Key Features

- **3 Difficulty Levels**:
  - 🟢 **Basic Level**: Conditionals (`if`, `if-else`, `elif`, `nested if`) — 150 questions.
  - 🟡 **Intermediate Level**: Functions, Decorators, Generators + Basic Conditionals — 206 question pool.
  - 🔴 **Advanced Level**: OOP, Exceptions, Comprehensions, Lambda, Map, File Handling + All levels — 286 question pool.
- **Hierarchical Question Pooling**:
  - Basic questions can appear in Intermediate and Advanced.
  - Intermediate questions can appear in Advanced.
- **Anti-Cheating Randomization**:
  - Students sitting side-by-side scanning the same QR code receive completely different question sets ($>10^{15}$ combinations).
  - Both **Scenario** and **Question** are displayed clearly for each question.
- **No Database Storage**:
  - All paper selection happens on-the-fly via deterministic seeding.
  - If a student's phone screen locks or reloads, their assigned paper stays the same via session state / query parameters.

---

## 🏃 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
python -m pip install streamlit
### 2. Generate QR Codes
To generate QR codes automatically mapped to your local Wi-Fi / LAN IP (so students can scan from mobile phones connected to the same Wi-Fi):
```bash
python make_qr.py
```
*(Or specify a custom host/domain)*:
```bash
python make_qr.py http://192.168.1.100:8501
```
This generates 3 images in `qr_codes/`:
- `qr_basic.png`
- `qr_intermediate.png`
- `qr_advanced.png`

### 3. Start the Streamlit Application
```bash
python -m streamlit run app.py --server.port 8501
```

---

## 📂 Project Structure

```
quiz/
├── app.py              # Streamlit portal (QR landing & student assessment view)
├── make_qr.py          # Script to generate the 3 QR codes
├── questions.json      # Structured database of 286 scenario-based questions
├── qr_codes/           # Generated QR codes (Basic, Intermediate, Advanced)
├── mock/               # Raw mock question source files
└── requirements.txt    # Dependencies (streamlit, qrcode[pil])
```
