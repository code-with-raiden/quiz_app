# Python Practice Quiz – QR Based

Students scan a QR code, enter name and roll number, and get 10 unique questions from that topic.

## Files

- `questions.json` – question bank (4 topics, 286 questions)
- `app.py` – Flask web app
- `make_qr.py` – creates 4 QR codes in `qr_codes/`
- `requirements.txt` – dependencies
- `issued.json` – created automatically, stores who got which questions

## Run locally

```bash
pip install -r requirements.txt
python make_qr.py http://localhost:5000
python app.py
```

Open http://localhost:5000 to test. QR codes are in `qr_codes/`.

## Deploy

1. Host the project (for example on Render, Railway, or a VPS) with start command:

   ```bash
   gunicorn -b 0.0.0.0:$PORT app:app
   ```

2. Regenerate the QR codes with your public URL:

   ```bash
   python make_qr.py https://your-app-url.com
   ```

3. Keep `issued.json` on persistent storage. If it is deleted, students may receive sets that were already issued.

## Check the question count

```bash
python3 -c "import json; d=json.load(open('questions.json')); print({k: len(v['questions']) for k,v in d['topics'].items()}); print('Total:', sum(len(v['questions']) for v in d['topics'].values()))"
```

## Reset

Delete `issued.json` before the real session so all students start fresh.
