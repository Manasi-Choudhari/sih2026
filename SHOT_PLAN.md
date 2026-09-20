# SHOT_PLAN.md — Project VAJRA

> Use this document side-by-side with your screen recorder (OBS / Loom / QuickTime). Every shot is mapped directly to the line of narration it delivers.

---

## Pre-Record Setup Checklist

- [ ] **Backend Server**: Ensure `cmd /c run_backend.cmd` is running on `http://127.0.0.1:8000`.
- [ ] **Frontend Dev Server**: Ensure Next.js is running on `http://localhost:3000`.
- [ ] **Browser Window**: Chrome / Edge set to **1920x1080** (or full-screen 1080p).
- [ ] **Browser Zoom Level**: **100%** (or 110% if on 4K display so labels and wallet hashes are crisp).
- [ ] **Browser Cleanliness**: Close all personal tabs, bookmarks bar hidden (`Ctrl + Shift + B`), notifications muted.
- [ ] **Initial URL**: Open tab to `http://localhost:3000/ncrp`.
- [ ] **Microphone & Audio**: Clear voice capture, room quiet, no background echo.

---

## Shot-by-Shot Matrix

| Shot # | Time | Screen State / Visual | Narration Line | Technical Detail to Highlight | Edit / Camera Note |
| :---: | :---: | :--- | :--- | :--- | :--- |
| **1** | `0:00–0:12` | Full browser view of `/ncrp`. Tricolor top bar, I4C / MHA badge, and title visible. | *"Over one thousand crore rupees are siphoned into cryptocurrency fraud schemes reported on the National Cybercrime Reporting Portal every year..."* | MHA / CFCFRMS 1930 Helpline branding | Static, majestic hold. Cursor rests near top emblem. |
| **2** | `0:12–0:22` | Slow scroll down `/ncrp` showing citizen complaint input fields. | *"...When a victim dials Helpline 1930, investigating officers face an impossible race against time. We built Project VAJRA to compress that forty-eight-hour investigation into less than ten seconds."* | Citizen Financial Cyber Fraud Reporting System UI | Smooth downward scroll. Do not jerk cursor. |
| **3** | `0:22–0:35` | Click **"Scenario 1: Phishing / Seed Drain"** card. Form auto-fills with 2.5 ETH and suspect wallet `0x71C6...`. | *"Here on the NCRP Gateway, citizen complaints enter the CFCFRMS pipeline. With one click, an incident involving a 2.5 Ethereum drain into suspect wallet 0x71C6 is lodged."* | Form fields reacting to preset | Highlight suspect wallet field with brief cursor hover. |
| **4** | `0:35–0:50` | Click **"Lodge Complaint & Auto-Triage on VAJRA"**. Green acknowledgment modal / receipt appears. | *"Instantly, VAJRA's automated webhook activates. Notice the official acknowledgment slip: hops are already bounded, initial risk is scored, and an automated callback notifies the national helpline system."* | Webhook response (`/api/v1/external/ncrp/webhook`), Complaint Ack No (`2026/NCRP/DL/...`) | Hold green receipt for 3 seconds so viewer reads acknowledgment. |
| **5** | `0:50–1:00` | Navigate to `/queue` (Officer Queue). Top row shows newly lodged case with "NCRP Gateway Live" badge. | *"Switching to the VAJRA Officer Console, the complaint appears in real time without a page refresh."* | Auto-polling queue detection | Highlight blinking live green status badge. |
| **6** | `1:00–1:12` | Click **"Investigate"** on `case_s1`. Page transitions to `/cases/case_s1/overview`. | *"High-velocity drains are flagged with high priority. As an investigator, we simply click into the case to access the complete cyber forensics suite."* | Route change to `/cases/[id]/overview` | Smooth cursor click on the Action button. |
| **7** | `1:12–1:30` | Interactive React Flow Graph loads with animation. Victim node ➔ Intermediary hop ➔ Binance Hot Wallet 14. | *"This is VAJRA's live forensics graph. In under a second, our bounded breadth-first search engine explored the transaction tree."* | Bounded BFS algorithm, React Flow node layout | Slow zoom into the graph canvas. Let edges pulse. |
| **8** | `1:30–1:45` | Hover over terminal node **Binance (Hot Wallet 14)**. Show tooltip / badge: `ACTIONABLE CUSTODIAN`. | *"For Ethereum wallets, VAJRA utilizes live Etherscan V2 API queries to stream on-chain transaction logs in real time. Stolen funds arrived directly at Binance Hot Wallet 14. We now have an actionable custodian."* | Live Etherscan V2 Explorer sync (`EXPLORER_API_KEY_ETH`) | Zoom crop into terminal node for 2 seconds. |
| **9** | `1:45–2:05` | Pan up to the **3 Metric Cards**: `0.88` Rule Risk, `95%` Attribution, `0.63` ML Anomaly. | *"Unlike black-box systems, VAJRA enforces a strict Three-Number Confidence Framework. First: a deterministic Rule Risk Score of 0.88... Second: Attribution Confidence of ninety-five percent... And third: our GPU-accelerated XGBoost ML model evaluates transaction velocity..."* | 3-Number Framework: Rule Risk vs Attribution vs ML XGBoost CUDA | Highlight each card sequentially with subtle cursor guidance. |
| **10** | `2:05–2:15` | Click the **ATLAS Counter-Hypotheses** tab below the graph. Show alternative hypotheses. | *"Defense attorneys will always challenge blockchain evidence. That's why we developed ATLAS—our Automated Typology & Legal Argumentation System. ATLAS stress-tests the leading hypothesis against alternative explanations..."* | Competing hypotheses: Permit2 drainer, Internal sweep, OTC settlement | Show the robustness score (88%) and contradiction points. |
| **11** | `2:15–2:25` | Click the **Evidence Ledger** tab. Show table of chained records with green verified badge and SHA-256 hashes. | *"Every transaction is appended to a cryptographic, tamper-evident SHA-256 ledger."* | Tamper-evident ledger, Merkle root hash | Hold on SHA-256 hash column for 1.5 seconds. |
| **12** | `2:25–2:35` | Click **"Generate Formal Report"** button in top right. Page loads `/cases/case_s1/report`. | *"Finally, the operational payoff. With one click on 'Export Verified PDF'..."* | Standardized Investigation Report Dossier | Instant transition to clean institutional report page. |
| **13** | `2:35–2:45` | Click **"Export Verified PDF"**. Show PDF file downloading instantly. Open the downloaded PDF in viewer. | *"...VAJRA generates a legally authenticated Investigation Dossier complete with statutory Section 91 CrPC freeze notices for the exchange's legal compliance desk. Project VAJRA transforms fragmented blockchain data into actionable law enforcement outcomes."* | Pure PDF 1.4 Binary Generator, Section 91 CrPC Statutory Notice | Show PDF open with official seal, tricolor bar, and signature line. Fade to black. |

---

## Composition Rules for Recording

1. **Never hide the URL bar completely**: Evaluators like knowing this is running on genuine endpoints (`localhost:3000/ncrp`, `localhost:3000/queue`, etc.).
2. **Smooth Cursor Dynamics**: Stop the mouse when talking about a specific concept. Do not swirl or shake the mouse pointer across the screen.
3. **Pacing on Results**: When the graph renders and when the PDF downloads, let the screen breathe for at least **2 seconds** without clicking away.
4. **Volume Balance**: Set your microphone gain so speech is crisp, with background ambient music (if any) mixed at **-22 dB or lower**.

---

## Reset Instructions (Between Takes)

If a recording take fails or you want to restart fresh:
1. Refresh `http://localhost:3000/ncrp`.
2. Click **"Scenario 1: Phishing / Seed Drain"** card to restore default inputs.
3. Open `http://localhost:3000/queue` in a second tab to verify existing cases are loaded.
4. Clean your browser downloads folder so clicking "Export Verified PDF" creates a clean `VAJRA_Investigation_Dossier_case_s1.pdf` without `(1)` or `(2)` suffixes.
