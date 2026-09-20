# RECORDING_CHECKLIST.md — Project VAJRA

Use this checklist before pressing Record, during your recording session, and during post-recording video editing to ensure an award-winning Smart India Hackathon submission demo.

---

## 1. Pre-Recording System Checks

- [ ] **Daemon Status**: Backend batch supervisor is active on `http://127.0.0.1:8000`. Test with:
  ```powershell
  curl http://127.0.0.1:8000/cases
  ```
- [ ] **Frontend Status**: Next.js development server is responsive at `http://localhost:3000`.
- [ ] **Clean Browser Environment**:
  - Open an Incognito or dedicated clean profile window.
  - Set resolution to **1920x1080** (Full HD).
  - Hide bookmarks bar (`Ctrl + Shift + B`).
  - Disable browser extension popups (Grammarly, password managers, ad blockers).
  - Clear previous PDF downloads from the `Downloads/` directory to avoid `...dossier (1).pdf` filenames.
- [ ] **Operating System Environment**:
  - Turn ON Windows **Focus Assist** / Do Not Disturb (mute notifications, Slack, WhatsApp, Telegram).
  - Hide desktop icons or keep browser strictly full-screen.
- [ ] **Audio & Voice Calibration**:
  - Microphone positioned 6–8 inches from mouth with pop filter.
  - Speak at an authoritative, clear pace (130–140 words per minute).
  - Test record 10 seconds of speech and listen back on headphones.

---

## 2. During Recording Execution

- [ ] **Hook Delivered Before Clicks**: Deliver Beat 1 narration ("Over one thousand crore rupees...") *before* interacting with the form.
- [ ] **Intentional Cursor Movements**:
  - Move the cursor in straight, calm lines.
  - Hover over key elements (Suspect Wallet, Complaint Ack Slip, Actionable Custodian badge) for 1.5 seconds.
  - Keep cursor stationary while speaking about conceptual points (e.g. while explaining the 3-Number Framework).
- [ ] **The "Wow Moment" Holds**:
  - When the React Flow graph renders, let the visual hold for **2 full seconds** before clicking any sub-tabs.
  - When the PDF downloads, open it immediately to show the official emblem and Section 91 CrPC notice.

---

## 3. Editing & Post-Production Checklist

- [ ] **Rough Cut Validation (Screen + Voice Only)**:
  - Sequence flows chronologically: Problem → NCRP Portal → Live Queue → Multi-Hop Graph → 3 Scores → ATLAS Hypotheses → PDF Export.
  - Cut all pauses where the cursor is idle or waiting for network requests.
- [ ] **Visual Polish**:
  - Add subtle zoom-ins (115–125%) when focusing on:
    1. The Complaint Acknowledgment Slip on `/ncrp`.
    2. The 3 Metric Cards (`0.88`, `95%`, `0.63`).
    3. The Actionable Custodian node on the graph canvas.
    4. The Section 91 CrPC notice on the downloaded PDF.
- [ ] **On-Screen Captions & Callouts**:
  - Lower-third label at 0:25: `NCRP / 1930 Helpline Automated Webhook Ingestion`
  - Lower-third label at 1:15: `Real-Time Multi-Hop Graph Tracing (Etherscan V2 Sync)`
  - Lower-third label at 1:48: `3-Tier Framework: Deterministic Rules + XGBoost CUDA ML`
  - Lower-third label at 2:08: `ATLAS: Counter-Hypothesis Legal Stress-Testing`
  - Lower-third label at 2:35: `Section 91 CrPC Automated Law Enforcement Dossier`
- [ ] **Audio Mixing**:
  - Voiceover peak normalized to **-1.0 dB to -3.0 dB**.
  - Background music (cinematic/investigative tech track) mixed low at **-22 dB to -26 dB**.
  - Music drops by an additional 3 dB whenever speaking begins (audio ducking).

---

## 4. Pre-Publish Validation (The Judge Test)

- [ ] **Muted Mobile Check**: Watch the video on a smartphone with **sound muted**. Can someone understand what happened just from the screen and on-screen callouts?
- [ ] **Judges Rubric Check**:
  - **Innovation**: Real-time integration with Helpline 1930 / CFCFRMS.
  - **Technical Depth**: Bounded BFS graph algorithms, live Etherscan V2 API, GPU XGBoost model, SHA-256 evidence ledger.
  - **Legal Feasibility**: ATLAS counter-hypotheses and Section 91 CrPC compliance.
  - **Presentation Quality**: Clean UI, zero lag, smooth transitions.
- [ ] **Total Runtime**: Under **3 minutes** (ideal target: `2:40` to `2:50`).

---

## 5. File Naming & Submission Packaging

- Export as: `VAJRA_SIH2026_Final_Demonstration_1080p.mp4`
- Video Codec: H.264 / AVC, High Profile
- Audio Codec: AAC Stereo, 320 kbps, 48 kHz
- Thumbnail: Screen capture of the interactive multi-hop graph with glowing nodes and the title: **"PROJECT VAJRA — Zero-Second Crypto Forensics"**.
