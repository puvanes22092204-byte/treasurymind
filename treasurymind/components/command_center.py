"""Pixel-perfect Command Center dashboard rendered as raw HTML."""


def render_command_center(user_name: str, data: dict) -> str:
    """Generate the full Command Center HTML."""
    initials = user_name[:2].upper() if user_name else "AK"
    s = data.get("summary", {})
    fx = data.get("fx_summary", {})
    alerts = data.get("alerts", [])
    cash = data.get("cash_flow", 8420000)

    transactions = str(s.get("total_invoices", 1247) + s.get("total_bank_entries", 0))
    reconciled = str(s.get("matched_count", 1089))
    pending = str(s.get("partial_count", 124))
    fx_diff = f"${int(fx.get('total_fx_loss', 28450)):,}"
    suspicious = str(len([a for a in alerts if a.get("priority", 5) <= 1]) or 14)
    cash_str = f"${int(cash):,}" if cash else "$8,420,000"
    match_rate = s.get("match_rate", 87)

    html = _get_css()
    html += _get_header(user_name, initials)
    html += _get_metrics(transactions, reconciled, pending, fx_diff, suspicious, cash_str)
    html += _get_charts()
    html += _get_fx_and_status(reconciled, pending, match_rate)
    html += _get_transactions_and_ai()
    html += "</body></html>"
    return html


def _get_css():
    return """<!DOCTYPE html><html><head>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#0b1120;color:#e6edf3;font-family:'Inter',-apple-system,sans-serif;padding:1.5rem 2rem;}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.75rem;}
.header h1{font-size:1.35rem;font-weight:700;color:#fff;}
.header .sub{font-size:0.78rem;color:#8b949e;margin-top:0.1rem;}
.header .user{display:flex;align-items:center;gap:0.6rem;}
.header .avatar{width:34px;height:34px;border-radius:50%;background:#d4760a;display:flex;align-items:center;justify-content:center;font-weight:600;font-size:0.72rem;color:#fff;}
.header .uname{font-size:0.8rem;color:#fff;font-weight:500;}
.header .urole{font-size:0.62rem;color:#8b949e;}
.metrics{display:grid;grid-template-columns:repeat(6,1fr);gap:0.9rem;margin-bottom:1.5rem;}
.m{background:#131d2f;border:1px solid rgba(255,255,255,0.05);border-radius:14px;padding:1rem 1.1rem;}
.m .mt{display:flex;justify-content:space-between;align-items:center;margin-bottom:0.45rem;}
.m .ml{font-size:0.58rem;text-transform:uppercase;letter-spacing:0.06em;color:#8b949e;font-weight:500;}
.m .mi{width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;}
.m .mv{font-size:1.35rem;font-weight:700;color:#fff;}
.m .md{font-size:0.68rem;font-weight:500;margin-top:0.15rem;}
.up{color:#06d6a0;}.down{color:#f85149;}.warn{color:#d29922;}
.card{background:#131d2f;border:1px solid rgba(255,255,255,0.05);border-radius:14px;padding:1.4rem;}
.ct{font-size:0.92rem;font-weight:600;color:#fff;margin-bottom:0.1rem;}
.cs{font-size:0.7rem;color:#8b949e;margin-bottom:0.9rem;}
.row{display:grid;gap:1rem;margin-bottom:1.25rem;}
.r21{grid-template-columns:2fr 1fr;}
.r11{grid-template-columns:1.3fr 1fr;}
.ps-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;}
.ps-l{font-size:0.76rem;color:#e6edf3;}.ps-v{font-size:0.76rem;color:#fff;font-weight:600;}
.ps-bar{height:5px;background:rgba(255,255,255,0.05);border-radius:3px;margin-bottom:0.75rem;}
.ps-f{height:100%;border-radius:3px;}
.th{display:grid;grid-template-columns:1.2fr 1.5fr 1fr 0.8fr 0.8fr;padding:0.5rem 1rem;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.04em;color:#8b949e;border-bottom:1px solid rgba(255,255,255,0.05);}
.tr{display:grid;grid-template-columns:1.2fr 1.5fr 1fr 0.8fr 0.8fr;padding:0.65rem 1rem;align-items:center;border-bottom:1px solid rgba(255,255,255,0.03);}
.tr:hover{background:rgba(6,214,160,0.03);}
.tp{color:#fff;font-size:0.76rem;font-weight:500;}.ts{color:#8b949e;font-size:0.62rem;}
.ta{color:#fff;font-size:0.8rem;font-weight:600;}.tc{color:#8b949e;font-weight:400;}
.conf{display:flex;align-items:center;gap:0.4rem;}
.cft{flex:1;height:5px;background:rgba(255,255,255,0.06);border-radius:3px;}
.cff{height:100%;border-radius:3px;}
.cp{font-size:0.68rem;color:#b1bac4;}
.badge{display:inline-block;padding:0.18rem 0.5rem;border-radius:10px;font-size:0.58rem;font-weight:600;}
.bg{background:rgba(6,214,160,0.12);color:#06d6a0;border:1px solid rgba(6,214,160,0.25);}
.by{background:rgba(210,153,34,0.12);color:#d29922;border:1px solid rgba(210,153,34,0.25);}
.bo{background:rgba(248,81,73,0.12);color:#f85149;border:1px solid rgba(248,81,73,0.25);}
.br{background:rgba(255,123,114,0.15);color:#ff7b72;border:1px solid rgba(255,123,114,0.3);}
.ai{background:#131d2f;border:1px solid rgba(255,255,255,0.05);border-radius:14px;padding:1.4rem;}
.ai .ah{display:flex;align-items:center;gap:0.5rem;margin-bottom:0.7rem;}
.ai .dot{width:8px;height:8px;border-radius:50%;background:#06d6a0;}
.ai .al{color:#06d6a0;font-size:0.76rem;font-weight:600;}
.ai .at{color:#8b949e;font-size:0.62rem;margin-left:auto;}
.ai .ax{color:#e6edf3;font-size:0.78rem;line-height:1.6;}
.ai .link{color:#06d6a0;font-size:0.76rem;font-weight:500;margin-top:0.7rem;display:inline-block;text-decoration:none;}
svg text{fill:#8b949e;font-size:10px;font-family:Inter,sans-serif;}
</style></head><body>
"""


def _get_header(user_name, initials):
    return f"""<div class="header"><div><h1>Command Center</h1><div class="sub">Live treasury operations · all currencies</div></div>
<div class="user"><div class="avatar">{initials}</div><div><div class="uname">{user_name}</div><div class="urole">Treasury Lead</div></div></div></div>"""


def _get_metrics(transactions, reconciled, pending, fx_diff, suspicious, cash_str):
    return f"""<div class="metrics">
<div class="m"><div class="mt"><span class="ml">Transactions</span><div class="mi" style="background:rgba(6,214,160,0.12);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#06d6a0" stroke-width="2.5"><path d="M7 17l9.2-9.2M17 17V7H7"/></svg></div></div><div class="mv">{transactions}</div><div class="md up">&#8599; +8.2%</div></div>
<div class="m"><div class="mt"><span class="ml">Reconciled</span><div class="mi" style="background:rgba(6,214,160,0.12);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#06d6a0" stroke-width="2.5"><circle cx="12" cy="12" r="9"/><path d="M9 12l2 2 4-4"/></svg></div></div><div class="mv">{reconciled}</div><div class="md up">&#8599; +4.1%</div></div>
<div class="m"><div class="mt"><span class="ml">Pending Review</span><div class="mi" style="background:rgba(248,81,73,0.12);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#f85149" stroke-width="2.5"><circle cx="12" cy="12" r="9"/><path d="M12 8v4m0 4h.01"/></svg></div></div><div class="mv">{pending}</div><div class="md down">&#8600; -12%</div></div>
<div class="m"><div class="mt"><span class="ml">FX Differences</span><div class="mi" style="background:rgba(210,153,34,0.12);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#d29922" stroke-width="2.5"><path d="M7 17l9.2-9.2M17 17V7H7"/></svg></div></div><div class="mv">{fx_diff}</div><div class="md warn">&#8599; +2.4%</div></div>
<div class="m"><div class="mt"><span class="ml">Suspicious</span><div class="mi" style="background:rgba(248,81,73,0.12);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#f85149" stroke-width="2.5"><path d="M7 17l9.2-9.2M17 17V7H7"/></svg></div></div><div class="mv">{suspicious}</div><div class="md down">&#8599; +3</div></div>
<div class="m"><div class="mt"><span class="ml">Cash Flow</span><div class="mi" style="background:rgba(6,214,160,0.12);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#06d6a0" stroke-width="2.5"><path d="M7 17l9.2-9.2M17 17V7H7"/></svg></div></div><div class="mv">{cash_str}</div><div class="md up">&#8599; +11.6%</div></div>
</div>"""


def _get_charts():
    return """<div class="row r21">
<div class="card"><div class="ct">Reconciliation Trends</div><div class="cs">Last 7 days</div>
<svg width="100%" height="200" viewBox="0 0 600 200" preserveAspectRatio="none">
<line x1="40" y1="50" x2="580" y2="50" stroke="rgba(255,255,255,0.04)"/>
<line x1="40" y1="100" x2="580" y2="100" stroke="rgba(255,255,255,0.04)"/>
<line x1="40" y1="150" x2="580" y2="150" stroke="rgba(255,255,255,0.04)"/>
<text x="10" y="55">220</text><text x="10" y="105">165</text><text x="10" y="155">110</text><text x="10" y="190">55</text>
<path d="M50,75 L130,55 L220,40 L310,65 L400,30 L490,85 L570,50 L570,195 L50,195 Z" fill="rgba(6,214,160,0.1)" stroke="none"/>
<path d="M50,75 L130,55 L220,40 L310,65 L400,30 L490,85 L570,50" fill="none" stroke="#06d6a0" stroke-width="2.5" stroke-linecap="round"/>
<path d="M50,168 L130,172 L220,158 L310,163 L400,152 L490,175 L570,165 L570,195 L50,195 Z" fill="rgba(248,81,73,0.06)" stroke="none"/>
<path d="M50,168 L130,172 L220,158 L310,163 L400,152 L490,175 L570,165" fill="none" stroke="#f85149" stroke-width="2" stroke-linecap="round"/>
<text x="50" y="195" text-anchor="middle">Mon</text><text x="130" y="195" text-anchor="middle">Tue</text>
<text x="220" y="195" text-anchor="middle">Wed</text><text x="310" y="195" text-anchor="middle">Thu</text>
<text x="400" y="195" text-anchor="middle">Fri</text><text x="490" y="195" text-anchor="middle">Sat</text>
<text x="570" y="195" text-anchor="middle">Sun</text>
</svg></div>
<div class="card"><div class="ct">Currency Distribution</div><div class="cs">By volume</div>
<div style="display:flex;justify-content:center;padding:0.25rem 0;">
<svg width="170" height="170" viewBox="0 0 170 170">
<circle cx="85" cy="85" r="65" fill="none" stroke="#06d6a0" stroke-width="22" stroke-dasharray="172 408" stroke-dashoffset="0" transform="rotate(-90 85 85)"/>
<circle cx="85" cy="85" r="65" fill="none" stroke="#58a6ff" stroke-width="22" stroke-dasharray="98 408" stroke-dashoffset="-172" transform="rotate(-90 85 85)"/>
<circle cx="85" cy="85" r="65" fill="none" stroke="#a855f7" stroke-width="22" stroke-dasharray="57 408" stroke-dashoffset="-270" transform="rotate(-90 85 85)"/>
<circle cx="85" cy="85" r="65" fill="none" stroke="#f85149" stroke-width="22" stroke-dasharray="37 408" stroke-dashoffset="-327" transform="rotate(-90 85 85)"/>
<circle cx="85" cy="85" r="65" fill="none" stroke="#d29922" stroke-width="22" stroke-dasharray="24 408" stroke-dashoffset="-364" transform="rotate(-90 85 85)"/>
<circle cx="85" cy="85" r="65" fill="none" stroke="#8b949e" stroke-width="22" stroke-dasharray="20 408" stroke-dashoffset="-388" transform="rotate(-90 85 85)"/>
</svg></div>
<div style="display:flex;flex-wrap:wrap;gap:0.5rem 1.2rem;justify-content:center;margin-top:0.5rem;font-size:0.68rem;color:#b1bac4;">
<span><span style="color:#06d6a0;">&#9679;</span> USD 42%</span><span><span style="color:#58a6ff;">&#9679;</span> EUR 24%</span>
<span><span style="color:#a855f7;">&#9679;</span> MYR 14%</span><span><span style="color:#f85149;">&#9679;</span> GBP 9%</span>
<span><span style="color:#d29922;">&#9679;</span> SGD 6%</span><span><span style="color:#8b949e;">&#9679;</span> Other 5%</span>
</div></div></div>"""


def _get_fx_and_status(reconciled, pending, match_rate):
    return f"""<div class="row r11">
<div class="card"><div class="ct">FX Exposure</div><div class="cs">USD equivalent by currency</div>
<svg width="100%" height="180" viewBox="0 0 480 180" preserveAspectRatio="xMidYMid meet">
<text x="10" y="18">6000k</text><text x="10" y="52">4500k</text><text x="10" y="86">3000k</text><text x="10" y="120">1500k</text><text x="10" y="154">0k</text>
<rect x="75" y="20" width="45" height="135" rx="3" fill="#06d6a0"/>
<rect x="145" y="50" width="45" height="105" rx="3" fill="#06d6a0"/>
<rect x="215" y="85" width="45" height="70" rx="3" fill="#58a6ff"/>
<rect x="285" y="110" width="45" height="45" rx="3" fill="#58a6ff"/>
<rect x="355" y="120" width="45" height="35" rx="3" fill="#58a6ff"/>
<rect x="425" y="130" width="35" height="25" rx="3" fill="#58a6ff"/>
<text x="97" y="172" text-anchor="middle">USD</text><text x="167" y="172" text-anchor="middle">EUR</text>
<text x="237" y="172" text-anchor="middle">MYR</text><text x="307" y="172" text-anchor="middle">GBP</text>
<text x="377" y="172" text-anchor="middle">SGD</text><text x="442" y="172" text-anchor="middle">JPY</text>
</svg></div>
<div class="card"><div class="ct">Payment Status</div><div class="cs">Today's breakdown</div>
<div style="margin-top:0.5rem;">
<div class="ps-row"><span class="ps-l">Auto Matched</span><span class="ps-v">{reconciled} &middot; {match_rate}%</span></div>
<div class="ps-bar"><div class="ps-f" style="width:{match_rate}%;background:#06d6a0;"></div></div>
<div class="ps-row"><span class="ps-l">Partial Match</span><span class="ps-v">{pending} &middot; 8%</span></div>
<div class="ps-bar"><div class="ps-f" style="width:8%;background:#d29922;"></div></div>
<div class="ps-row"><span class="ps-l">Needs Review</span><span class="ps-v">42 &middot; 4%</span></div>
<div class="ps-bar"><div class="ps-f" style="width:4%;background:#58a6ff;"></div></div>
<div class="ps-row"><span class="ps-l">Fraud Risk</span><span class="ps-v">14 &middot; 1%</span></div>
<div class="ps-bar"><div class="ps-f" style="width:1.5%;background:#f85149;"></div></div>
</div></div></div>"""


def _get_transactions_and_ai():
    return """<div class="row r21">
<div class="card">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.9rem;">
<div><div class="ct">Recent Transactions</div><div class="cs" style="margin-bottom:0;">Latest AI-processed payments</div></div>
<a class="link" href="#" style="color:#06d6a0;font-size:0.75rem;text-decoration:none;font-weight:500;">Open reconciliation &#8594;</a></div>
<div class="th"><span>Transaction</span><span>Counterparty</span><span>Amount</span><span>Confidence</span><span>Status</span></div>
<div class="tr">
<div><div class="tp">TXN-10241</div><div class="ts">INV-2025-0421</div></div>
<div><div class="tp">Acme Industries (US)</div><div class="ts">&#8594; Pacific Holdings (MY)</div></div>
<div><div class="ta">42.5 <span class="tc">MYR</span></div><div class="ts">exp 10 USD</div></div>
<div class="conf"><div class="cft"><div class="cff" style="width:94%;background:#06d6a0;"></div></div><span class="cp">94%</span></div>
<span class="badge bg">Auto Matched</span></div>
<div class="tr">
<div><div class="tp">TXN-10242</div><div class="ts">INV-2025-0422</div></div>
<div><div class="tp">Tanaka Trading Co (JP)</div><div class="ts">&#8594; Nordic Components (SE)</div></div>
<div><div class="ta">12,410 <span class="tc">EUR</span></div><div class="ts">exp 12,500 EUR</div></div>
<div class="conf"><div class="cft"><div class="cff" style="width:88%;background:#06d6a0;"></div></div><span class="cp">88%</span></div>
<span class="badge by">Partial Match</span></div>
<div class="tr">
<div><div class="tp">TXN-10243</div><div class="ts">INV-2025-0419</div></div>
<div><div class="tp">Mumbai Textiles (IN)</div><div class="ts">&#8594; Lyon Fashion House (FR)</div></div>
<div><div class="ta">7,920 <span class="tc">EUR</span></div><div class="ts">exp 8,500 EUR</div></div>
<div class="conf"><div class="cft"><div class="cff" style="width:62%;background:#f85149;"></div></div><span class="cp">62%</span></div>
<span class="badge bo">Needs Review</span></div>
<div class="tr">
<div><div class="tp">TXN-10244</div><div class="ts">INV-2025-0418</div></div>
<div><div class="tp">Unknown wire</div><div class="ts">&#8594; Pacific Holdings (MY)</div></div>
<div><div class="ta">24,800 <span class="tc">USD</span></div><div class="ts">exp 0 USD</div></div>
<div class="conf"><div class="cft"><div class="cff" style="width:21%;background:#f85149;"></div></div><span class="cp">21%</span></div>
<span class="badge br">Fraud Risk</span></div>
</div>
<div class="ai">
<div class="ah"><div class="dot"></div><span class="al">AI Insight</span><span class="at">Updated 2 min ago</span></div>
<div class="ax">Reconciliation rate up <span style="color:#06d6a0;font-weight:600;">+4.1%</span> this week. MYR settlements show recurring <span style="color:#f85149;font-weight:600;">MYR 0.70</span> intermediary fee from CIMB &#8594; Maybank corridor. Consider whitelisting this fee pattern to lift auto-match by ~6%.</div>
<a class="link" href="#" style="color:#06d6a0;font-size:0.76rem;text-decoration:none;font-weight:500;margin-top:0.7rem;display:inline-block;">Ask Treasury Copilot &#8594;</a>
</div></div>"""
