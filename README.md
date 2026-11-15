# SEN 304 – Software Testing and Quality Assurance (TMA)

**Emmanuel Onyo – 2023/B/SENG/0242**

A shopping-cart / checkout module for a Nigerian online store (discount tiers, coupon, 7.5% VAT).

```
SEN304/
├── buggy/
│   ├── cart_buggy.py      # Part A: 7 intentional bugs (syntax, runtime, logical)
│   └── debug_session.py   # driver used with VS Code breakpoints
├── src/
│   └── cart.py            # fixed version with exception handling
├── tests/
│   └── test_cart.py       # Part B: 45 PyTest tests (EP, BVA, statement, branch, path)
├── evidence/              # real outputs captured while building this
├── .vscode/launch.json    # debug configurations
├── .coveragerc  pytest.ini  requirements.txt
```

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   (source .venv/bin/activate on Mac/Linux)
pip install -r requirements.txt
```
In VS Code install the **Python** and **Python Debugger** extensions.

## Part A – screenshots to take (VS Code)
1. Open `buggy/cart_buggy.py` and run it → **screenshot the SyntaxError** (BUG-01) in the terminal and the red squiggle in the editor.
2. Add the missing `:` on `def discount_rate(amount)`. Save.
3. Set the breakpoints listed at the top of `buggy/debug_session.py` (click left of the line number).
4. Run and Debug (Ctrl+Shift+D) → choose **"Debug buggy cart"** → F5.
5. At each breakpoint, add the watch expressions to the **WATCH** panel, then step with **F10 (Step Over)** / **F11 (Step Into)**. Screenshot:
   - Breakpoint A: `len(items)=3` but the loop stops at `i=1` → BUG-06
   - Breakpoint B: `amount=10000`, `amount > 10000` is `False` → BUG-05
   - Breakpoint C: `with_vat=50525.0` so the 10% tier is used → BUG-07
   - Breakpoint D: `total_qty=0` → BUG-02
   - VARIABLES panel showing `qty: '2'` (a string) → BUG-04
   - Terminal showing the KeyError for `'Beans'` → BUG-03
6. Open `src/cart.py` (the fix) and run **"Run fixed cart demo"** → screenshot the clean output.

## Part B – tests
```bash
pytest -v --cov --cov-report=term-missing
pytest --cov --cov-report=html     # then open htmlcov/index.html
```
Screenshot the green test run, the coverage table (100% statements and branches) and the HTML report.
