# Smart Receipt Manager 🧾

Hi! I'm a student trying things out, and this is my project to help manage messy paper receipts. It uses AI and rule-list to read and categorize your expenses automatically.   

You wanna only use it (and have german receipts) and dont think about code: Download the groq version, need an groq-account for it an create api-key (look it up where)   

You wanna change code / language: use groq - I used gemeni to clean the comments and make them english, good luck!   
You have good pc and wanna have it offline: use ollama (missing some crash-security, but it works excatly the same)    

change langueges, only needed in: rule_config and path_config   

anything below here is AI generated - have fun reading it, cuz I didnt   
---
## 🚀 Two Ways to Use AI

You can choose between two versions in this repository:

### 1. The "Fast" Version (Groq Cloud - v1.5)
* **What it does:** Sends the receipt text to the Groq Cloud. It's super fast.
* **Good for:** Everyone who wants it to "just work" without needing a powerful PC.
* **How to use:** You need a free API-Key from [Groq](https://console.groq.com/). Just paste it into the settings (⚙️) tab in the app.

### 2. The "Private" Version (Ollama - v1.0)
* **What it does:** Everything stays 100% on your computer. No data is sent to the internet.
* **Good for:** People who care about privacy or want to experiment with local LLMs.
* **How to use:** You need to have [Ollama](https://ollama.com/) installed and running on your PC.

---

## ✨ Features
* **OCR Scanning:** Turn photos of receipts into searchable PDFs (uses Tesseract).
* **Auto-Category:** AI decides if your purchase was "Food", "Electronics", or "Clothing".
* **Stats:** A simple dashboard to see where your money goes.
* **Memory:** If you manually correct a category once, the app remembers it for the next time.

---

## 🛠 How to Start

### I just want to use it:
1. Go to the **Releases** section on the right side of this page.
2. Download the `Setup.exe`.
3. Install it and start dragging your receipts into the window!

### I want to see/run the code:
1. Clone this repository.
2. Install the requirements: 
   `pip install PyQt6 pytesseract Pillow matplotlib requests groq`
3. Make sure you have **Tesseract OCR** installed on your PC.
4. Run `python main_gui.py`.

---

## 📂 Where is my data?
The app creates a folder in your **Documents** directory called `SmartReceipts`.
* `Input/`: Your raw receipts.
* `Processed_PDFs/`: Your digital archive.
* `CSV_Database/`: All your extracted numbers and the AI's "memory".

---
*Created as a learning project.*****
