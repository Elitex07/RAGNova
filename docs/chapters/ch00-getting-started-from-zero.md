# Chapter 0 — Getting Started From Absolute Zero (Day 0 / Day 1 evening)

> **Who this chapter is for.** Someone who has never installed VS Code, has never opened a terminal, is not sure what Python actually *is*, and last saw a square root in school. If that's you, you are in exactly the right place. Nothing here is assumed. Nothing here is skipped.
>
> **If you already code comfortably in Python and know what pip and a virtual environment are**, skim Part C (the maths refresher) and Part D (jargon), then go straight to [Chapter 1](ch01-objective-and-problem-identification.md).
>
> **Contents:** Part A gets your machine working *and includes a full Python primer (§A.6) covering exactly what this project uses.* Part B explains the concepts Chapter 1 opens with. Part C decodes the maths notation in ten minutes. Part D is a jargon table. Part E is troubleshooting. Part F is the checklist you must clear before Chapter 1.
>
> **Time:** ~90 minutes for Parts A.1–A.5 and B–F, plus two evenings for the Python primer if you have never programmed.

---

## What this chapter is NOT

There is a Chapter 5 later called "Environment Setup." That is a different thing, and confusing the two wastes a day:

| | Chapter 0 (this one) | Chapter 5 |
|---|---|---|
| **Question it answers** | Can my computer run Python at all? | Can my computer run *this project's* AI models? |
| **You install** | VS Code, Python | Ollama, ChromaDB, PyTorch, Whisper, etc. |
| **When** | Day 0 / Day 1 evening | Day 5 |
| **Skip it if** | You already program in Python | Never skip it |

Do Chapter 0 **before** Chapter 1's theory if you're new. It takes about 90 minutes, most of which is downloads running in the background while you read.

---

# Part A — Making your computer usable

Instructions are written for **Windows 11** (what this team is on). macOS differences are noted in indented boxes.

## A.1 The terminal: the black box you type commands into

Everything in software development eventually goes through a **terminal** — a window where you type text commands instead of clicking buttons. It feels archaic. It is also the fastest, most precise way to control a computer, which is why it never went away.

**Open it on Windows:** press `Win` key, type `powershell`, press Enter. A blue window appears with something like:

```
PS C:\Users\yourname>
```

That is a **prompt**. It is telling you two things: `PS` means PowerShell, and `C:\Users\yourname` is the folder you are currently "standing in."

> **macOS:** press `Cmd + Space`, type `terminal`, press Enter. Your prompt looks like `yourname@MacBook ~ %`.

### Try these four commands right now

Type each, press Enter, watch what happens. You cannot break anything with these — they only look, they do not change.

| Command (Windows) | macOS equivalent | What it does |
|---|---|---|
| `dir` | `ls` | List everything in the current folder |
| `cd Desktop` | `cd Desktop` | **C**hange **D**irectory — walk into the Desktop folder |
| `cd ..` | `cd ..` | Walk *back out* one folder (`..` means "the folder above me") |
| `cd X:\RAGNova` | `cd ~/RAGNova` | Jump straight to our project folder |

**That's genuinely 90% of the terminal skill you need for this project.** Move around with `cd`, look around with `dir`, and later run programs by typing their name.

### Two things that will confuse you once, then never again

**Folder vs directory.** Same thing. "Directory" is the older word; both are used interchangeably, including in these docs.

**Absolute vs relative paths.**
- **Absolute** — the full address from the drive root: `X:\RAGNova\data\images\screenshot.png`. Works from anywhere. Unambiguous.
- **Relative** — the address from where you're currently standing: `data\images\screenshot.png`. Shorter, but only correct if you're standing in `X:\RAGNova`.

Most "file not found" errors you will hit this month are a relative path used from the wrong folder. When something can't be found, first ask: *where am I standing?* Type `dir` and find out.

> **Windows quirk worth knowing now:** Windows uses backslashes `\` in paths, while Mac/Linux and most Python code use forward slashes `/`. Python handles both on Windows, so don't panic when you see either in our code.

## A.2 Install VS Code (your editor)

**VS Code** (Visual Studio Code) is a free text editor from Microsoft, built for writing code. It is not "Visual Studio" — different, much heavier product. You want **VS Code**.

Why an editor rather than Notepad: it colours your code so mistakes are visible, it flags errors before you run anything, it has a terminal built in so you never switch windows, and it previews the Markdown documents you're reading right now.

**Steps:**

1. Go to **https://code.visualstudio.com** and click the big Download button.
2. Run the downloaded `.exe`.
3. **On the "Select Additional Tasks" screen, tick these boxes:**
   - ✅ *Add "Open with Code" action to Windows Explorer file context menu*
   - ✅ *Add "Open with Code" action to Windows Explorer directory context menu*
   - ✅ *Add to PATH* ← this one matters most; it lets you type `code .` in a terminal
4. Finish, and launch VS Code.

### Open the project

In VS Code: **File → Open Folder…** → navigate to `X:\RAGNova` → **Select Folder**. If it asks "Do you trust the authors of the files in this folder?", click **Yes, I trust the authors** (it's your own folder).

You now see the file tree on the left. This is your project.

### Read these documents properly

The `.md` files are **Markdown** — plain text with light formatting marks (`#` for a heading, `|` for tables, `**bold**`). Reading the raw text is unpleasant. Reading the *rendered* version is pleasant.

**In VS Code: open any `.md` file, then press `Ctrl + Shift + V`.** (macOS: `Cmd + Shift + V`.) You get a clean, formatted, scrollable document with working tables and clickable links.

Do this now with this file. Genuinely — it makes the next 13 chapters far less painful.

### VS Code's built-in terminal

Press ``Ctrl + ` `` (the backtick key, top-left under `Esc`). A terminal opens *at the bottom of VS Code, already standing in your project folder*. Use this instead of the separate PowerShell window from A.1 — it saves a `cd` every time.

### Two extensions to install

Click the **Extensions** icon in the left bar (four squares), search, click Install:

1. **Python** (by Microsoft) — syntax highlighting, error checking, running code with one click.
2. **Markdown All in One** — better preview and table editing for our docs.

## A.3 Install Python

**Python** is the programming language this project is written in. Installing "Python" means installing the program that reads `.py` files and executes them (the *interpreter*).

**Use Python 3.11.** Not 3.12, not 3.13, not the version in the Microsoft Store. Reason: machine-learning libraries publish prebuilt packages per Python version, and they lag months behind new releases. On 3.13 you will hit install errors that have nothing to do with your code and everything to do with version mismatch. 3.11 is the boring, everything-works choice.

**Steps:**

1. Go to **https://www.python.org/downloads/release/python-3119/**
2. Scroll to the bottom, download **Windows installer (64-bit)**.
3. Run it. **On the very first screen, before clicking anything else:**

   ### ⚠️ TICK THE BOX: "Add python.exe to PATH"

   It is a small unticked checkbox at the bottom of the first screen. If you miss it, your terminal will say `'python' is not recognized` forever, and the fix is uninstalling and reinstalling. Every beginner misses this box. Do not be every beginner.

4. Click **Install Now**. Wait.
5. If offered "Disable path length limit" at the end, click it. Yes.

> **macOS:** download the macOS 64-bit universal2 installer from the same page. There is no PATH checkbox — it's handled for you. Note that Macs ship with an old Python; always type `python3`, not `python`.

### Verify it worked

**Close every terminal window and open a fresh one** (PATH changes only apply to newly-opened terminals — this trips people up constantly). Then:

```bash
python --version
```

You want to see `Python 3.11.9`. If instead you see `'python' is not recognized...`, see the troubleshooting table in Part E.

Now check `pip`, Python's package installer:

```bash
pip --version
```

### What pip actually is

You will almost never write everything from scratch. Other people have written and published reusable code — a **package** or **library**. `pip` downloads and installs them from a public repository called **PyPI**.

```bash
pip install requests
```

That one command downloads a library for fetching web pages and makes it available to your programs. In Chapter 5 we run one `pip install` that pulls in everything RAGNova needs.

**Library vs package vs module** — used loosely and interchangeably. A *module* is one `.py` file; a *package* is a folder of modules; a *library* is a package published for others to use. Nobody will correct you.

## A.4 Virtual environments: the one habit that saves you a week

Here is a problem you will otherwise meet painfully. Project A needs version 1.0 of some library. Project B needs version 2.0. Install both globally and they overwrite each other — one project breaks, mysteriously, and fixing it breaks the other.

A **virtual environment** (venv) is a private folder holding one project's own copy of Python and its own libraries. Projects stop interfering. If everything goes wrong, you delete the folder and rebuild in two minutes instead of debugging for two days.

**We create one in Chapter 5**, but understand the three commands now:

```bash
python -m venv .venv
```
Creates a folder named `.venv` inside your project holding a private Python. Done once, ever.

```bash
.\.venv\Scripts\Activate.ps1
```
**Activates** it. Your prompt changes to show `(.venv)` at the front. That prefix is your proof it worked — from now on, `pip install` installs *into this project only*.

> **macOS/Linux:** `source .venv/bin/activate`

```bash
deactivate
```
Leaves the environment.

**The rule, and the single most common source of "but I installed it!" confusion:** you must activate the venv **every time you open a new terminal**. It is not permanent. No `(.venv)` in your prompt means you are outside it, and your libraries appear to have vanished.

> **PowerShell may refuse to run the activate script**, saying *"running scripts is disabled on this system."* This is a Windows security default, not a broken install. Fix it once by running this in PowerShell:
>
> ```bash
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
>
> This allows scripts you wrote locally to run, while still requiring downloaded scripts to be signed. It applies to your user account only and does not require admin rights. Answer `Y` when prompted.

## A.5 Write and run your first Python file

Proof that everything above worked.

In VS Code: **File → New File**, save it as `hello.py` inside `X:\RAGNova`. Type:

```python
print("RAGNova setup works")

numbers = [3, 1, 4, 1, 5]
print("Sum:", sum(numbers))
print("Largest:", max(numbers))
```

Save (`Ctrl + S`). In the VS Code terminal (``Ctrl + ` ``):

```bash
python hello.py
```

Expected output:

```
RAGNova setup works
Sum: 14
Largest: 5
```

If you see that, your machine is ready. Delete `hello.py` afterwards — it was only a smoke test.

**Never written Python before?** §A.6 below is a complete primer covering exactly what this project uses — nothing more. Budget two evenings.

---

## A.6 Python primer — everything RAGNova needs, and nothing it doesn't

> **Scope promise.** This section teaches the *entire* subset of Python used across all thirteen chapters. We use no async, no decorators, no metaclasses, no inheritance hierarchies, no generators beyond comprehensions. If it isn't here, we don't use it. Work through it once and you can read and modify every line of code in this project.
>
> **Every example uses RAGNova's real data** — chunks, embeddings, metadata — so this doubles as a preview of Chapters 6–10.

### A.6.0 How to follow along

Two ways to run code. Use both.

**The REPL** (Read-Eval-Print Loop) — for quick experiments. In a terminal, type `python` alone:

```
PS X:\RAGNova> python
Python 3.11.9 ...
>>>
```

The `>>>` prompt runs one line at a time and prints the result immediately. Type `exit()` to leave. Perfect for "what does this do?" questions.

**A scratch file** — for anything longer. Make `scratch.py` in VS Code, write code, save, and run `python scratch.py`. Keep this file all week; delete it before submission.

**Type every example yourself.** Do not copy-paste. Typing produces the small errors that teach you what the error messages mean, which is half the skill.

---

### A.6.1 Variables and types

A variable is a name pointing at a value. No declaration, no type keyword — just assign.

```python
filename = "notice.pdf"      # str   — text
page_number = 2              # int   — whole number
similarity = 0.87            # float — decimal number
is_indexed = True            # bool  — True or False
```

Python figures out the type. Check it with `type()`:

```python
print(type(similarity))      # <class 'float'>
```

**Naming rules:** letters, digits, underscores; no starting digit; case-sensitive (`Page` ≠ `page`). **Convention:** `lower_case_with_underscores` for variables and functions. Follow it — our whole codebase does.

Types matter more than beginners expect:

```python
"2" + "3"      # "23"   — string concatenation
2 + 3          # 5      — arithmetic
"2" + 3        # TypeError: can only concatenate str (not "int") to str
```

That `TypeError` will happen to you. It means you mixed text and numbers. Convert explicitly with `int()`, `float()`, or `str()`:

```python
int("2") + 3       # 5
str(2) + "3"       # "23"
```

### A.6.2 Strings and f-strings

Text. Single or double quotes, identical meaning.

```python
source = "data/documents/notice.pdf"

len(source)                 # 28   — number of characters
source.upper()              # "DATA/DOCUMENTS/NOTICE.PDF"
source.lower()
source.strip()              # remove leading/trailing whitespace
source.replace("/", "\\")   # swap characters
source.endswith(".pdf")     # True
source.startswith("data")   # True
"notice" in source          # True  — substring check
```

**`.split()` and `.join()` are the two you will use most in this project**, because chunking is built from them:

```python
text = "the submission deadline is 21st August"

words = text.split()        # ['the','submission','deadline','is','21st','August']
                            # splits on whitespace by default
back = " ".join(words)      # "the submission deadline is 21st August"

"a,b,c".split(",")          # ['a','b','c'] — split on a specific character
```

**f-strings** build text containing values. Put `f` before the quote, and expressions inside `{}`:

```python
page = 2
score = 0.8734

print(f"Found on page {page} with score {score}")
# Found on page 2 with score 0.8734

print(f"Score: {score:.2f}")        # Score: 0.87   — 2 decimal places
print(f"Score: {score:.1%}")        # Score: 87.3%  — as a percentage
```

Use f-strings everywhere. The older `%` and `.format()` styles exist in tutorials; ignore them.

**Multi-line strings** use triple quotes — we use these constantly for LLM prompts in Chapter 10:

```python
prompt = """Answer the question using ONLY the context below.
If the context does not contain the answer, say so.

Context:
{context}
"""
```

### A.6.3 Lists

An ordered, changeable sequence. Square brackets.

```python
chunks = ["first chunk", "second chunk", "third chunk"]

chunks[0]          # "first chunk"   — counting starts at ZERO
chunks[2]          # "third chunk"
chunks[-1]         # "third chunk"   — negative counts from the end
chunks[-2]         # "second chunk"

len(chunks)        # 3
```

**Zero-based indexing** is the classic beginner trap: the first item is `[0]`, and the last item of a 3-item list is `[2]`. Asking for `chunks[3]` raises `IndexError: list index out of range`.

Changing lists:

```python
chunks.append("fourth chunk")     # add to the end
chunks.insert(0, "new first")     # insert at a position
chunks.remove("second chunk")     # remove by value
last = chunks.pop()               # remove and return the last item
chunks[0] = "replaced"            # overwrite by index
```

Useful built-ins:

```python
scores = [0.91, 0.45, 0.78, 0.62]

len(scores)            # 4
max(scores)            # 0.91
min(scores)            # 0.45
sum(scores)            # 2.76
sum(scores)/len(scores)  # 0.69 — the average
sorted(scores)                       # [0.45, 0.62, 0.78, 0.91]
sorted(scores, reverse=True)         # [0.91, 0.78, 0.62, 0.45]  ← ranking results!
```

That last one is literally how we rank retrieval results in Chapter 10.

### A.6.4 Slicing — the operation chunking is built on

`list[start:end]` takes a section. **`start` is included, `end` is excluded.**

```python
words = ["a", "b", "c", "d", "e", "f"]

words[0:3]      # ['a','b','c']       — positions 0,1,2 — NOT 3
words[2:5]      # ['c','d','e']
words[:3]       # ['a','b','c']       — omitted start means 0
words[3:]       # ['d','e','f']       — omitted end means "to the end"
words[:]        # whole list (a copy)
words[-2:]      # ['e','f']           — last two
```

The end-exclusive rule looks fussy but makes ranges join cleanly: `words[0:3]` and `words[3:6]` together cover everything, with no overlap and no gap.

Slicing works on strings too:

```python
"notice.pdf"[:6]     # "notice"
"notice.pdf"[-4:]    # ".pdf"
```

**Why this matters:** splitting a document into overlapping chunks is nothing more than repeated slicing of a word list. You will write that function in Exercise 2.

### A.6.5 Dictionaries — how RAGNova stores metadata

A dictionary maps **keys** to **values**. Curly braces, `key: value` pairs. This is the single most important structure in the project, because **every chunk's provenance metadata is a dictionary** (Chapter 1 §1.8).

```python
chunk = {
    "chunk_id": "notice_pdf__p2__c003",
    "source": "data/documents/notice.pdf",
    "modality": "pdf",
    "page": 2,
    "text": "...submission deadline is 21st August...",
}
```

Reading and writing:

```python
chunk["page"]                 # 2
chunk["page"] = 3             # change a value
chunk["score"] = 0.87         # add a NEW key just by assigning

chunk["author"]               # KeyError — the key doesn't exist
chunk.get("author")           # None — no crash
chunk.get("author", "unknown")  # "unknown" — supply a default
```

**Use `.get()` when a key might be missing.** Audio chunks have `start_s`; PDF chunks don't. `.get()` prevents crashes on that difference — a real bug you would otherwise hit in Chapter 10.

Inspecting:

```python
"page" in chunk               # True — check a key exists
chunk.keys()                  # all key names
chunk.values()                # all values
chunk.items()                 # key-value pairs, for looping
```

**Lists of dictionaries** are the shape of nearly all our data — a retrieval result set is exactly this:

```python
results = [
    {"source": "notice.pdf",  "page": 2, "score": 0.91},
    {"source": "syllabus.pdf", "page": 7, "score": 0.78},
    {"source": "lecture3.mp3", "start_s": 872.4, "score": 0.65},
]

results[0]["source"]          # "notice.pdf"  — index the list, then the key
```

Note this line carefully. `results[0]` gets the first dictionary; `["source"]` gets a value from it. Chained access like this is everywhere in our code.

### A.6.6 Tuples and sets (brief — we use these lightly)

**Tuple** — like a list, but unchangeable. Round brackets. Used for fixed pairs:

```python
dimensions = (384, 512)       # text dims, image dims
start, end = (12.4, 18.9)     # "unpacking" — two variables at once
```

Whisper returns timestamps as tuples like this in Chapter 9.

**Set** — unordered, no duplicates. Useful for de-duplication:

```python
sources = ["a.pdf", "b.pdf", "a.pdf"]
unique = set(sources)         # {'a.pdf', 'b.pdf'}
list(unique)                  # back to a list
```

Chapter 10 uses a set to avoid citing the same document twice.

### A.6.7 Conditionals: `if` / `elif` / `else`

```python
score = 0.87

if score > 0.8:
    print("strong match")
elif score > 0.5:
    print("weak match")
else:
    print("probably irrelevant")
```

Note the **colon** at the end of each condition line, and the **indentation** of the body. Both are mandatory — see §A.6.18.

Comparison and logic operators:

```python
a == b        # equal          ← two equals signs. ONE means "assign"
a != b        # not equal
a > b, a < b, a >= b, a <= b

score > 0.5 and modality == "pdf"     # both must be true
score > 0.9 or modality == "image"    # either
not is_indexed                        # flips True/False
```

`=` versus `==` is a classic beginner bug. `=` assigns a value; `==` asks a question.

A real example from our pipeline:

```python
if filename.endswith(".pdf"):
    parse_pdf(filename)
elif filename.endswith(".docx"):
    parse_docx(filename)
elif filename.endswith((".png", ".jpg", ".jpeg")):
    parse_image(filename)
elif filename.endswith((".wav", ".mp3")):
    parse_audio(filename)
else:
    print(f"Skipping unsupported file: {filename}")
```

That is essentially Chapter 6's file dispatcher.

### A.6.8 Loops

**`for`** repeats over each item in a collection:

```python
for chunk in chunks:
    print(chunk)
```

Read it as "for each chunk in chunks." The variable name is yours to choose.

**`enumerate()`** gives you the position as well — needed for numbering citations `[1]`, `[2]`:

```python
for i, chunk in enumerate(results):
    print(f"[{i+1}] {chunk['source']} page {chunk['page']}")

# [1] notice.pdf page 2
# [2] syllabus.pdf page 7
```

`i+1` because enumerate starts at 0 but humans count from 1. (You can also write `enumerate(results, start=1)`.)

**`zip()`** walks two lists together — used when pairing chunks with their embeddings:

```python
for text, vector in zip(chunk_texts, embeddings):
    store(text, vector)
```

**`range()`** counts:

```python
for i in range(5):        # 0,1,2,3,4
    print(i)

range(2, 6)               # 2,3,4,5
range(0, 100, 10)         # 0,10,20,...,90  — third value is the step
```

**Looping a dictionary:**

```python
for key, value in chunk.items():
    print(f"{key}: {value}")
```

**`while`** repeats until a condition stops being true — we use exactly one, in the chunker:

```python
start = 0
while start < len(words):
    ...
    start = start + chunk_size - overlap
```

⚠️ If the condition never becomes false, the program hangs forever. Press `Ctrl + C` to stop a runaway program. Always make sure something inside the loop changes the variable being tested.

**`break` and `continue`:**

```python
for chunk in chunks:
    if chunk == "":
        continue        # skip this one, go to the next
    if found_answer:
        break           # stop looping entirely
```

### A.6.9 Functions

A function packages reusable code, gives it a name, and takes inputs.

```python
def format_citation(source, page):
    return f"{source}, page {page}"

label = format_citation("notice.pdf", 2)
print(label)        # notice.pdf, page 2
```

Breaking that down: `def` starts the definition, `format_citation` is the name, `(source, page)` are **parameters** (inputs), the colon and indentation mark the body, and `return` sends a value back to whoever called it.

**Default values** make parameters optional:

```python
def chunk_text(text, chunk_size=300, overlap=50):
    ...

chunk_text(document)                    # uses 300 / 50
chunk_text(document, chunk_size=150)    # override just one
```

Naming the argument (`chunk_size=150`) is called a **keyword argument**. Prefer it when there are several parameters — `chunk_text(doc, 150, 20)` is unreadable six months later.

A function without `return` gives back `None`. Functions that only *do* something (write a file, print) legitimately return nothing.

**Docstrings** — a string on the first line of a function, describing it. **Our project requires one on every function** (Objective O7, documentation):

```python
def chunk_text(text, chunk_size=300, overlap=50):
    """Split text into overlapping word chunks.

    Args:
        text: The full document text.
        chunk_size: Words per chunk.
        overlap: Words repeated between consecutive chunks,
                 so sentences spanning a boundary aren't lost.

    Returns:
        A list of chunk strings.
    """
    ...
```

### A.6.10 List comprehensions

A compact way to build a list from another list. Extremely common in ML code — you must be able to *read* these even if you prefer writing loops.

```python
# The long way
long_chunks = []
for c in chunks:
    if len(c) > 100:
        long_chunks.append(c)

# The comprehension — identical result, one line
long_chunks = [c for c in chunks if len(c) > 100]
```

Read it right-to-left-ish: *"for each `c` in chunks, if it's longer than 100, keep `c`."*

```python
# Transform every item
upper = [c.upper() for c in chunks]

# Pull one field out of a list of dicts  ← we do this constantly
sources = [r["source"] for r in results]

# Transform and filter together
good = [r["source"] for r in results if r["score"] > 0.7]
```

The same syntax with curly braces builds a dictionary:

```python
scores_by_source = {r["source"]: r["score"] for r in results}
```

### A.6.11 `None`, and what counts as false

`None` means "no value." Different from `0`, `False`, or `""`.

```python
start_s = None      # a PDF chunk has no timestamp

if start_s is None:
    print("not an audio chunk")
```

Use `is None` / `is not None`, not `== None`. Both work; `is` is the convention.

**Falsy values** — these all behave as false in an `if`:

```python
if not text:        # true when text is "" or None
    return []
```

Falsy: `False`, `None`, `0`, `""`, `[]`, `{}`. Everything else is truthy. This makes guard clauses tidy:

```python
def chunk_text(text, chunk_size=300, overlap=50):
    if not text:
        return []       # empty input, empty output — no crash later
    ...
```

### A.6.12 Imports — using other people's code

```python
import math                          # whole module
math.sqrt(16)                        # 4.0

from pathlib import Path             # one name from a module
Path("data/documents")

import numpy as np                   # with a short alias
np.array([1, 2, 3])

from sentence_transformers import SentenceTransformer   # a real one from Ch 7
```

`import x` then `x.thing()`. `from x import thing` then `thing()` directly. Aliases (`as np`) are conventions you'll see in every ML codebase — `np` for numpy, `pd` for pandas.

**Put all imports at the top of the file.** Standard-library imports first, then third-party, then your own project modules — with a blank line between groups:

```python
import math
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from src.core.schemas import Chunk
```

`ModuleNotFoundError` means either the library isn't installed, or your virtual environment isn't activated (§A.4). Check for `(.venv)` in your prompt before reaching for `pip install`.

### A.6.13 File paths with `pathlib`

Handling paths as plain strings breaks across Windows and Mac. `pathlib` handles it properly:

```python
from pathlib import Path

data_dir = Path("data/documents")
file = data_dir / "notice.pdf"        # the / operator joins paths

file.exists()          # True/False
file.name              # "notice.pdf"
file.stem              # "notice"        — name without extension
file.suffix            # ".pdf"          — extension only
file.parent            # Path("data/documents")
```

**Listing files** — this is how Chapter 6 finds everything to ingest:

```python
for pdf in Path("data/documents").glob("*.pdf"):
    print(pdf.name)

for f in Path("data").rglob("*"):     # rglob = recursive, all subfolders
    if f.is_file():
        print(f)
```

`file.suffix.lower()` is the reliable way to dispatch by file type — it handles `.PDF` as well as `.pdf`.

### A.6.14 Reading and writing files

```python
# Read
with open("notes.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Write (overwrites)
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("some text")
```

**Always use `with`.** It guarantees the file is closed afterwards, even if an error occurs. Forgetting to close files causes "file is in use" errors on Windows.

**Always pass `encoding="utf-8"`.** Windows otherwise defaults to a legacy encoding that mangles accented characters, curly quotes, and anything non-English — a genuinely annoying bug to track down later.

JSON, which we use for saving metadata and transcripts:

```python
import json

with open("chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2)      # Python list/dict → JSON file

with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)               # JSON file → Python list/dict
```

`indent=2` makes the file human-readable, which matters when you're debugging what got indexed.

### A.6.15 Handling errors with `try` / `except`

Some files are corrupt, password-protected, or empty. Without handling, one bad file stops the whole ingestion run — which is exactly what you don't want after waiting twenty minutes.

```python
for file in files:
    try:
        text = parse_pdf(file)
    except Exception as e:
        print(f"Skipping {file.name}: {e}")
        continue
```

`try` runs the risky code; if it raises an error, `except` catches it and the program keeps going. `as e` captures the error object so you can print what actually went wrong.

Catching specific errors is better practice where you know what to expect:

```python
try:
    page = chunk["page"]
except KeyError:
    page = None
```

⚠️ **Never write a bare `except: pass`.** It silently swallows every error including your own typos, and you will lose hours wondering why nothing indexed. Always at least print the error.

### A.6.16 Classes — enough to read them, plus the one we write

You will *use* classes constantly (every library gives you objects) but you barely need to *write* them.

**Using** a class — create an instance, call its methods:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")   # create an instance
vector = model.encode("some text")                # call a method on it
```

That's the pattern for nearly every library in this project.

**Writing** one — we define exactly one kind, our chunk schema, and we use a `dataclass`, which is the easy way:

```python
from dataclasses import dataclass

@dataclass
class Chunk:
    chunk_id: str
    source: str
    modality: str
    text: str
    page: int = None
    start_s: float = None

c = Chunk(
    chunk_id="notice_pdf__p2__c003",
    source="data/documents/notice.pdf",
    modality="pdf",
    text="...deadline is 21st August...",
    page=2,
)

print(c.source)     # dot access, not ["brackets"]
print(c.page)       # 2
```

The `@dataclass` line above the class automatically writes the boilerplate for you. **Why bother instead of a plain dictionary?** A typo like `chunk["surce"]` fails silently at runtime with `KeyError`; `c.surce` is flagged by VS Code as you type. When three people work on separate pipelines that must produce identically-shaped data (Chapter 4's team split), a shared dataclass is the contract that keeps them compatible. We define this in Chapter 5.

### A.6.17 Type hints

You'll see annotations like this throughout our code:

```python
def chunk_text(text: str, chunk_size: int = 300) -> list[str]:
    ...
```

`text: str` says text should be a string; `-> list[str]` says the function returns a list of strings.

**Python does not enforce these** — they're documentation that VS Code reads to autocomplete and to warn you. Adding them takes five seconds and prevents real bugs. Common ones:

```python
str, int, float, bool
list[str]              # list of strings
dict[str, float]       # dict with string keys, float values
list[dict]             # list of dictionaries  ← our results shape
Chunk | None           # either a Chunk or None
```

### A.6.18 Indentation and the errors it causes

**Python uses indentation to define structure.** Other languages use `{ }`; Python uses whitespace. This is not cosmetic — it changes what your program does.

```python
for chunk in chunks:
    print(chunk)        # INSIDE the loop — runs for every chunk
print("done")           # OUTSIDE — runs once, at the end
```

Rules: **4 spaces** per level (VS Code's Tab key does this), consistently. Never mix tabs and spaces — VS Code shows this as `IndentationError: unindent does not match any outer indentation level`.

The three syntax errors you'll actually meet:

| Error | Cause |
|---|---|
| `IndentationError: expected an indented block` | You wrote `if x:` or `def f():` and didn't indent the next line |
| `SyntaxError: invalid syntax` pointing at a line that looks fine | Missing colon on the line *above*, or an unclosed `(` / `[` / `"` on a previous line — **always check the line before the one reported** |
| `IndentationError: unindent does not match...` | Mixed tabs and spaces |

### A.6.19 Debugging with `print()`

Professional debuggers exist; you will use `print()` for 90% of this project and that's fine.

```python
print(f"DEBUG chunks made: {len(chunks)}")
print(f"DEBUG first chunk: {chunks[0][:100]}")     # first 100 characters
print(f"DEBUG top score: {results[0]['score']:.3f}")
```

The method that solves almost everything: **when output is wrong, print the value at each stage until you find the first place it stops being what you expected.** Wrong retrieval results? Print the query, then the query's vector length, then how many chunks are in the database, then the raw scores. The bug is at the first surprise.

Two more inspection tools:

```python
type(x)      # what kind of thing is this?
len(x)       # how many items? (works on str, list, dict)
```

`len()` in particular catches the most common silent failure in this project — an empty list where you expected chunks means parsing produced nothing.

---

### A.6.20 Exercises — do these before Chapter 1

Three exercises. **Each one is a real function you will need later**, written with only what's above. Attempt them before reading the solutions.

#### Exercise 1 — Cosine similarity in pure Python

Write `cosine_similarity(a, b)` for two lists of numbers. Verify it against Chapter 1 §1.5.3: `[2,1,0]` vs `[3,1,0]` should give ≈ 0.990, and `[2,1,0]` vs `[0,1,4]` should give ≈ 0.108.

<details>
<summary>Solution</summary>

```python
import math

def dot_product(a: list[float], b: list[float]) -> float:
    """Multiply matching positions and sum the results."""
    return sum(x * y for x, y in zip(a, b))

def magnitude(v: list[float]) -> float:
    """Length of a vector: square, sum, square-root."""
    return math.sqrt(sum(x * x for x in v))

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine of the angle between two vectors. 1.0 = identical direction."""
    return dot_product(a, b) / (magnitude(a) * magnitude(b))


A = [2, 1, 0]
B = [3, 1, 0]
C = [0, 1, 4]

print(f"cat vs kitten:  {cosine_similarity(A, B):.3f}")   # 0.990
print(f"cat vs database: {cosine_similarity(A, C):.3f}")  # 0.108
```

You have now implemented, from scratch, the operation every vector database performs millions of times per second. It is genuinely this simple — real systems just do it very fast, over 384 dimensions, using the tricks in Chapter 1 §1.6.

</details>

#### Exercise 2 — A chunker with overlap

Write `chunk_text(text, chunk_size=300, overlap=50)` that splits text into lists of words of `chunk_size`, where consecutive chunks share `overlap` words. Return a list of strings.

*Why overlap?* A sentence landing exactly on a boundary would otherwise be cut in half, and neither fragment would retrieve well. Overlap guarantees every sentence appears whole in at least one chunk. Chapter 6 explores this properly.

Test with a paragraph, using small numbers like `chunk_size=10, overlap=3` so you can see the result.

<details>
<summary>Solution</summary>

```python
def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Split text into overlapping word chunks.

    Args:
        text: The full document text.
        chunk_size: Words per chunk.
        overlap: Words repeated between consecutive chunks, so sentences
                 spanning a boundary survive intact in at least one chunk.

    Returns:
        A list of chunk strings. Empty list if text is empty.
    """
    if not text:
        return []
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap

    return chunks


sample = " ".join(f"word{i}" for i in range(25))
for i, c in enumerate(chunk_text(sample, chunk_size=10, overlap=3), start=1):
    print(f"[{i}] {c}")
```

Note the two guards at the top: empty input returns an empty list rather than crashing later, and `overlap >= chunk_size` is rejected because it would make `start` move backwards — an infinite loop. Defensive guards like these are what separate code that survives a real corpus from code that works once on your test file.

</details>

#### Exercise 3 — Rank and format retrieval results

Given this list, write code that keeps only results scoring above 0.7, sorts them best-first, and prints them as numbered citations.

```python
results = [
    {"source": "notice.pdf",   "page": 2,        "score": 0.91},
    {"source": "syllabus.pdf", "page": 7,        "score": 0.78},
    {"source": "lecture3.mp3", "start_s": 872.4, "score": 0.65},
    {"source": "poster.png",                     "score": 0.83},
]
```

Expected output:

```
[1] notice.pdf (page 2) — 0.91
[2] poster.png — 0.83
[3] syllabus.pdf (page 7) — 0.78
```

Note that `poster.png` has no `page` and `lecture3.mp3` has no `page` either — handle missing keys without crashing.

<details>
<summary>Solution</summary>

```python
results = [
    {"source": "notice.pdf",   "page": 2,        "score": 0.91},
    {"source": "syllabus.pdf", "page": 7,        "score": 0.78},
    {"source": "lecture3.mp3", "start_s": 872.4, "score": 0.65},
    {"source": "poster.png",                     "score": 0.83},
]

good = [r for r in results if r["score"] > 0.7]
good = sorted(good, key=lambda r: r["score"], reverse=True)

for i, r in enumerate(good, start=1):
    page = r.get("page")
    location = f" (page {page})" if page is not None else ""
    print(f"[{i}] {r['source']}{location} — {r['score']:.2f}")
```

Two new things worth naming. `key=lambda r: r["score"]` tells `sorted` *which value to sort by* — a `lambda` is just a tiny unnamed function, and this is the only place we use one. And `r.get("page")` returns `None` instead of raising `KeyError` for the image and audio results, which is precisely the situation §A.6.5 warned about.

This is, in miniature, exactly what Chapter 10 does before handing results to the LLM.

</details>

---

### A.6.21 Cheat sheet

| Task | Code |
|---|---|
| Format text with values | `f"page {n} score {s:.2f}"` |
| Split into words / rejoin | `text.split()` / `" ".join(words)` |
| Slice a list | `words[start:end]` (end excluded) |
| Last item | `items[-1]` |
| Safe dictionary read | `d.get("key", default)` |
| Add a dictionary key | `d["new"] = value` |
| Loop with a counter from 1 | `for i, x in enumerate(items, start=1):` |
| Loop two lists together | `for a, b in zip(list1, list2):` |
| Filter a list | `[x for x in items if condition]` |
| Pull a field from dicts | `[d["field"] for d in items]` |
| Sort by a field, best first | `sorted(items, key=lambda d: d["score"], reverse=True)` |
| Read a text file | `with open(p, "r", encoding="utf-8") as f: f.read()` |
| Save/load JSON | `json.dump(obj, f, indent=2)` / `json.load(f)` |
| Join a path | `Path("data") / "file.pdf"` |
| Find files by type | `Path("data").glob("*.pdf")` |
| File extension | `p.suffix.lower()` |
| Survive a bad file | `try: ... except Exception as e: print(e); continue` |
| Check emptiness | `if not items:` |
| Inspect while debugging | `print(f"DEBUG {len(x)=} {type(x)=}")` |

### A.6.22 What we deliberately skip

So you don't worry about gaps: this project uses **no** `async`/`await`, no decorators (beyond `@dataclass`), no inheritance or abstract classes, no generators or `yield`, no metaclasses, no threading, no regular expressions (beyond possibly one trivial pattern), no `*args`/`**kwargs` in code you write.

If a tutorial you find online leads with those topics, it's aimed at a different goal. Everything above is sufficient for all thirteen chapters.

---

# Part B — Concepts you need so Chapter 1 doesn't lose you

Chapter 1 uses these words from its first paragraph. Here they are from zero.

## B.1 What a neural network actually is

Forget brains. A neural network is **a very large mathematical function with adjustable numbers inside it.**

It takes numbers in, multiplies and adds them through many layers, and produces numbers out. That is the whole object.

```
input numbers → [multiply by weights, add, apply a simple curve] × many layers → output numbers
```

The adjustable numbers are called **weights** or **parameters**. Initially they are random, so the output is garbage.

**Training** is the process of fixing that:
1. Feed in an example whose correct answer you know.
2. Compare the network's output to the correct answer. The gap is the **loss**.
3. Nudge every weight slightly in the direction that would have made the loss smaller.
4. Repeat, billions of times, over billions of examples.

After enough repetitions the weights encode genuine structure about the data. That's it. There is no comprehension step hidden anywhere — just an enormous number of small numeric adjustments that add up to useful behaviour.

**Inference** is using the trained network: weights are frozen, numbers go in, answer comes out. **Everything RAGNova does is inference.** We never train anything — training a language model costs millions of dollars and months of GPU time. We download models other people trained and use them. That is normal, professional practice, not a shortcut.

**A "model"** = the architecture (the shape of the function) + the weights (the learned numbers). When Chapter 1 says a 3B model is ~2 GB on disk, that file is the weights.

## B.2 Why everything becomes numbers

Neural networks only do arithmetic. So every input must first become numbers:

| Input | Becomes |
|---|---|
| Text | Token IDs → then vectors of numbers (Ch 1 §1.1.2) |
| Image | Pixel brightness values, e.g. 224 × 224 × 3 colour channels |
| Audio | Amplitude samples, usually converted to a spectrogram (Ch 1 §1.7.6) |

This is precisely *why* cross-modal search is possible at all. Once a picture and a sentence are both just lists of numbers, you can ask whether the two lists are similar — provided a model was trained to make them comparable. That single idea is the heart of Chapter 1 §1.7, and it is much less mysterious once you see that everything was numbers from the start.

## B.3 API, and why "local API" isn't a contradiction

An **API** (Application Programming Interface) is an agreed way for one program to ask another program to do something.

You probably associate APIs with the internet — your app calls Google's servers. But an API is just a contract about how to send a request and receive a response. **It does not require a network.**

Ollama (Chapter 5) runs an AI model as a background program on *your* computer and exposes a local API at `http://localhost:11434`. `localhost` means "this same machine." Our Python code sends the question there and gets the answer back — the request never leaves your laptop, never touches a router, and works in airplane mode.

**This is what "offline" means in our project.** Not "no APIs." It means every program in the conversation is running on your own hardware.

## B.4 JSON

**JSON** is a plain-text format for structured data. You'll meet it constantly because our chunk metadata (Ch 1 §1.8) is written as JSON:

```json
{
  "source": "data/documents/notice.pdf",
  "modality": "pdf",
  "page": 2,
  "text": "...submission deadline is 21st August..."
}
```

Curly braces hold a set of `"name": value` pairs. Values can be text (in quotes), numbers, `true`/`false`, `null`, lists in square brackets, or nested objects. That's the entire format. It maps almost exactly onto a Python dictionary, which is why it's everywhere.

## B.5 Repository, and what "commit" means

A **repository** ("repo") is just a project folder tracked by version-control software — nearly always **Git**.

**Git** records snapshots of your project over time. Each snapshot is a **commit**, with a message describing what changed. It lets you see history, undo mistakes, and — critically for a 3-person team — merge everyone's work without emailing zip files.

When Chapter 1 says "add it to the glossary and commit," it means: edit the file, then save a snapshot with a message like `docs: add HNSW to glossary`.

**Your team lead is managing Git for this project**, so you are not blocked on learning it. But learn `git add`, `git commit`, `git push`, and `git pull` during Days 1–4 — four commands, and they are how professional teams actually collaborate.

---

# Part C — The maths you actually need (and the maths you don't)

Chapter 1 §1.5.3 does a calculation. It looks like this:

```
                    A · B              Σ (Aᵢ × Bᵢ)
cos(θ) = ───────────────────── = ────────────────────────
            ‖A‖ × ‖B‖            √(ΣAᵢ²) × √(ΣBᵢ²)
```

If that made your stomach drop, read this part. It is entirely school-level, and it decodes completely in about ten minutes.

**What you do NOT need for this project:** calculus, matrix algebra, probability theory, statistics beyond averages. We are *using* trained models, not deriving them. If you can do arithmetic and square roots, you can follow every calculation in these thirteen chapters.

## C.1 A vector is a list of numbers

That's it. `[2, 1, 0]` is a 3-dimensional vector. `[0.021, -0.153, ..., 0.44]` with 384 entries is a 384-dimensional vector.

"384-dimensional" sounds alarming but means nothing more than *a list with 384 numbers in it*. You cannot picture it, and you do not need to — every operation below works identically at 3 dimensions and at 384.

Picture 2D to build intuition: `[3, 4]` is an arrow from the origin going 3 right and 4 up. It has a **direction** and a **length**. Vectors in 384 dimensions have exactly those same two properties; there are just more numbers describing them.

## C.2 Σ (sigma) means "add all of these up"

`Σ` is the Greek capital sigma, and it is shorthand for a loop.

```
Σ Aᵢ    means:  A₁ + A₂ + A₃ + ... + Aₙ
```

The little `ᵢ` is just the position index — `Aᵢ` means "the i-th number in list A." So `A₁` is the first number, `A₂` the second.

In Python, `Σ Aᵢ` is literally:

```python
sum(A)
```

And `Σ (Aᵢ × Bᵢ)` — multiply matching pairs, then add the results — is:

```python
sum(a * b for a, b in zip(A, B))
```

Concretely, with `A = [2, 1, 0]` and `B = [3, 1, 0]`:

```
Σ (Aᵢ × Bᵢ) = (2×3) + (1×1) + (0×0) = 6 + 1 + 0 = 7
```

Notation decoded. It was a `for` loop the whole time.

## C.3 The dot product (`A · B`)

The operation you just did has a name: the **dot product**. Multiply matching positions, add everything up, get one single number.

```
A = [2, 1, 0]
B = [3, 1, 0]
A · B = 2×3 + 1×1 + 0×0 = 7
```

**Intuition worth carrying:** the dot product is large when two vectors have big values in the *same positions*, and small when their big values are in *different positions*. That is exactly why it measures agreement — and why, when embeddings encode meaning across positions, a large dot product means "similar meaning."

## C.4 Magnitude (`‖A‖`) — the length of a vector

The double bars mean **length** (also called magnitude or norm). It's Pythagoras, extended to any number of dimensions: square everything, add, take the square root.

```
‖A‖ = √(A₁² + A₂² + ... + Aₙ²) = √(Σ Aᵢ²)
```

For `A = [2, 1, 0]`:

```
‖A‖ = √(2² + 1² + 0²) = √(4 + 1 + 0) = √5 ≈ 2.236
```

Check it in 2D against Pythagoras: `[3, 4]` gives `√(9 + 16) = √25 = 5` — the familiar 3-4-5 triangle. Same formula, more terms.

## C.5 Putting it together: cosine similarity

Now the formula reads in plain English:

> **Take the dot product of A and B (how much they agree), then divide by both of their lengths (to cancel out how big they are). What remains is purely how much they point in the same direction.**

The dividing step is the important idea. Without it, a long document would score highly against everything simply for being long. Dividing by the lengths removes size from the comparison and leaves only direction — and in embedding space, **direction is meaning**.

The result always lands between −1 and 1:

| Value | Meaning |
|---|---|
| 1.0 | Identical direction — same meaning |
| ~0.7–0.9 | Strongly related |
| ~0.0 | Unrelated (perpendicular) |
| −1.0 | Opposite direction |

Now go back and read Chapter 1 §1.5.3. The worked example will be straightforward.

## C.6 Big-O notation: `O(N × d)` and `O(log N)`

Chapter 1 §1.6 uses these. They describe **how the time a task takes grows as the data grows** — not actual seconds, just the shape of the growth.

| Notation | Meaning | Real example |
|---|---|---|
| `O(N)` | Double the data → double the time | Reading every line of a file |
| `O(N × d)` | Time grows with data size × per-item cost | Comparing a query against all N vectors, each with d numbers |
| `O(log N)` | Data grows 1000× → time grows ~10× | Looking up a word in a dictionary by halving your search |
| `O(N²)` | Double the data → **four times** the time | Comparing every item against every other item |

That's the entire point of §1.6.2: brute-force vector search is `O(N × d)` and gets slow as your collection grows, while HNSW is roughly `O(log N)` and barely notices. Dictionary lookup versus reading the dictionary cover to cover.

## C.7 Softmax and probability, informally

Chapter 1 §1.1.3 says the model applies **softmax** to produce probabilities. All this means: take a list of raw scores, convert them into positive numbers that **add up to 1**, preserving the order (biggest score → biggest probability).

```
raw scores:     [3.2, 1.1, 0.4]
after softmax:  [0.79, 0.13, 0.08]   ← sums to 1.0
```

Why bother: a list summing to 1 can be read as "79% chance the next word is *deadline*, 13% chance it's *date*…" — which is exactly what lets the model sample a next token, and what **temperature** adjusts. Low temperature exaggerates the gaps (the top choice wins almost always → factual, repeatable). High temperature flattens them (more variety → creative, riskier). We use low temperature, for the reason given in Chapter 1 §1.1.3.

---

# Part D — Jargon decoder for Chapter 1

Terms Chapter 1 uses without pausing. The full glossary is [GLOSSARY.md](../GLOSSARY.md); these are the ones that specifically trip up first-time readers.

| You'll read | It means |
|---|---|
| **"weights"** | The learned numbers inside a model. The downloadable file *is* the weights. |
| **"the model file is 2 GB"** | The weights take 2 GB of disk. Loading the model copies most of that into RAM. |
| **"CPU-only, no GPU required"** | A GPU (graphics card) does the parallel arithmetic AI needs ~10–50× faster. We chose components small enough to run acceptably on an ordinary processor, because you don't have gaming laptops. |
| **"RAM"** | Working memory. Programs must fit in it while running. Full budget in Ch 1 §1.9.2 — this is why model size matters so much. |
| **"quantized" / "4-bit"** | Weights stored with less precision to shrink the file. `0.4172358` becomes one of 16 nearby values. Small accuracy cost, 4× smaller. This is the entire reason a laptop can run an LLM. |
| **"embedded database"** | Runs as a library *inside* your Python program. No server to install, no service to start. ChromaDB is embedded — which is why it's beginner-friendly. |
| **"pipeline"** | A sequence of processing steps where each one's output feeds the next. "Audio pipeline" = load file → transcribe → chunk → embed → store. |
| **"chunk"** | One small piece of a document (~300 words) after splitting. The unit we embed, store, retrieve, and cite. |
| **"index" (verb)** | Do the whole preparation pass over a file: parse → chunk → embed → store. "Index the corpus" = process everything once so queries are fast later. |
| **"index" (noun)** | The stored, searchable collection that results. |
| **"query"** | A search — the user's question, or the vector we search with. |
| **"top-K"** | The K best-matching results. We start with K = 5. |
| **"latency"** | How long something takes, measured end to end. |
| **"~/.cache/huggingface"** | A hidden folder in your user directory where downloaded models are stored. `~` means your home folder (`C:\Users\yourname`). Downloaded once, reused forever. |
| **"CTranslate2", "int8"** | An optimisation library and a number format. You do not need to understand these — they are why faster-whisper is fast. Use it and move on. |
| **"corpus"** | Your whole collection of files. Ours lives in `data/`. |
| **"gold set"** | Test questions where you already know the right answer, used to measure whether retrieval works. |

---

# Part E — When things go wrong

Every beginner hits several of these. None of them mean you did something stupid.

| Symptom | Cause | Fix |
|---|---|---|
| `'python' is not recognized as an internal or external command` | PATH box unticked during install, or terminal opened before installing | Close all terminals, open a fresh one. Still broken → re-run the Python installer, choose **Modify**, ensure "Add to PATH" is ticked |
| `'pip' is not recognized` | Same cause | Same fix. Workaround: use `python -m pip install ...` instead of `pip install ...` |
| `running scripts is disabled on this system` | PowerShell's default security policy blocking venv activation | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, answer `Y` (see A.4) |
| `ModuleNotFoundError: No module named 'x'` | Library not installed, **or** venv not activated | Check for `(.venv)` at the start of your prompt. Not there → activate it. There → `pip install x` |
| Installed a library, Python still can't find it | Installed into a different Python than the one running your code | Activate the venv *first*, then install. Verify with `python -m pip list` |
| VS Code underlines correct code in red | VS Code is using a different Python interpreter than your terminal | `Ctrl+Shift+P` → "Python: Select Interpreter" → choose the one inside `.venv` |
| `Permission denied` / `Access is denied` | File open in another program, or a protected location | Close the file elsewhere. Keep the project in `X:\RAGNova`, not in `C:\Program Files` |
| `FileNotFoundError` with a path that looks right | Relative path used from the wrong folder | `dir` to see where you're standing. Use an absolute path to confirm the file exists |
| Download stalls or fails partway | Slow/unstable connection — model files are large | Retry; most tools resume. Download overnight. Have one member share files by USB |
| Terminal appears frozen mid-install | It's working, just silent | Wait. Large installs can take 10+ minutes with no output. Do not press `Ctrl+C` |

### How to ask for help well

Whether you're asking a teammate, a professor, or an AI, include these four things and you'll get a real answer instead of twenty questions:

1. **The exact command you ran** (copy-paste it, don't retype from memory).
2. **The complete error message** (all of it — the useful line is usually the *last* one, not the first).
3. **What you expected** to happen.
4. **What you already tried.**

"It doesn't work" is unanswerable. "I ran `python ingest.py`, got `FileNotFoundError: data/documents/notes.pdf`, but the file is visibly there in VS Code" gets solved in one reply.

---

# Part F — Chapter 0 checklist

Tick every box before starting Chapter 1's theory.

**Computer setup**
- [ ] I can open a terminal and I know what the prompt is telling me
- [ ] I can navigate with `cd` and list files with `dir`
- [ ] VS Code is installed, with **Add to PATH** ticked
- [ ] I opened `X:\RAGNova` in VS Code and can see the file tree
- [ ] I can read `.md` files rendered with `Ctrl + Shift + V`
- [ ] The **Python** and **Markdown All in One** extensions are installed
- [ ] Python **3.11** is installed with **Add python.exe to PATH** ticked
- [ ] `python --version` prints `3.11.x` in a fresh terminal
- [ ] `pip --version` works
- [ ] I created, ran, and deleted `hello.py` successfully

**Python (§A.6)**
- [ ] I can create variables, and I know why `"2" + 3` is a `TypeError`
- [ ] I can build an f-string with a number formatted to 2 decimal places
- [ ] I can split text into words, slice the list, and join it back
- [ ] I know that lists start at index `0` and that `words[0:3]` excludes position 3
- [ ] I can read and write a dictionary, and I know when to use `.get()` instead of `[ ]`
- [ ] I can loop with `enumerate()` to produce numbering that starts at 1
- [ ] I can write a function with a default parameter, a docstring, and a `return`
- [ ] I can read a list comprehension and say what it does
- [ ] I know why `with open(...)` and `encoding="utf-8"` are non-negotiable
- [ ] I can wrap risky code in `try`/`except` so one bad file doesn't stop a run
- [ ] I finished **Exercise 1** (cosine similarity) and my numbers match Chapter 1 §1.5.3
- [ ] I finished **Exercise 2** (chunker with overlap) and understand why overlap exists
- [ ] I finished **Exercise 3** (rank and format results) without a `KeyError`

**Understanding**
- [ ] I can explain what a neural network is in one sentence, without saying "brain"
- [ ] I know the difference between training and inference, and which one we do
- [ ] I understand why a local API is still an API
- [ ] I can compute a dot product by hand
- [ ] I can compute a vector's magnitude by hand
- [ ] I know what `Σ` means and could write it as a Python loop
- [ ] I know what `O(log N)` is claiming, roughly

**Ready**
- [ ] I know that Chapter 0 ≠ Chapter 5, and that I'll install the AI libraries later
- [ ] I have started the `ollama pull llama3.2:3b` download, or scheduled it for tonight

---

**Next:** [Chapter 1 — Objective & Problem Identification](ch01-objective-and-problem-identification.md). Every term it uses is now either defined above or defined there. If you hit something undefined in Chapter 1, that is a **bug in our documentation** — add it to [GLOSSARY.md](../GLOSSARY.md) and tell the team.
