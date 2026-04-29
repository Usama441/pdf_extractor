import pdfplumber, re, pandas as pd
import os

# New date pattern including DDMMMYY
date_pattern = re.compile(r'(\d{2}[-/]\w{3}[-/]\d{2,4}|\d{2}[-/]\d{2}[-/]\d{2,4}|\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[A-Za-z]{3}\d{2,4})')

header_kws_detect = ['date', 'description', 'balance', 'amount', 'withdrawal', 
                     'deposit', 'credit', 'debit', 'transaction', 'type', 'ref.', 'reference', 'account', 'debits', 'credits']

known_multi_word = {
    'reference number': 'Reference Number',
    'account balance': 'Account Balance',
    'ref. number': 'Ref. Number',
    'payments in': 'Payments In',
    'payments out': 'Payments Out',
}
extra_kws = ('in', 'out', 'number', 'cheque', 'ref.', 'reference', 'account')

skip_keywords = [
    'your bank statement', 'account summary', 'opening balance',
    'closing balance', 'total deposits', 'total withdrawals',
    'interest rate', 'overdue charges', 'interest type',
    'please see', 'important information', 'the national bank',
    'end of day', 'account balance', 'carried forward',
    'mashreqbank psc', 'it is the policy', 'full compliance',
    'customer number', 'account currency', 'account number ',
    'page ', 'opening balance', 'brought forward', 'carried forward',
    'emirates nbd', 'baniyas road', 'p.o box 777', 
    'commercial registration no', 'paid up capital', 
    'confirmation of the correctness', 'licensed by the central bank',
    'tax registration number', 'description debits', 'credits balance',
    'p.j.s.c', 'head office:', 'tel +971', 'www.emiratesnbd.com',
    'need help?', 'following channels', 'personal banking', 'business banking',
    'private banking', 'dedicated relationship', 'online banking',
    'future reference', 'dispute resolution', 'sanadak.ae',
    'centralbank.ae', 'complaint with the bank', 'contact us',
    'customer service', 'registered details:', 'commercial registration',
    'emirates nbd bank'
]

def is_skip_line(line):
    lower = line.lower().strip()
    if not lower: return True
    for kw in skip_keywords:
        if kw in lower: return True
    if any('\u0600' <= c <= '\u06FF' for c in line): return True
    if re.search(r'page\s*\d+', lower): return True
    letters = sum(1 for c in lower if 'a' <= c <= 'z')
    digits = sum(1 for c in lower if '0' <= c <= '9')
    if letters == 0 and digits == 0 and len(lower) > 2: return True
    return False

pdf_path = "/home/infiniti/Projects/Pdf_extrector/pdf/E-STATEMENT_02JUL2025_3601_unlocked.pdf"

if not os.path.exists(pdf_path):
    print(f"File not found: {pdf_path}")
    exit(1)

with pdfplumber.open(pdf_path) as pdf:
    hw = []; ht = None; hpi = None
    
    # Step 1: Detect Header
    for pi, page in enumerate(pdf.pages):
        words = page.extract_words()
        yg = {}
        for w in words:
            yk = round(w['top'] / 4) * 4
            if yk not in yg: yg[yk] = []
            yg[yk].append(w)
        
        sorted_yk = sorted(yg.keys())
        for yi, yk in enumerate(sorted_yk):
            lw = yg[yk]
            lt = ' '.join([w['text'].lower() for w in lw])
            km = sum(1 for kw in header_kws_detect if kw in lt)
            if km >= 3 and 'date' in lt:
                ht = lw[0]['top']; hpi = pi
                for adj_y in sorted_yk:
                    if abs(adj_y - yk) <= 12:
                        for w in yg[adj_y]:
                            wt = w['text'].lower()
                            if wt in header_kws_detect or wt in extra_kws:
                                hw.append(w)
                        if adj_y > yk:
                            ht = max(ht, max(w['top'] for w in yg[adj_y]))
                break
        if hw: break
    
    if not hw:
        print("Header not found")
        exit(1)

    hw.sort(key=lambda w: w['x0'])
    mc = []
    i = 0
    while i < len(hw):
        w = hw[i]
        if any(ord(c) > 127 for c in w['text']): i += 1; continue
        if i + 1 < len(hw):
            nw = hw[i + 1]
            two = (w['text'] + ' ' + nw['text']).lower()
            if two in known_multi_word:
                mc.append({'text': known_multi_word[two], 'x0': w['x0'], 'x1': nw['x1']})
                i += 2; continue
        mc.append({'text': w['text'].capitalize(), 'x0': w['x0'], 'x1': w['x1']})
        i += 1
    
    cn = [c['text'] for c in mc]
    cr = []
    for ci, col in enumerate(mc):
        xs = 0 if ci == 0 else (mc[ci-1]['x1'] + col['x0']) / 2
        xe = 9999 if ci == len(mc) - 1 else (col['x1'] + mc[ci+1]['x0']) / 2
        cr.append((xs, xe))
    
    print(f'Columns: {cn}')
    
    # Step 2: Extract rows
    raw_rows = []
    for pi, page in enumerate(pdf.pages):
        words = page.extract_words()
        if pi == hpi and ht: words = [w for w in words if w['top'] > ht + 10]
        elif pi < hpi: continue
        
        yg = {}
        for w in words:
            yk = round(w['top'] / 4) * 4
            if yk not in yg: yg[yk] = []
            yg[yk].append(w)
        
        for yk in sorted(yg.keys()):
            row = [''] * len(cn)
            for w in sorted(yg[yk], key=lambda x: x['x0']):
                wc = (w['x0'] + w['x1']) / 2
                bc = 0
                for ci, (xs, xe) in enumerate(cr):
                    if xs <= wc <= xe: bc = ci; break
                if row[bc]: row[bc] += ' ' + w['text']
                else: row[bc] = w['text']
            
            rt = ' '.join(row)
            if is_skip_line(rt): continue
            if not any(c.strip() for c in row): continue
            
            # Cleanup logic like in app.py
            num_col_indices = []
            desc_col_idx = -1
            for ci, name in enumerate(cn):
                lname = name.lower()
                if any(kw in lname for kw in ['in', 'out', 'balance', 'debit', 'credit', 'amount']):
                    num_col_indices.append(ci)
                if any(kw in lname for kw in ['transaction', 'description', 'details']):
                    desc_col_idx = ci
            
            if desc_col_idx != -1:
                for nci in num_col_indices:
                    val = row[nci].strip()
                    clean_val = val.lower().replace('cr', '').replace('dr', '').replace('aed', '').replace('usd', '').strip()
                    if any('a' <= c <= 'z' for c in clean_val):
                        if row[desc_col_idx]: row[desc_col_idx] += ' ' + val
                        else: row[desc_col_idx] = val
                        row[nci] = ''
            
            raw_rows.append(row)
    
    # Step 3: Group transactions
    txns = []; ct = None
    for row in raw_rows:
        hd = date_pattern.search(row[0]) if row[0] else False
        if hd:
            if ct: txns.append(ct)
            ct = [list(row)]
        else:
            if ct: ct.append(list(row))
    if ct: txns.append(ct)
    
    print(f'\nTransactions: {len(txns)}\n')
    for txn in txns[:50]: # Show more to check footer
        m = [''] * len(cn)
        for row in txn:
            for ci, cell in enumerate(row):
                if cell.strip():
                    if m[ci]: m[ci] += ' | ' + cell.strip()
                    else: m[ci] = cell.strip()
        print(f'  {m}')
