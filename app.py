<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fondamentaux Économiques — Timor-Leste</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root {
            --bg: #f5f4f0;
            --bg2: #edecea;
            --surface: #ffffff;
            --surface2: #f9f8f6;
            --border: #dddbd7;
            --border2: #e8e6e2;
            --text: #1a1916;
            --text2: #4a4843;
            --muted: #8a8780;
            --accent: #2b4a6b;
            --accent2: #1a3450;
            --accent-light: #e8eef4;
            --red: #c0392b;
            --red-light: #fdf0ee;
            --orange: #c0620a;
            --orange-light: #fef3e8;
            --green: #2e7d4f;
            --green-light: #eef6f1;
            --blue: #2563a8;
            --blue-light: #eef3fa;
            --gold: #8b6914;
            --gold-light: #faf4e6;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.65;
            font-size: 14px;
        }

        /* HEADER */
        header {
            background: var(--accent2);
            padding: 1.8rem 2.5rem;
            border-bottom: 3px solid #c8a84b;
        }

        .header-inner {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            gap: 2rem;
            flex-wrap: wrap;
        }

        .header-text h1 {
            font-size: 1.5rem;
            font-weight: normal;
            color: #f0ece4;
            letter-spacing: 0.3px;
            font-family: 'Georgia', serif;
        }

        .header-text h1 em {
            color: #c8a84b;
            font-style: normal;
            font-weight: bold;
        }

        .header-text p {
            color: rgba(240,236,228,0.55);
            font-size: 0.75rem;
            margin-top: 0.35rem;
            font-family: 'Segoe UI', sans-serif;
            letter-spacing: 0.2px;
        }

        .header-badges {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-left: auto;
            align-items: center;
        }

        .badge {
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(200,168,75,0.35);
            border-radius: 3px;
            padding: 0.25rem 0.7rem;
            font-size: 0.7rem;
            color: rgba(240,236,228,0.7);
            font-family: 'Segoe UI', sans-serif;
            letter-spacing: 0.3px;
        }

        .badge.warn { border-color: rgba(192,98,10,0.6); color: #e8a96a; }
        .badge.danger { border-color: rgba(192,57,43,0.6); color: #e8968c; }
        .badge.ok { border-color: rgba(46,125,79,0.6); color: #8ecfaa; }

        /* NAV */
        nav {
            background: var(--surface);
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        }

        .nav-inner {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            overflow-x: auto;
            scrollbar-width: none;
        }

        .nav-inner::-webkit-scrollbar { display: none; }

        .nav-btn {
            padding: 0.85rem 1.3rem;
            background: none;
            border: none;
            color: var(--muted);
            cursor: pointer;
            white-space: nowrap;
            font-size: 0.78rem;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 500;
            border-bottom: 2px solid transparent;
            transition: all 0.15s;
            letter-spacing: 0.2px;
        }

        .nav-btn:hover { color: var(--text); background: var(--bg2); }
        .nav-btn.active { color: var(--accent); border-bottom-color: var(--accent); font-weight: 600; }

        /* MAIN */
        main {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem 2.5rem;
        }

        /* SECTION */
        .section { display: none; }
        .section.active { display: block; }

        .section-header {
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            margin-bottom: 1.8rem;
            padding-bottom: 1.2rem;
            border-bottom: 1px solid var(--border);
        }

        .section-icon {
            font-size: 1.2rem;
            opacity: 0.7;
            padding-top: 0.15rem;
            flex-shrink: 0;
        }

        .section-header h2 {
            font-size: 1.2rem;
            font-weight: normal;
            color: var(--accent2);
            font-family: 'Georgia', serif;
            letter-spacing: 0.2px;
        }

        .section-header p {
            color: var(--muted);
            font-size: 0.76rem;
            margin-top: 0.25rem;
            font-family: 'Segoe UI', sans-serif;
        }

        /* GRID */
        .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.2rem; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2rem; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.2rem; }

        @media (max-width: 1100px) {
            .grid-4 { grid-template-columns: repeat(2, 1fr); }
            .grid-3 { grid-template-columns: repeat(2, 1fr); }
        }
        @media (max-width: 680px) {
            .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
            main { padding: 1.2rem; }
            header { padding: 1.2rem; }
        }

        /* CARD */
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 1.2rem 1.4rem;
        }

        .card-title {
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--muted);
            margin-bottom: 0.6rem;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 600;
        }

        .kpi {
            font-size: 1.9rem;
            font-weight: bold;
            color: var(--accent2);
            line-height: 1;
            font-family: 'Georgia', serif;
        }

        .kpi-sub {
            font-size: 0.75rem;
            color: var(--text2);
            margin-top: 0.4rem;
            font-family: 'Segoe UI', sans-serif;
        }

        .kpi-trend {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            font-size: 0.7rem;
            margin-top: 0.4rem;
            padding: 0.2rem 0.5rem;
            border-radius: 2px;
            font-family: 'Segoe UI', sans-serif;
        }

        .trend-up { background: var(--green-light); color: var(--green); }
        .trend-down { background: var(--red-light); color: var(--red); }
        .trend-neutral { background: var(--orange-light); color: var(--orange); }

        /* CHART CARD */
        .chart-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 1.2rem 1.4rem;
        }

        .chart-card h3 {
            font-size: 0.85rem;
            font-weight: normal;
            color: var(--text);
            font-family: 'Georgia', serif;
            margin-bottom: 0.2rem;
        }

        .chart-card p {
            font-size: 0.71rem;
            color: var(--muted);
            margin-bottom: 1rem;
            font-family: 'Segoe UI', sans-serif;
        }

        .chart-wrap { position: relative; height: 210px; }
        .chart-wrap.tall { height: 260px; }

        /* TABLE */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.78rem;
            font-family: 'Segoe UI', sans-serif;
        }

        .data-table th {
            background: var(--surface2);
            padding: 0.5rem 0.75rem;
            text-align: left;
            color: var(--muted);
            font-weight: 600;
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            border-bottom: 1px solid var(--border);
        }

        .data-table td {
            padding: 0.5rem 0.75rem;
            border-bottom: 1px solid var(--border2);
            color: var(--text2);
        }

        .data-table tr:last-child td { border-bottom: none; }
        .data-table tr:hover td { background: var(--surface2); }

        /* PROGRESS BAR */
        .progress-wrap { margin-bottom: 0.85rem; }

        .progress-label {
            display: flex;
            justify-content: space-between;
            font-size: 0.74rem;
            margin-bottom: 0.3rem;
            font-family: 'Segoe UI', sans-serif;
            color: var(--text2);
        }

        .progress-bar {
            height: 5px;
            background: var(--bg2);
            border-radius: 2px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            border-radius: 2px;
        }

        /* ALERT */
        .alert {
            border-radius: 3px;
            padding: 0.85rem 1rem;
            font-size: 0.78rem;
            border-left: 3px solid;
            margin-bottom: 0.85rem;
            font-family: 'Segoe UI', sans-serif;
            line-height: 1.55;
        }

        .alert-warn { background: var(--orange-light); border-color: #c0620a; color: #5a3008; }
        .alert-danger { background: var(--red-light); border-color: #c0392b; color: #5a1a14; }
        .alert-ok { background: var(--green-light); border-color: #2e7d4f; color: #15402a; }
        .alert-info { background: var(--blue-light); border-color: #2563a8; color: #12305a; }
        .alert-gold { background: var(--gold-light); border-color: #8b6914; color: #4a3608; }

        .alert strong { display: block; margin-bottom: 0.25rem; font-size: 0.8rem; }

        /* SOURCE TAG */
        .source-tag {
            font-size: 0.65rem;
            color: var(--muted);
            margin-top: 0.6rem;
            font-family: 'Segoe UI', sans-serif;
            font-style: italic;
            border-top: 1px solid var(--border2);
            padding-top: 0.4rem;
        }

        /* RISK METER */
        .risk-meter { display: flex; flex-direction: column; gap: 0.6rem; }

        .risk-row {
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }

        .risk-label {
            font-size: 0.75rem;
            color: var(--text2);
            width: 150px;
            flex-shrink: 0;
            font-family: 'Segoe UI', sans-serif;
        }

        .risk-bar {
            flex: 1;
            height: 6px;
            background: var(--bg2);
            border-radius: 2px;
            overflow: hidden;
        }

        .risk-fill { height: 100%; border-radius: 2px; }

        .risk-val {
            font-size: 0.7rem;
            font-weight: 600;
            width: 50px;
            text-align: right;
            font-family: 'Segoe UI', sans-serif;
        }

        /* TIMELINE */
        .timeline { position: relative; padding-left: 1.3rem; }

        .timeline::before {
            content: '';
            position: absolute;
            left: 0; top: 0; bottom: 0;
            width: 1px;
            background: var(--border);
        }

        .timeline-item { position: relative; padding-bottom: 1rem; }

        .timeline-item::before {
            content: '';
            position: absolute;
            left: -1.45rem;
            top: 0.38rem;
            width: 8px;
            height: 8px;
            background: var(--accent);
            border-radius: 50%;
            border: 2px solid var(--surface);
        }

        .timeline-year {
            font-size: 0.68rem;
            color: var(--accent);
            font-weight: 700;
            font-family: 'Segoe UI', sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .timeline-text {
            font-size: 0.77rem;
            color: var(--text2);
            font-family: 'Segoe UI', sans-serif;
            line-height: 1.5;
        }

        /* COMPARE BOX */
        .compare-box {
            background: var(--surface2);
            border: 1px solid var(--border2);
            border-radius: 3px;
            padding: 0.55rem 0.8rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.4rem;
        }

        .compare-label {
            font-size: 0.74rem;
            color: var(--text2);
            font-family: 'Segoe UI', sans-serif;
        }

        .compare-val {
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--accent2);
            font-family: 'Segoe UI', sans-serif;
        }

        /* PILL */
        .pill {
            display: inline-block;
            padding: 0.15rem 0.5rem;
            border-radius: 2px;
            font-size: 0.68rem;
            font-weight: 600;
            font-family: 'Segoe UI', sans-serif;
        }

        .pill-red { background: var(--red-light); color: var(--red); }
        .pill-orange { background: var(--orange-light); color: var(--orange); }
        .pill-green { background: var(--green-light); color: var(--green); }
        .pill-blue { background: var(--blue-light); color: var(--blue); }
        .pill-gold { background: var(--gold-light); color: var(--gold); }

        /* OVERVIEW RIBBON */
        .overview-ribbon {
            background: var(--accent-light);
            border: 1px solid #c8d8e8;
            border-left: 3px solid var(--accent);
            border-radius: 3px;
            padding: 1rem 1.2rem;
            margin-bottom: 1.5rem;
            font-size: 0.8rem;
            color: var(--text2);
            font-family: 'Segoe UI', sans-serif;
            line-height: 1.6;
        }

        .overview-ribbon strong { color: var(--accent2); }

        /* DIVIDER */
        .sep {
            height: 1px;
            background: var(--border2);
            margin: 1rem 0;
        }

        .mt-1 { margin-top: 1rem; }
        .mt-2 { margin-top: 1.5rem; }

        /* SECTION LABEL */
        .sub-label {
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--muted);
            margin-bottom: 0.8rem;
            margin-top: 1.5rem;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 600;
            padding-bottom: 0.4rem;
            border-bottom: 1px solid var(--border2);
        }

        /* FOOTNOTE */
        .footnote {
            font-size: 0.68rem;
            color: var(--muted);
            font-family: 'Segoe UI', sans-serif;
            font-style: italic;
            margin-top: 0.5rem;
        }

        /* FOOTER */
        footer {
            text-align: center;
            padding: 2rem;
            color: var(--muted);
            font-size: 0.7rem;
            border-top: 1px solid var(--border);
            margin-top: 3rem;
            background: var(--surface);
            font-family: 'Segoe UI', sans-serif;
            line-height: 1.8;
        }
    </style>
</head>
<body>

<!-- HEADER -->
<header>
    <div class="header-inner">
        <div class="header-text">
            <h1>Timor-Leste — <em>Fondamentaux Économiques</em></h1>
            <p>Tableau de bord analytique · Sources : FMI, Banque Mondiale, ADB, BPA, INE · Données 2022–2025</p>
        </div>
        <div class="header-badges">
            <span class="badge">PIB ~2,4 Md$</span>
            <span class="badge warn">IDA · PDSL</span>
            <span class="badge danger">Pétrole > 70% rev.</span>
            <span class="badge ok">Paix stable</span>
            <span class="badge">Devise : USD</span>
        </div>
    </div>
</header>

<!-- NAV -->
<nav>
    <div class="nav-inner">
        <button class="nav-btn active" onclick="showTab('socio', this)">① Socioéco & Politique</button>
        <button class="nav-btn" onclick="showTab('croissance', this)">② Modèle de Croissance</button>
        <button class="nav-btn" onclick="showTab('finances', this)">③ Finances Publiques</button>
        <button class="nav-btn" onclick="showTab('externe', this)">④ Équilibres Externes</button>
        <button class="nav-btn" onclick="showTab('financier', this)">⑤ Syst. Financier & Mon.</button>
        <button class="nav-btn" onclick="showTab('climat', this)">⑥ Risque Climat & Nature</button>
    </div>
</nav>

<!-- MAIN -->
<main>

<!-- ======================================================= -->
<!-- PILIER 1 — SOCIOÉCONOMIQUE & POLITIQUE -->
<!-- ======================================================= -->
<section id="socio" class="section active">
    <div class="section-header">
        <div class="section-icon">🏛</div>
        <div>
            <h2>Pilier 1 — Cadre Socioéconomique & Politique</h2>
            <p>Population, développement humain, gouvernance, pauvreté et indicateurs structurels</p>
        </div>
    </div>

    <div class="overview-ribbon">
        Le Timor-Leste est l'un des États les plus jeunes du monde (indépendance 2002). Avec ~1,36 million d'habitants et un IDH de <strong>0,607</strong> (rang 140e/191 — PNUD 2023), il est classé <strong>pays à développement humain moyen</strong>. La dépendance aux hydrocarbures et la fragilité institutionnelle contraignent la trajectoire de développement, malgré des progrès notables depuis 2002.
    </div>

    <div class="grid-4">
        <div class="card">
            <div class="card-title">Population (2023)</div>
            <div class="kpi">1,36 M</div>
            <div class="kpi-sub">Croissance : +2,1%/an · Âge médian : 20 ans</div>
            <div class="kpi-trend trend-neutral">↗ Population très jeune</div>
            <div class="source-tag">INE Timor-Leste · Banque Mondiale 2023</div>
        </div>
        <div class="card">
            <div class="card-title">IDH (PNUD 2023)</div>
            <div class="kpi">0,607</div>
            <div class="kpi-sub">Rang 140 / 191 nations</div>
            <div class="kpi-trend trend-up">↑ +0,011 vs 2019 (0,596)</div>
            <div class="source-tag">UNDP Human Development Report 2023/24</div>
        </div>
        <div class="card">
            <div class="card-title">Taux de pauvreté national</div>
            <div class="kpi">41,8%</div>
            <div class="kpi-sub">Seuil $1,90/j (PPA) : ~19%</div>
            <div class="kpi-trend trend-down">↓ vs 49,9% en 2007</div>
            <div class="source-tag">INE — Enquête Démographie & Santé 2016 · BAD 2022</div>
        </div>
        <div class="card">
            <div class="card-title">PIB / habitant (PPA)</div>
            <div class="kpi">8 450 $</div>
            <div class="kpi-sub">Nominal : ~1 790 $ · inclut revenus pétroliers</div>
            <div class="kpi-trend trend-neutral">Nominal faible hors pétrole</div>
            <div class="source-tag">FMI WEO Avril 2024</div>
        </div>
    </div>

    <div class="sub-label">Développement humain & indicateurs sociaux</div>

    <div class="grid-2">
        <div class="chart-card">
            <h3>Évolution de l'IDH et composantes (2010–2023)</h3>
            <p>Éducation, santé, revenu — comparaison avec la moyenne Asie-Pacifique bas revenu</p>
            <div class="chart-wrap">
                <canvas id="idhChart"></canvas>
            </div>
            <div class="source-tag">PNUD Human Development Reports 2010-2023</div>
        </div>
        <div class="chart-card">
            <h3>Indicateurs sociaux clés — comparaison régionale (2022–23)</h3>
            <p>Timor-Leste vs moyenne Asie-Pacifique bas revenu (score normalisé /100)</p>
            <div class="chart-wrap">
                <canvas id="socialRadar"></canvas>
            </div>
            <div class="source-tag">UNDP · WHO · UNESCO · Banque Mondiale 2023</div>
        </div>
    </div>

    <div class="sub-label">Gouvernance & contexte politique</div>

    <div class="grid-3">
        <div class="card">
            <div class="card-title">Indicateurs de gouvernance (Banque Mondiale — WGI 2022)</div>
            <div class="mt-1 risk-meter">
                <div class="risk-row">
                    <span class="risk-label">Voix & responsabilité</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:55%;background:#2563a8"></div></div>
                    <span class="risk-val" style="color:var(--blue)">+0,22</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Stabilité politique</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:42%;background:#2e7d4f"></div></div>
                    <span class="risk-val" style="color:var(--green)">-0,32</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Efficacité gouvernement</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:28%;background:#c0620a"></div></div>
                    <span class="risk-val" style="color:var(--orange)">-0,89</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Qualité réglementation</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:22%;background:#c0392b"></div></div>
                    <span class="risk-val" style="color:var(--red)">-1,05</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">État de droit</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:30%;background:#c0620a"></div></div>
                    <span class="risk-val" style="color:var(--orange)">-0,82</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Contrôle corruption</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:38%;background:#c0620a"></div></div>
                    <span class="risk-val" style="color:var(--orange)">-0,56</span>
                </div>
            </div>
            <div class="source-tag">Banque Mondiale — Worldwide Governance Indicators 2022</div>
        </div>

        <div class="card">
            <div class="card-title">Indicateurs sociaux fondamentaux</div>
            <table class="data-table mt-1">
                <thead>
                    <tr><th>Indicateur</th><th>Valeur</th><th>Tendance</th></tr>
                </thead>
                <tbody>
                    <tr><td>Espérance de vie</td><td>69,5 ans</td><td><span class="pill pill-green">↑</span></td></tr>
                    <tr><td>Mortalité infantile (‰)</td><td>37,8</td><td><span class="pill pill-orange">↓ lente</span></td></tr>
                    <tr><td>Taux de fécondité</td><td>4,0</td><td><span class="pill pill-orange">↓ lente</span></td></tr>
                    <tr><td>Scolarisation primaire</td><td>95,4%</td><td><span class="pill pill-green">↑</span></td></tr>
                    <tr><td>Analphabétisme adulte</td><td>31,6%</td><td><span class="pill pill-orange">↓ lente</span></td></tr>
                    <tr><td>Accès eau potable</td><td>71%</td><td><span class="pill pill-orange">↑</span></td></tr>
                    <tr><td>Accès électricité</td><td>82%</td><td><span class="pill pill-green">↑</span></td></tr>
                    <tr><td>Malnutrition &lt;5 ans</td><td>47%</td><td><span class="pill pill-red">Critique</span></td></tr>
                    <tr><td>Indice Gini</td><td>28,7</td><td><span class="pill pill-green">Modéré</span></td></tr>
                </tbody>
            </table>
            <div class="source-tag">UNICEF · WHO · INE TL · Banque Mondiale WDI 2022-23</div>
        </div>

        <div class="card">
            <div class="card-title">Repères politiques & institutionnels</div>
            <div class="timeline mt-1">
                <div class="timeline-item">
                    <div class="timeline-year">2002</div>
                    <div class="timeline-text">Indépendance. République Démocratique, régime semi-présidentiel.</div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-year">2006</div>
                    <div class="timeline-text">Crise politico-militaire. Intervention UNMIT (ONU jusqu'en 2012).</div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-year">2011</div>
                    <div class="timeline-text">Loi du Fonds Pétrolier (BPA) renforcée. Adhésion ITIE.</div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-year">2023</div>
                    <div class="timeline-text">Rui Maria de Araújo (Fretilin) Premier ministre. Stabilité coalitionnelle.</div>
                </div>
                <div class="timeline-item">
                    <div class="timeline-year">2024</div>
                    <div class="timeline-text">Candidature ASEAN (admission attendue 2025). Négociations Greater Sunrise actives.</div>
                </div>
            </div>
            <div class="sep"></div>
            <div class="alert alert-info">
                <strong>IPC — Transparency International 2023</strong>
                Score : 38/100 · Rang 77/180. +12 points depuis 2012.
            </div>
            <div class="source-tag">TI · Parlement TL · UNMIT · MNE Timor-Leste</div>
        </div>
    </div>

    <div class="sub-label">Revenus & emploi</div>

    <div class="grid-2">
        <div class="chart-card">
            <h3>PIB par habitant (USD courants) 2002–2023</h3>
            <p>Total vs non-pétrolier — l'écart mesure la dépendance aux hydrocarbures</p>
            <div class="chart-wrap tall">
                <canvas id="gdpPerCapita"></canvas>
            </div>
            <div class="source-tag">Banque Mondiale WDI · FMI WEO 2024</div>
        </div>
        <div class="chart-card">
            <h3>Structure de l'emploi par secteur (2021)</h3>
            <p>Informalité et agriculture de subsistance dominantes</p>
            <div class="chart-wrap tall">
                <canvas id="emploiChart"></canvas>
            </div>
            <div class="source-tag">INE TL — Enquête Emploi 2021 · ILO</div>
        </div>
    </div>
</section>

<!-- ======================================================= -->
<!-- PILIER 2 — MODÈLE DE CROISSANCE -->
<!-- ======================================================= -->
<section id="croissance" class="section">
    <div class="section-header">
        <div class="section-icon">📈</div>
        <div>
            <h2>Pilier 2 — Modèle de Croissance</h2>
            <p>Structure du PIB, secteurs porteurs, diversification, investissement et productivité</p>
        </div>
    </div>

    <div class="overview-ribbon">
        L'économie timoraise souffre d'une <strong>dépendance extrême aux hydrocarbures</strong> (>80% des recettes publiques, >95% des exportations). Le <strong>PIB non-pétrolier</strong> (~1,8 Md$) est dominé par les services publics et l'agriculture de subsistance. La croissance post-COVID s'est stabilisée autour de <strong>+3–4%</strong>, insuffisante face à la pression démographique de 2,1%/an.
    </div>

    <div class="grid-4">
        <div class="card">
            <div class="card-title">Taux de croissance réel 2023</div>
            <div class="kpi" style="color:var(--blue)">+3,4%</div>
            <div class="kpi-sub">PIB non-pétrolier : +2,8%</div>
            <div class="kpi-trend trend-neutral">Prévision 2024 : +3,8% (FMI)</div>
            <div class="source-tag">FMI Article IV 2024</div>
        </div>
        <div class="card">
            <div class="card-title">Part pétrole dans PIB total</div>
            <div class="kpi" style="color:var(--red)">42%</div>
            <div class="kpi-sub">En baisse (>60% en 2012)</div>
            <div class="kpi-trend trend-down">↓ Déclin naturel des champs</div>
            <div class="source-tag">FMI · BPA 2023</div>
        </div>
        <div class="card">
            <div class="card-title">FBCF / PIB</div>
            <div class="kpi" style="color:var(--green)">22,4%</div>
            <div class="kpi-sub">Investissement public : 15% · Privé : ~7%</div>
            <div class="kpi-trend trend-neutral">Investissement privé très faible</div>
            <div class="source-tag">Banque Mondiale WDI 2022</div>
        </div>
        <div class="card">
            <div class="card-title">Productivité du travail</div>
            <div class="kpi" style="color:var(--gold)">3 210 $</div>
            <div class="kpi-sub">PIB non-pétrolier / actif occupé</div>
            <div class="kpi-trend trend-neutral">Parmi les plus faibles d'ASE</div>
            <div class="source-tag">ILO · FMI 2022</div>
        </div>
    </div>

    <div class="sub-label">Dynamique de croissance</div>

    <div class="grid-2">
        <div class="chart-card">
            <h3>Croissance du PIB réel (%) 2005–2025p</h3>
            <p>PIB total vs PIB non-pétrolier</p>
            <div class="chart-wrap tall">
                <canvas id="gdpGrowth"></canvas>
            </div>
            <div class="source-tag">FMI WEO Avril 2024 · p = projection</div>
        </div>
        <div class="chart-card">
            <h3>Composition du PIB non-pétrolier par secteur (2022)</h3>
            <p>Structure sectorielle hors hydrocarbures</p>
            <div class="chart-wrap tall">
                <canvas id="sectorPie"></canvas>
            </div>
            <div class="source-tag">INE TL — Comptes nationaux 2022</div>
        </div>
    </div>

    <div class="sub-label">Secteurs & contraintes</div>

    <div class="grid-3">
        <div class="card">
            <div class="card-title">Agriculture — secteur de subsistance</div>
            <div class="alert alert-ok mt-1">
                <strong>27% du PIB non-pétrolier · 60% de l'emploi</strong>
                Café Arabica d'altitude (Ermera, Aileu) : principal produit d'export non-pétrolier. Riz, maïs, manioc. Rendements faibles : 0,8–1,2 t/ha vs 4 t/ha médiane asiatique.
            </div>
            <div class="compare-box">
                <span class="compare-label">Export café (2023)</span>
                <span class="compare-val">~11 M$</span>
            </div>
            <div class="compare-box">
                <span class="compare-label">Surface agricole utilisée</span>
                <span class="compare-val">26% du territoire</span>
            </div>
            <div class="source-tag">FAO · MAFF TL · Banque Mondiale 2023</div>
        </div>

        <div class="card">
            <div class="card-title">Secteur pétrolier — Greater Sunrise & Bayu-Undan</div>
            <div class="alert alert-danger mt-1">
                <strong>Épuisement de Bayu-Undan (~2023)</strong>
                Plus de 16 Md$ de recettes cumulées depuis 2004. Fermeture imminente. Greater Sunrise (5,1 Tcf de gaz estimés) reste en négociation sans accord commercial définitif. Risque d'effondrement des recettes à horizon 2030.
            </div>
            <div class="compare-box">
                <span class="compare-label">Réserves Greater Sunrise (gaz)</span>
                <span class="compare-val">5,1 Tcf</span>
            </div>
            <div class="compare-box">
                <span class="compare-label">Production pétrole 2023</span>
                <span class="compare-val">~8 000 bbl/j</span>
            </div>
            <div class="source-tag">Timor Sea Treaty · BPA 2023 · TLEA</div>
        </div>

        <div class="card">
            <div class="card-title">Tourisme & services — potentiel latent</div>
            <div class="alert alert-info mt-1">
                <strong>~75 000 visiteurs/an (2023)</strong>
                Un seul aéroport international. Patrimoine marin exceptionnel (Atauro). Port profond Tibar Bay opérationnel depuis 2023. Zone économique spéciale ZEESM (Oecusse) en développement.
            </div>
            <div class="compare-box">
                <span class="compare-label">Contribution tourisme / PIB</span>
                <span class="compare-val">~3,5%</span>
            </div>
            <div class="compare-box">
                <span class="compare-label">Capacité hôtelière</span>
                <span class="compare-val">~2 500 chambres</span>
            </div>
            <div class="source-tag">SEFOPE · WTTC · Banque Mondiale 2023</div>
        </div>
    </div>

    <div class="grid-2 mt-1">
        <div class="chart-card">
            <h3>Environnement des affaires (scores /100)</h3>
            <p>Timor-Leste vs médiane Asie du Sud-Est — obstacles à l'investissement privé</p>
            <div class="chart-wrap">
                <canvas id="doingBiz"></canvas>
            </div>
            <div class="source-tag">Banque Mondiale B-READY 2024 · Doing Business 2020</div>
        </div>

        <div class="card">
            <div class="card-title">Contraintes structurelles à la croissance</div>
            <div class="mt-1 risk-meter">
                <div class="risk-row">
                    <span class="risk-label">Qualité infrastructures</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:28%;background:#c0392b"></div></div>
                    <span class="risk-val" style="color:var(--red)">Faible</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Capital humain</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:40%;background:#c0620a"></div></div>
                    <span class="risk-val" style="color:var(--orange)">Moyen</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Accès au financement</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:25%;background:#c0392b"></div></div>
                    <span class="risk-val" style="color:var(--red)">Faible</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Diversification export</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:12%;background:#c0392b"></div></div>
                    <span class="risk-val" style="color:var(--red)">Très faible</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Environnement réglem.</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:32%;background:#c0620a"></div></div>
                    <span class="risk-val" style="color:var(--orange)">Faible</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Connectivité numérique</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:35%;background:#c0620a"></div></div>
                    <span class="risk-val" style="color:var(--orange)">Moyen</span>
                </div>
            </div>
            <div class="sep"></div>
            <div class="alert alert-gold">
                <strong>Plan national PNDS 2011–2030</strong>
                Diversification ciblée : agro-industrie café, tourisme côtier, industrie légère. Tibar Bay (port profond, 2023) et ZEESM comme leviers structurants.
            </div>
            <div class="source-tag">Gouvernement TL · BAD · FMI 2024</div>
        </div>
    </div>
</section>

<!-- ======================================================= -->
<!-- PILIER 3 — FINANCES PUBLIQUES -->
<!-- ======================================================= -->
<section id="finances" class="section">
    <div class="section-header">
        <div class="section-icon">💰</div>
        <div>
            <h2>Pilier 3 — Finances Publiques</h2>
            <p>Budget de l'État, Fonds pétrolier, soutenabilité fiscale et trajectoire de la dépense</p>
        </div>
    </div>

    <div class="overview-ribbon">
        Le Timor-Leste dispose d'un <strong>Fonds Pétrolier (BPA)</strong> de ~15,8 Md$ (fin 2023) — l'un des plus grands fonds souverains rapporté au PIB (~7x). Mais les prélèvements excèdent le <strong>Revenu Soutenable Estimé (ESI)</strong> depuis 2016, créant une trajectoire d'épuisement à horizon 2034–2036 sans réforme. Les recettes domestiques ne couvrent que <strong>20–25%</strong> des dépenses publiques.
    </div>

    <div class="grid-4">
        <div class="card">
            <div class="card-title">Fonds Pétrolier (BPA) — Actifs fin 2023</div>
            <div class="kpi" style="color:var(--gold)">15,8 Md$</div>
            <div class="kpi-sub">~7x le PIB nominal</div>
            <div class="kpi-trend trend-down">↓ De 17,3 Md$ (2022) — prélèvements > ESI</div>
            <div class="source-tag">BPA Annual Report 2023</div>
        </div>
        <div class="card">
            <div class="card-title">ESI (revenu soutenable estimé)</div>
            <div class="kpi" style="color:var(--green)">~625 M$</div>
            <div class="kpi-sub">3% des actifs du fonds</div>
            <div class="kpi-trend trend-down">Prélèvement réel 2023 : ~980 M$</div>
            <div class="source-tag">BPA · FMI Article IV 2024</div>
        </div>
        <div class="card">
            <div class="card-title">Dépenses publiques / PIB</div>
            <div class="kpi" style="color:var(--accent)">54%</div>
            <div class="kpi-sub">Salaires + transferts = 60% des dép.</div>
            <div class="kpi-trend trend-neutral">État très interventionniste</div>
            <div class="source-tag">MF TL — Budget Geral Estado 2023</div>
        </div>
        <div class="card">
            <div class="card-title">Recettes domestiques / PIB</div>
            <div class="kpi" style="color:var(--red)">12,3%</div>
            <div class="kpi-sub">Parmi les plus faibles au monde</div>
            <div class="kpi-trend trend-up">↑ Objectif : 15% à 2026 (PFM)</div>
            <div class="source-tag">FMI Article IV 2024 · MF TL</div>
        </div>
    </div>

    <div class="sub-label">Fonds pétrolier & trajectoire budgétaire</div>

    <div class="grid-2">
        <div class="chart-card">
            <h3>Évolution du Fonds Pétrolier vs ESI (2007–2024)</h3>
            <p>Actifs totaux, prélèvements annuels et revenu soutenable estimé</p>
            <div class="chart-wrap tall">
                <canvas id="petroFund"></canvas>
            </div>
            <div class="source-tag">BPA Annual Reports 2007-2023 · FMI projections 2024</div>
        </div>
        <div class="chart-card">
            <h3>Structure des recettes budgétaires (2023)</h3>
            <p>Ventilation des sources de financement de l'État</p>
            <div class="chart-wrap tall">
                <canvas id="recettesChart"></canvas>
            </div>
            <div class="source-tag">Ministère des Finances TL — Budget 2023</div>
        </div>
    </div>

    <div class="sub-label">Soutenabilité & dépenses</div>

    <div class="grid-3">
        <div class="card">
            <div class="card-title">Trajectoire budgétaire 2020–2025</div>
            <table class="data-table mt-1">
                <thead>
                    <tr><th>Année</th><th>Recettes</th><th>Dépenses</th><th>Solde / PIB</th></tr>
                </thead>
                <tbody>
                    <tr><td>2020</td><td>1 241 M$</td><td>1 420 M$</td><td><span class="pill pill-red">-5,2%</span></td></tr>
                    <tr><td>2021</td><td>983 M$</td><td>1 380 M$</td><td><span class="pill pill-red">-11,2%</span></td></tr>
                    <tr><td>2022</td><td>1 650 M$</td><td>1 610 M$</td><td><span class="pill pill-green">+0,9%</span></td></tr>
                    <tr><td>2023</td><td>1 380 M$</td><td>1 520 M$</td><td><span class="pill pill-red">-4,1%</span></td></tr>
                    <tr><td>2024e</td><td>1 290 M$</td><td>1 450 M$</td><td><span class="pill pill-red">-5,8%</span></td></tr>
                    <tr><td>2025p</td><td>1 200 M$</td><td>1 400 M$</td><td><span class="pill pill-red">-6,5%</span></td></tr>
                </tbody>
            </table>
            <div class="source-tag">FMI WEO / Article IV 2024 · MF TL · p=proj · e=estim.</div>
        </div>

        <div class="card">
            <div class="card-title">Structure des dépenses publiques (2023)</div>
            <div class="mt-1">
                <div class="progress-wrap">
                    <div class="progress-label"><span>Salaires & fonction publique</span><span>31%</span></div>
                    <div class="progress-bar"><div class="progress-fill" style="width:31%;background:#2b4a6b"></div></div>
                </div>
                <div class="progress-wrap">
                    <div class="progress-label"><span>Transferts & programmes sociaux</span><span>22%</span></div>
                    <div class="progress-bar"><div class="progress-fill" style="width:22%;background:#2563a8"></div></div>
                </div>
                <div class="progress-wrap">
                    <div class="progress-label"><span>Investissement public</span><span>28%</span></div>
                    <div class="progress-bar"><div class="progress-fill" style="width:28%;background:#2e7d4f"></div></div>
                </div>
                <div class="progress-wrap">
                    <div class="progress-label"><span>Biens & services</span><span>13%</span></div>
                    <div class="progress-bar"><div class="progress-fill" style="width:13%;background:#c0620a"></div></div>
                </div>
                <div class="progress-wrap">
                    <div class="progress-label"><span>Intérêts de la dette</span><span>2%</span></div>
                    <div class="progress-bar"><div class="progress-fill" style="width:2%;background:#c0392b"></div></div>
                </div>
                <div class="progress-wrap">
                    <div class="progress-label"><span>Autres</span><span>4%</span></div>
                    <div class="progress-bar"><div class="progress-fill" style="width:4%;background:#8a8780"></div></div>
                </div>
            </div>
            <div class="source-tag">MF TL — Budget Geral Estado 2023</div>
        </div>

        <div class="card">
            <div class="card-title">Soutenabilité fiscale & dette publique</div>
            <div class="alert alert-ok">
                <strong>Dette extérieure : ~3,2% du PIB (2023)</strong>
                Très faible endettement (prêts concessionnels BAD, BM). Pas d'émission obligataire souveraine. Risque de surendettement : FAIBLE (DSA FMI 2024).
            </div>
            <div class="alert alert-danger">
                <strong>Risque d'épuisement du Fonds Pétrolier</strong>
                Les projections FMI (2024) indiquent un épuisement entre 2034 et 2037 si les prélèvements restent supérieurs à l'ESI sans nouveau revenu pétrolier. La mobilisation des recettes domestiques est urgente.
            </div>
            <div class="compare-box">
                <span class="compare-label">Créanciers concessionnels</span>
                <span class="compare-val">95% (BM / BAD)</span>
            </div>
            <div class="compare-box">
                <span class="compare-label">Service dette / rev. export</span>
                <span class="compare-val">< 2%</span>
            </div>
            <div class="source-tag">FMI DSA 2024 · BPA · Trésor TL</div>
        </div>
    </div>

    <div class="chart-card mt-2">
        <h3>Projection d'épuisement du Fonds Pétrolier — trois scénarios (2024–2040)</h3>
        <p>Scénario de base FMI · Scénario réforme fiscale · Scénario Greater Sunrise</p>
        <div class="chart-wrap tall">
            <canvas id="fundProjection"></canvas>
        </div>
        <div class="source-tag">FMI Article IV Staff Report 2024 · BPA modèles actuariels</div>
    </div>
</section>

<!-- ======================================================= -->
<!-- PILIER 4 — ÉQUILIBRES EXTERNES -->
<!-- ======================================================= -->
<section id="externe" class="section">
    <div class="section-header">
        <div class="section-icon">⚖️</div>
        <div>
            <h2>Pilier 4 — Équilibres Externes</h2>
            <p>Balance des paiements, commerce extérieur, IDE et position extérieure nette</p>
        </div>
    </div>

    <div class="overview-ribbon">
        Le Timor-Leste présente une <strong>dépendance totale aux exportations pétrolières</strong> (~95% des recettes d'export). Le compte courant est fortement volatil selon le cours du Brent. La <strong>Position Extérieure Nette</strong> est exceptionnellement favorable grâce au Fonds Pétrolier (~+650% du PIB). Les IDE non-pétroliers restent anémiques (~50–80 M$/an).
    </div>

    <div class="grid-4">
        <div class="card">
            <div class="card-title">Solde compte courant 2023</div>
            <div class="kpi" style="color:var(--red)">-14,2%</div>
            <div class="kpi-sub">du PIB non-pétrolier</div>
            <div class="kpi-trend trend-neutral">Excédent global grâce aux revenus pétrole</div>
            <div class="source-tag">FMI Article IV 2024</div>
        </div>
        <div class="card">
            <div class="card-title">Exportations totales (2023)</div>
            <div class="kpi" style="color:var(--blue)">620 M$</div>
            <div class="kpi-sub">Pétrole : 95% · Café : ~2%</div>
            <div class="kpi-trend trend-down">↓ Déclin de la production pétrolière</div>
            <div class="source-tag">BPA · DNTPF · OEC 2023</div>
        </div>
        <div class="card">
            <div class="card-title">Importations totales (2023)</div>
            <div class="kpi" style="color:var(--orange)">750 M$</div>
            <div class="kpi-sub">Alimentation + carburant = 55%</div>
            <div class="kpi-trend trend-neutral">Forte dépendance aux importations</div>
            <div class="source-tag">DNTPF · UNSD Comtrade 2023</div>
        </div>
        <div class="card">
            <div class="card-title">Position Extérieure Nette</div>
            <div class="kpi" style="color:var(--green)">+645%</div>
            <div class="kpi-sub">du PIB (actifs nets)</div>
            <div class="kpi-trend trend-up">↑ Grâce au Fonds Pétrolier</div>
            <div class="source-tag">BPA · FMI IIP 2023</div>
        </div>
    </div>

    <div class="sub-label">Flux commerciaux & partenaires</div>

    <div class="grid-2">
        <div class="chart-card">
            <h3>Balance commerciale 2010–2023 (Millions USD)</h3>
            <p>Exportations, importations et solde commercial</p>
            <div class="chart-wrap tall">
                <canvas id="tradeBalance"></canvas>
            </div>
            <div class="source-tag">UNSD Comtrade · FMI BOP Statistics 2023</div>
        </div>
        <div class="chart-card">
            <h3>Principaux partenaires commerciaux (2022)</h3>
            <p>Destinations des exports et origines des imports (M$)</p>
            <div class="chart-wrap tall">
                <canvas id="tradePartners"></canvas>
            </div>
            <div class="source-tag">OEC (Observatory of Economic Complexity) · DNTPF 2022</div>
        </div>
    </div>

    <div class="sub-label">Structure & IDE</div>

    <div class="grid-3">
        <div class="card">
            <div class="card-title">Structure des exportations (2022)</div>
            <table class="data-table mt-1">
                <thead>
                    <tr><th>Produit</th><th>Valeur</th><th>Part</th></tr>
                </thead>
                <tbody>
                    <tr><td>Pétrole brut & condensats</td><td>580 M$</td><td><span class="pill pill-red">93,5%</span></td></tr>
                    <tr><td>Café vert & transformé</td><td>11 M$</td><td><span class="pill pill-orange">1,8%</span></td></tr>
                    <tr><td>Minerais & matériaux</td><td>8 M$</td><td>1,3%</td></tr>
                    <tr><td>Produits de la mer</td><td>4 M$</td><td>0,6%</td></tr>
                    <tr><td>Autres</td><td>17 M$</td><td>2,8%</td></tr>
                </tbody>
            </table>
            <div class="alert alert-danger mt-1">
                <strong>Concentration extrême (HHI élevé)</strong>
                Vulnérabilité maximale aux chocs pétroliers.
            </div>
            <div class="source-tag">OEC · DNTPF · BPA 2022</div>
        </div>

        <div class="card">
            <div class="card-title">Structure des importations (2022)</div>
            <div class="mt-1">
                <div class="progress-wrap">
                    <div class="progress-label"><span>Produits alimentaires</span><span>28%</span></div>
                    <div class="progress-bar"><div class="progress-fill" style="width:28%;background:#c0392b"></div></div>
                </div>
                <div class="progress-wrap">
                    <div class="progress-label"><span>Carburants & énergie</span><span>18%</span></div>
                    <div class="progress-bar"><div class="progress-fill" style="width:18%;background:#c0620a"></div></div>
                </div>
                <div class="progress-wrap">
                    <div class="progress-label"><span>Machines & équipements</span><span>22%</span></div>
                    <div class="progress-bar"><div class="progress-fill" style="width:22%;background:#2563a8"></div></div>
                </div>
                <div class="progress-wrap">
                    <div class="progress-label"><span>Matériaux de construction</span><span>12%</span></div>
                    <div class="progress-bar"><div class="progress-fill" style="width:12%;background:#2b4a6b"></div></div>
                </div>
                <div class="progress-wrap">
                    <div class="progress-label"><span>Produits manufacturés</span><span>14%</span></div>
                    <div class="progress-bar"><div class="progress-fill" style="width:14%;background:#2e7d4f"></div></div>
                </div>
                <div class="progress-wrap">
                    <div class="progress-label"><span>Autres</span><span>6%</span></div>
                    <div class="progress-bar"><div class="progress-fill" style="width:6%;background:#8a8780"></div></div>
                </div>
            </div>
            <div class="source-tag">UNSD Comtrade · DNTPF 2022</div>
        </div>

        <div class="card">
            <div class="card-title">IDE entrants & financements externes</div>
            <div class="compare-box">
                <span class="compare-label">IDE nets entrants 2022</span>
                <span class="compare-val">62 M$ (2,7% PIB)</span>
            </div>
            <div class="compare-box">
                <span class="compare-label">Stock IDE 2022</span>
                <span class="compare-val">~780 M$</span>
            </div>
            <div class="compare-box">
                <span class="compare-label">Remittances diaspora</span>
                <span class="compare-val">~25 M$ (1,1% PIB)</span>
            </div>
            <div class="compare-box">
                <span class="compare-label">Aide publique au développement</span>
                <span class="compare-val">~120 M$ (5,3% PIB)</span>
            </div>
            <div class="alert alert-info mt-1">
                <strong>Principaux investisseurs IDE :</strong>
                Australie, Chine, Portugal, Indonésie. Secteurs : télécom (Telkomcel), hôtellerie, construction. Loi sur l'investissement (2011, rév. 2017) jugée peu attractive : procédures lentes, insécurité foncière.
            </div>
            <div class="source-tag">UNCTAD WIR 2023 · Banque Mondiale 2023 · OECD DAC</div>
        </div>
    </div>

    <div class="chart-card mt-2">
        <h3>Compte courant et composantes 2015–2023 (% PIB non-pétrolier)</h3>
        <p>Balance commerciale, revenus primaires, transferts courants et solde global</p>
        <div class="chart-wrap">
            <canvas id="currentAccount"></canvas>
        </div>
        <div class="source-tag">FMI BOP Statistics / Article IV 2024</div>
    </div>
</section>

<!-- ======================================================= -->
<!-- PILIER 5 — SYSTÈME FINANCIER & MONÉTAIRE -->
<!-- ======================================================= -->
<section id="financier" class="section">
    <div class="section-header">
        <div class="section-icon">🏦</div>
        <div>
            <h2>Pilier 5 — Système Financier & Politique Monétaire</h2>
            <p>Secteur bancaire, inclusion financière, dollarisation et politique de change</p>
        </div>
    </div>

    <div class="overview-ribbon">
        Le Timor-Leste est <strong>entièrement dollarisé</strong> (USD monnaie officielle depuis 2000) — sans banque centrale au sens propre ni politique monétaire indépendante. L'<strong>Autoridade Bancária e de Pagamentos (ABP)</strong> assure la supervision prudentielle. Le secteur bancaire est <strong>petit, peu profond mais très bien capitalisé</strong>. L'inclusion financière reste parmi les plus faibles d'Asie (~36%).
    </div>

    <div class="grid-4">
        <div class="card">
            <div class="card-title">Régime monétaire</div>
            <div class="kpi" style="color:var(--accent);font-size:1.4rem">USD Officiel</div>
            <div class="kpi-sub">Dollarisation intégrale depuis 2000</div>
            <div class="kpi-trend trend-neutral">Aucune politique de change propre</div>
            <div class="source-tag">ABP · BCP · FMI AREAER 2023</div>
        </div>
        <div class="card">
            <div class="card-title">Crédit privé / PIB</div>
            <div class="kpi" style="color:var(--red)">22,4%</div>
            <div class="kpi-sub">Médiane ASE : ~80%</div>
            <div class="kpi-trend trend-up">↑ +5 pts en 5 ans</div>
            <div class="source-tag">ABP · Banque Mondiale GFDD 2022</div>
        </div>
        <div class="card">
            <div class="card-title">Inclusion financière</div>
            <div class="kpi" style="color:var(--orange)">36%</div>
            <div class="kpi-sub">Adultes avec compte bancaire</div>
            <div class="kpi-trend trend-up">↑ de 22% en 2017 — mobile money +</div>
            <div class="source-tag">Banque Mondiale Findex 2021</div>
        </div>
        <div class="card">
            <div class="card-title">NPL / Prêts totaux</div>
            <div class="kpi" style="color:var(--orange)">5,8%</div>
            <div class="kpi-sub">En amélioration (7,2% en 2020)</div>
            <div class="kpi-trend trend-up">↑ Qualité de portefeuille améliorée</div>
            <div class="source-tag">ABP Annual Report 2023</div>
        </div>
    </div>

    <div class="sub-label">Crédit & taux d'intérêt</div>

    <div class="grid-2">
        <div class="chart-card">
            <h3>Évolution du crédit bancaire au secteur privé (2012–2023)</h3>
            <p>Stock total par type d'emprunteur (M USD)</p>
            <div class="chart-wrap tall">
                <canvas id="creditChart"></canvas>
            </div>
            <div class="source-tag">ABP — Supervisão do Sistema Financeiro 2023</div>
        </div>
        <div class="chart-card">
            <h3>Taux d'intérêt bancaires (2018–2023)</h3>
            <p>Taux débiteur, créditeur et spread — parmi les plus élevés de la région</p>
            <div class="chart-wrap tall">
                <canvas id="ratesChart"></canvas>
            </div>
            <div class="source-tag">ABP · FMI International Financial Statistics 2023</div>
        </div>
    </div>

    <div class="sub-label">Architecture du secteur & contraintes</div>

    <div class="grid-3">
        <div class="card">
            <div class="card-title">Architecture du secteur bancaire (2023)</div>
            <table class="data-table mt-1">
                <thead>
                    <tr><th>Banque</th><th>Type</th><th>Part marché</th></tr>
                </thead>
                <tbody>
                    <tr><td>ANZ (Australie)</td><td>Étrangère</td><td>~35%</td></tr>
                    <tr><td>BNU (BCP Portugal)</td><td>Étrangère</td><td>~28%</td></tr>
                    <tr><td>Mandiri (Indonésie)</td><td>Étrangère</td><td>~18%</td></tr>
                    <tr><td>Banco Kambista</td><td>Nationale pub.</td><td>~10%</td></tr>
                    <tr><td>Microfinance (IMFTL, Moris Rasik)</td><td>IMF</td><td>~9%</td></tr>
                </tbody>
            </table>
            <div class="alert alert-info mt-1">
                <strong>5 banques commerciales + 4 IMF</strong>
                Secteur concentré, dominé par les banques étrangères. Absence de marché obligataire et de bourse des valeurs.
            </div>
            <div class="source-tag">ABP · FMI 2023</div>
        </div>

        <div class="card">
            <div class="card-title">Contraintes de la dollarisation</div>
            <div class="alert alert-ok">
                <strong>Avantages</strong>
                Stabilité nominale, crédibilité anti-inflationniste, facilitation des échanges internationaux. Inflation 2023 : 8,1% (choc alimentaire/énergie), attendue ~5% en 2024.
            </div>
            <div class="alert alert-danger">
                <strong>Contraintes majeures</strong>
                Absence d'instrument de politique monétaire propre · Impossible d'ajuster le taux de change pour la compétitivité · Prêteur en dernier ressort limité · Exposition aux chocs transmis par le cycle USD.
            </div>
            <div class="compare-box">
                <span class="compare-label">Inflation CPI 2023</span>
                <span class="compare-val">8,1%</span>
            </div>
            <div class="compare-box">
                <span class="compare-label">Inflation prévue 2024</span>
                <span class="compare-val">4,8%</span>
            </div>
            <div class="source-tag">ABP · FMI WEO · INE TL — IPC 2023</div>
        </div>

        <div class="card">
            <div class="card-title">Inclusion financière & mobile money</div>
            <div class="mt-1 risk-meter">
                <div class="risk-row">
                    <span class="risk-label">Compte bancaire formel</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:36%;background:#2563a8"></div></div>
                    <span class="risk-val" style="color:var(--blue)">36%</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Mobile money (actif)</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:28%;background:#2b4a6b"></div></div>
                    <span class="risk-val" style="color:var(--accent)">28%</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Accès crédit formel</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:15%;background:#c0392b"></div></div>
                    <span class="risk-val" style="color:var(--red)">15%</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Femmes — compte bancaire</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:28%;background:#c0620a"></div></div>
                    <span class="risk-val" style="color:var(--orange)">28%</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Agences / 10 000 hab.</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:21%;background:#c0620a"></div></div>
                    <span class="risk-val" style="color:var(--orange)">2,1</span>
                </div>
            </div>
            <div class="sep"></div>
            <div class="alert alert-gold">
                <strong>Programme Telemóvel Banking (ABP 2022)</strong>
                Agents mobiles en zones rurales. Bnkle (fintech locale) lancée 2021. NFIS cible 60% d'inclusion d'ici 2025.
            </div>
            <div class="source-tag">Banque Mondiale Findex 2021 · ABP NFIS 2021-2025</div>
        </div>
    </div>

    <div class="chart-card mt-2">
        <h3>Indicateurs prudentiels du secteur bancaire (2019–2023)</h3>
        <p>Ratio de fonds propres (CAR), NPL, ROA, ratio de liquidité</p>
        <div class="chart-wrap">
            <canvas id="prudentialChart"></canvas>
        </div>
        <div class="source-tag">ABP Annual Reports 2019-2023 · FMI FSI Database</div>
    </div>
</section>

<!-- ======================================================= -->
<!-- PILIER 6 — RISQUES CLIMAT & NATURE -->
<!-- ======================================================= -->
<section id="climat" class="section">
    <div class="section-header">
        <div class="section-icon">🌿</div>
        <div>
            <h2>Pilier 6 — Risques Climat & Nature</h2>
            <p>Vulnérabilité climatique, aléas naturels, biodiversité et transition énergétique</p>
        </div>
    </div>

    <div class="overview-ribbon">
        Le Timor-Leste est classé parmi les <strong>10 pays les plus vulnérables au changement climatique</strong> (ND-GAIN Index). Les risques physiques sont multiples : cyclones, inondations, glissements de terrain, sécheresses, élévation du niveau marin et dégradation des récifs. L'économie agro-dépendante amplifie directement les <strong>risques de transmission sur la sécurité alimentaire</strong>.
    </div>

    <div class="grid-4">
        <div class="card">
            <div class="card-title">ND-GAIN Vulnerability Score (2022)</div>
            <div class="kpi" style="color:var(--red)">0,474</div>
            <div class="kpi-sub">Rang 113/185 — vulnérabilité élevée</div>
            <div class="kpi-trend trend-down">Capacité d'adaptation : très faible</div>
            <div class="source-tag">Notre Dame Global Adaptation Initiative 2022</div>
        </div>
        <div class="card">
            <div class="card-title">Index risque climatique (Germanwatch)</div>
            <div class="kpi" style="color:var(--orange)">46,8</div>
            <div class="kpi-sub">Rang 41/183 — très exposé</div>
            <div class="kpi-trend trend-neutral">Pertes 2002-2021 : ~0,9% PIB/an</div>
            <div class="source-tag">Germanwatch Global Climate Risk Index 2023</div>
        </div>
        <div class="card">
            <div class="card-title">Couverture forestière (2020)</div>
            <div class="kpi" style="color:var(--green)">46%</div>
            <div class="kpi-sub">Du territoire</div>
            <div class="kpi-trend trend-down">↓ Déforestation : -0,8%/an</div>
            <div class="source-tag">FAO FRA 2020 · MAQP TL</div>
        </div>
        <div class="card">
            <div class="card-title">Émissions CO₂ / habitant (2021)</div>
            <div class="kpi" style="color:var(--blue)">0,44 t</div>
            <div class="kpi-sub">Total national : ~0,6 Mt CO₂/an</div>
            <div class="kpi-trend trend-neutral">Empreinte très faible</div>
            <div class="source-tag">Global Carbon Atlas · IEA 2022</div>
        </div>
    </div>

    <div class="sub-label">Risques physiques & tendances climatiques</div>

    <div class="grid-2">
        <div class="chart-card">
            <h3>Profil de risque — Aléas naturels (probabilité × intensité)</h3>
            <p>Évaluation multidimensionnelle des risques physiques</p>
            <div class="chart-wrap tall">
                <canvas id="hazardRadar"></canvas>
            </div>
            <div class="source-tag">PDNA 2013 · UNDRR · Banque Mondiale CCDR 2023 · EM-DAT</div>
        </div>
        <div class="chart-card">
            <h3>Anomalies de température & précipitations (1980–2023)</h3>
            <p>Écart par rapport à la moyenne de référence 1981-2010</p>
            <div class="chart-wrap tall">
                <canvas id="climateChart"></canvas>
            </div>
            <div class="source-tag">NOAA · BMKG · Climate Change Knowledge Portal BM 2023</div>
        </div>
    </div>

    <div class="sub-label">Biodiversité, politique climatique & scénarios</div>

    <div class="grid-3">
        <div class="card">
            <div class="card-title">Risques physiques détaillés</div>
            <div class="mt-1 risk-meter">
                <div class="risk-row">
                    <span class="risk-label">Glissements de terrain</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:85%;background:#c0392b"></div></div>
                    <span class="risk-val" style="color:var(--red)">Très élevé</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Inondations fluviales</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:78%;background:#c0392b"></div></div>
                    <span class="risk-val" style="color:var(--red)">Élevé</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Élévation niveau mer</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:72%;background:#c0392b"></div></div>
                    <span class="risk-val" style="color:var(--red)">Élevé</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Blanchissement coraux</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:80%;background:#c0392b"></div></div>
                    <span class="risk-val" style="color:var(--red)">Élevé</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Sécheresse agricole</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:65%;background:#c0620a"></div></div>
                    <span class="risk-val" style="color:var(--orange)">Élevé</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Cyclones tropicaux</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:60%;background:#c0620a"></div></div>
                    <span class="risk-val" style="color:var(--orange)">Modéré+</span>
                </div>
                <div class="risk-row">
                    <span class="risk-label">Séismes</span>
                    <div class="risk-bar"><div class="risk-fill" style="width:55%;background:#c0620a"></div></div>
                    <span class="risk-val" style="color:var(--orange)">Modéré</span>
                </div>
            </div>
            <div class="source-tag">UNDRR GAR 2022 · EM-DAT · IPCC AR6 2023</div>
        </div>

        <div class="card">
            <div class="card-title">Biodiversité & capital naturel</div>
            <div class="alert alert-ok">
                <strong>Biodiversité marine exceptionnelle</strong>
                Île d'Atauro : densité de poissons de récif la plus haute jamais enregistrée (Conservation International, 2016). Mer de Timor : hotspot mondial requin-baleine et dugong.
            </div>
            <div class="alert alert-warn">
                <strong>Pressions terrestres importantes</strong>
                Agriculture sur brûlis, surpâturage, urbanisation non planifiée de Dili. Érosion des sols affectant 46% des terres agricoles (UNDP-FAO 2019).
            </div>
            <table class="data-table mt-1">
                <thead><tr><th>Indicateur</th><th>Valeur</th></tr></thead>
                <tbody>
                    <tr><td>Aires protégées (% territoire)</td><td>8,2%</td></tr>
                    <tr><td>Zones marines protégées</td><td>~11%</td></tr>
                    <tr><td>Espèces menacées (UICN)</td><td>62 espèces</td></tr>
                    <tr><td>Score intégrité biodiversité</td><td>44/100</td></tr>
                </tbody>
            </table>
            <div class="source-tag">UICN Red List · CI · UNDP BIOFIN · IBAT 2023</div>
        </div>

        <div class="card">
            <div class="card-title">Politique climatique & scénarios à 2050</div>
            <div class="alert alert-info">
                <strong>NDC actualisée (2022)</strong>
                Réduction de 22% des émissions d'ici 2030 (conditionnel : 50%). Objectif mix renouvelable : 55% en 2030 vs ~14% actuellement. Accord de Paris ratifié 2017.
            </div>
            <div class="alert alert-danger">
                <strong>Scénario +3°C à 2050 (IPCC SSP3-7.0)</strong>
                Perte 20–35% productivité agricole · Submersion 15% des zones côtières basses · Déplacement potentiel 80–120 000 personnes · Effondrement des récifs coralliens (-70%).
            </div>
            <div class="compare-box">
                <span class="compare-label">Mix électricité renouvelable</span>
                <span class="compare-val">~14% (2023)</span>
            </div>
            <div class="compare-box">
                <span class="compare-label">Finance climatique reçue (2021)</span>
                <span class="compare-val">~45 M$</span>
            </div>
            <div class="alert alert-warn">
                <strong>Paradoxe climatique</strong>
                Le développement de Greater Sunrise (gaz fossile) est central à la stratégie de recettes publiques, en tension directe avec les objectifs NDC et la neutralité carbone.
            </div>
            <div class="source-tag">UNFCCC NDC Registry · IRENA · GCF · ARE 2022-23 · IPCC AR6</div>
        </div>
    </div>

    <div class="grid-2 mt-1">
        <div class="chart-card">
            <h3>Catastrophes naturelles & pertes économiques (2000–2023)</h3>
            <p>Nombre d'événements enregistrés et pertes estimées en % du PIB</p>
            <div class="chart-wrap">
                <canvas id="disasterChart"></canvas>
            </div>
            <div class="source-tag">EM-DAT CRED Database 2023 · OCHA TL</div>
        </div>
        <div class="chart-card">
            <h3>Transition énergétique — État des lieux (2023)</h3>
            <p>Mix de production électrique actuel et objectif 2030</p>
            <div class="chart-wrap">
                <canvas id="energyChart"></canvas>
            </div>
            <div class="source-tag">IRENA · ARE · EDTL (Eletricidade de Timor-Leste) 2023</div>
        </div>
    </div>
</section>

</main>

<footer>
    <p><strong>Timor-Leste — Fondamentaux Économiques</strong> · Tableau de bord analytique</p>
    <p>Sources principales : FMI (WEO, Article IV, DSA 2024) · Banque Mondiale (WDI, WGI, Findex) · UNDP HDR 2023 · BPA Annual Report 2023 · ABP · INE Timor-Leste · ADB · UNCTAD · FAO · IPCC AR6 · ND-GAIN · Germanwatch · EM-DAT · UNSD Comtrade · OEC</p>
    <p>Document à des fins analytiques et pédagogiques · Données 2022–2025 · Avril 2026</p>
</footer>

<script>
// NAVIGATION
function showTab(id, btn) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    btn.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// CHART DEFAULTS
Chart.defaults.color = '#6a6860';
Chart.defaults.borderColor = '#dddbd7';
Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";
Chart.defaults.font.size = 11;

const g = 'rgba(221,219,215,0.6)';

// Palette sobre
const P = {
    blue:    '#2b4a6b',
    blue2:   '#4a7aab',
    green:   '#2e7d4f',
    red:     '#c0392b',
    orange:  '#c0620a',
    gold:    '#8b6914',
    grey:    '#8a8780',
    teal:    '#2e7d6e',
    purple:  '#5a4a7a',
};

const alphaColor = (hex, a) => {
    const r = parseInt(hex.slice(1,3),16);
    const g2 = parseInt(hex.slice(3,5),16);
    const b = parseInt(hex.slice(5,7),16);
    return `rgba(${r},${g2},${b},${a})`;
};

// ── PILIER 1 ────────────────────────────────────────────
new Chart(document.getElementById('idhChart'), {
    type: 'line',
    data: {
        labels: ['2010','2012','2014','2015','2017','2018','2019','2021','2022','2023'],
        datasets: [
            { label: 'IDH Timor-Leste', data: [0.496,0.530,0.558,0.569,0.582,0.589,0.596,0.601,0.604,0.607], borderColor: P.blue, backgroundColor: alphaColor(P.blue,0.06), tension:0.4, fill:true, pointRadius:3, borderWidth:2 },
            { label: 'Indice Éducation', data: [0.430,0.452,0.465,0.473,0.489,0.495,0.502,0.508,0.511,0.515], borderColor: P.orange, backgroundColor:'transparent', tension:0.4, borderDash:[5,3], pointRadius:2, borderWidth:1.5 },
            { label: 'Indice Santé', data: [0.700,0.718,0.730,0.738,0.748,0.752,0.758,0.762,0.765,0.769], borderColor: P.green, backgroundColor:'transparent', tension:0.4, borderDash:[5,3], pointRadius:2, borderWidth:1.5 },
            { label: 'Moy. ASE bas revenu', data: [0.520,0.535,0.548,0.556,0.564,0.568,0.572,0.578,0.581,0.585], borderColor: P.grey, backgroundColor:'transparent', tension:0.4, borderDash:[8,4], pointRadius:2, borderWidth:1.5 }
        ]
    },
    options: { responsive:true, maintainAspectRatio:false, interaction:{mode:'index',intersect:false}, plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}}, scales:{y:{min:0.4,max:0.85,grid:{color:g}},x:{grid:{color:g}}} }
});

new Chart(document.getElementById('socialRadar'), {
    type: 'radar',
    data: {
        labels: ['Espérance vie', 'Scolarisation', 'Accès eau', 'Électricité', 'Mortalité inf. (inv)', 'Nutrition', 'Égalité genre'],
        datasets: [
            { label: 'Timor-Leste', data: [70,78,71,82,45,35,55], borderColor: P.blue, backgroundColor: alphaColor(P.blue,0.1), pointBackgroundColor: P.blue, borderWidth:2 },
            { label: 'Moy. Asie-Pac. bas revenu', data: [74,85,82,78,60,55,65], borderColor: P.grey, backgroundColor: alphaColor(P.grey,0.05), borderDash:[5,3], pointBackgroundColor: P.grey, borderWidth:1.5 }
        ]
    },
    options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}}, scales:{r:{min:0,max:100,grid:{color:g},angleLines:{color:g},pointLabels:{font:{size:10}}}} }
});

new Chart(document.getElementById('gdpPerCapita'), {
    type: 'line',
    data: {
        labels: ['2002','2004','2006','2008','2010','2012','2014','2016','2018','2020','2022','2023'],
        datasets: [
            { label: 'PIB/hab total (USD)', data: [490,610,730,1050,2120,3780,2860,2010,1820,1560,1890,1790], borderColor: P.gold, backgroundColor: alphaColor(P.gold,0.08), tension:0.3, fill:true, pointRadius:3, borderWidth:2 },
            { label: 'PIB/hab non-pétrolier', data: [320,390,450,590,780,920,1050,1180,1240,1150,1390,1420], borderColor: P.blue, backgroundColor: alphaColor(P.blue,0.06), tension:0.3, fill:true, pointRadius:3, borderWidth:2 }
        ]
    },
    options: { responsive:true, maintainAspectRatio:false, interaction:{mode:'index',intersect:false}, plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}}, scales:{y:{ticks:{callback:v=>v+'$'},grid:{color:g}},x:{grid:{color:g}}} }
});

new Chart(document.getElementById('emploiChart'), {
    type: 'doughnut',
    data: {
        labels: ['Agriculture (subsistance)', 'Services publics', 'Commerce & serv. priv.', 'Construction', 'Industrie légère', 'Pêche', 'Autre'],
        datasets: [{ data: [60,16,10,7,4,2,1], backgroundColor: [P.green, P.blue, P.purple, P.orange, P.red, P.teal, P.grey], borderColor:'#ffffff', borderWidth:2 }]
    },
    options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'right',labels:{boxWidth:10,padding:8,font:{size:10}}}} }
});

// ── PILIER 2 ────────────────────────────────────────────
new Chart(document.getElementById('gdpGrowth'), {
    type: 'bar',
    data: {
        labels: ['2005','2007','2009','2011','2013','2015','2017','2019','2020','2021','2022','2023','2024p','2025p'],
        datasets: [
            { label: 'Croissance PIB total (%)', data: [6.2,9.8,12.9,14.6,2.8,4.0,0.2,-0.1,-8.3,3.5,3.5,3.4,3.8,4.0], backgroundColor: (ctx) => ctx.raw >= 0 ? alphaColor(P.blue,0.65) : alphaColor(P.red,0.65), borderRadius:2 },
            { type:'line', label: 'PIB non-pétrolier (%)', data: [8.5,12.2,10.1,9.0,6.8,3.5,5.4,3.2,-7.2,2.8,4.2,2.8,3.5,3.8], borderColor: P.orange, backgroundColor:'transparent', tension:0.3, pointRadius:3, borderWidth:2 }
        ]
    },
    options: { responsive:true, maintainAspectRatio:false, interaction:{mode:'index',intersect:false}, plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}}, scales:{y:{grid:{color:g},ticks:{callback:v=>v+'%'}},x:{grid:{color:g}}} }
});

new Chart(document.getElementById('sectorPie'), {
    type: 'doughnut',
    data: {
        labels: ['Adm. publique & défense', 'Agriculture', 'Commerce & hôtellerie', 'Construction', 'Transport & comm.', 'Éducation & santé', 'Industrie', 'Autres services'],
        datasets: [{ data: [28,22,15,12,8,7,4,4], backgroundColor: [P.blue, P.green, P.purple, P.orange, P.teal, P.red, P.gold, P.grey], borderColor:'#ffffff', borderWidth:2 }]
    },
    options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'right',labels:{boxWidth:10,padding:6,font:{size:10}}}} }
});

new Chart(document.getElementById('doingBiz'), {
    type: 'bar',
    data: {
        labels: ['Création entreprise', 'Permis construction', 'Électricité', 'Enregist. propriété', 'Crédit', 'Protection invest.', 'Commerce transfr.', 'Contrats', 'Insolvabilité'],
        datasets: [
            { label: 'Timor-Leste', data: [52,38,45,22,28,32,41,25,18], backgroundColor: alphaColor(P.red,0.7), borderRadius:2 },
            { label: 'Médiane ASE', data: [72,68,65,58,55,62,68,55,48], backgroundColor: alphaColor(P.blue,0.45), borderRadius:2 }
        ]
    },
    options: { responsive:true, maintainAspectRatio:false, indexAxis:'y', interaction:{mode:'index',intersect:false}, plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}}, scales:{x:{min:0,max:100,grid:{color:g}},y:{grid:{color:g}}} }
});

// ── PILIER 3 ────────────────────────────────────────────
new Chart(document.getElementById('petroFund'), {
    type: 'line',
    data: {
        labels: ['2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021','2022','2023','2024e'],
        datasets: [
            { label: 'Actifs BPA (Md$)', data: [1.0,2.4,5.4,7.1,8.8,11.8,14.9,16.6,16.3,15.8,16.8,17.1,17.1,16.2,18.9,17.3,15.8,14.9], borderColor: P.gold, backgroundColor: alphaColor(P.gold,0.08), tension:0.3, fill:true, pointRadius:2, borderWidth:2.5 },
            { label: 'Prélèvement annuel (Md$)', data: [0.3,0.5,0.7,0.7,0.9,1.0,0.5,0.7,0.9,0.9,0.7,0.8,0.6,0.7,0.6,0.8,0.98,0.95], borderColor: P.red, backgroundColor:'transparent', tension:0.3, borderDash:[6,3], pointRadius:2, borderWidth:2 },
            { label: 'ESI — revenu soutenable (Md$)', data: [0.03,0.07,0.16,0.21,0.26,0.35,0.45,0.50,0.49,0.47,0.50,0.51,0.51,0.49,0.57,0.52,0.62,0.59], borderColor: P.green, backgroundColor:'transparent', tension:0.3, pointRadius:2, borderWidth:2 }
        ]
    },
    options: { responsive:true, maintainAspectRatio:false, interaction:{mode:'index',intersect:false}, plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}}, scales:{y:{ticks:{callback:v=>v+'Md$'},grid:{color:g}},x:{grid:{color:g}}} }
});

new Chart(document.getElementById('recettesChart'), {
    type: 'doughnut',
    data: {
        labels: ['Prélèvement Fonds Pétrolier', 'Impôts sur revenus', 'Taxes commerce intérieur', 'Droits de douane', 'Aide au développement', 'Autres recettes'],
        datasets: [{ data: [64,10,8,5,9,4], backgroundColor: [P.gold, P.blue, P.purple, P.green, P.teal, P.grey], borderColor:'#ffffff', borderWidth:2 }]
    },
    options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'right',labels:{boxWidth:10,padding:8,font:{size:10}}}} }
});

new Chart(document.getElementById('fundProjection'), {
    type: 'line',
    data: {
        labels: ['2023','2024','2025','2026','2027','2028','2029','2030','2031','2032','2033','2034','2035','2036','2037','2038','2040'],
        datasets: [
            { label: 'Scénario de base (sans réforme)', data: [15.8,14.9,13.8,12.6,11.2,9.7,8.0,6.2,4.4,2.8,1.5,0.5,0,null,null,null,null], borderColor: P.red, backgroundColor: alphaColor(P.red,0.05), tension:0.3, fill:true, pointRadius:2, borderWidth:2 },
            { label: 'Scénario réforme fiscale', data: [15.8,15.0,14.2,13.5,12.8,12.0,11.3,10.6,9.9,9.3,8.7,8.2,7.8,7.5,7.2,6.9,6.5], borderColor: P.orange, backgroundColor:'transparent', tension:0.3, pointRadius:2, borderWidth:2, borderDash:[6,3] },
            { label: 'Scénario Greater Sunrise', data: [15.8,14.9,14.0,13.5,13.8,15.2,17.0,18.5,19.8,20.5,21.0,21.4,21.7,21.9,22.0,22.0,21.8], borderColor: P.green, backgroundColor: alphaColor(P.green,0.04), tension:0.3, fill:false, pointRadius:2, borderWidth:2 }
        ]
    },
    options: { responsive:true, maintainAspectRatio:false, interaction:{mode:'index',intersect:false}, plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}}, scales:{y:{min:0,ticks:{callback:v=>v+'Md$'},grid:{color:g}},x:{grid:{color:g}}} }
});

// ── PILIER 4 ────────────────────────────────────────────
new Chart(document.getElementById('tradeBalance'), {
    type: 'bar',
    data: {
        labels: ['2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021','2022','2023'],
        datasets: [
            { label: 'Exportations (M$)', data: [1542,2052,2682,1748,1628,802,492,388,462,324,198,248,680,620], backgroundColor: alphaColor(P.blue,0.65), borderRadius:2 },
            { label: 'Importations (M$)', data: [-410,-490,-602,-621,-690,-658,-610,-580,-625,-648,-545,-590,-680,-750], backgroundColor: alphaColor(P.red,0.65), borderRadius:2 },
            { type:'line', label: 'Solde commercial (M$)', data: [1132,1562,2080,1127,938,144,-118,-192,-163,-324,-347,-342,0,-130], borderColor: P.gold, backgroundColor:'transparent', tension:0.3, pointRadius:3, borderWidth:2 }
        ]
    },
    options: { responsive:true, maintainAspectRatio:false, interaction:{mode:'index',intersect:false}, plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}}, scales:{y:{ticks:{callback:v=>v+'M$'},grid:{color:g}},x:{grid:{color:g}}} }
});

new Chart(document.getElementById('tradePartners'), {
    type: 'bar',
    data: {
        labels: ['Australie', 'Indonésie', 'Singapour', 'Chine', 'Portugal', 'Japon', 'Corée', 'Autres'],
        datasets: [
            { label: 'Exports vers (M$)', data: [568,18,15,8,5,2,1,18], backgroundColor: alphaColor(P.blue,0.7), borderRadius:2 },
            { label: 'Imports depuis (M$)', data: [45,285,95,110,22,18,15,160], backgroundColor: alphaColor(P.red,0.6), borderRadius:2 }
        ]
    },
    options: { responsive:true, maintainAspectRatio:false, indexAxis:'y', interaction:{mode:'index',intersect:false}, plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}}, scales:{x:{grid:{color:g}},y:{grid:{color:g}}} }
});

new Chart(document.getElementById('currentAccount'), {
    type: 'bar',
    data: {
        labels: ['2015','2016','2017','2018','2019','2020','2021','2022','2023'],
        datasets: [
            { label: 'Balance commerciale (% PIB np)', data: [-38,-42,-40,-43,-48,-50,-48,-42,-44], backgroundColor: alphaColor(P.red,0.6), borderRadius:2 },
            { label: 'Revenus primaires pétroliers', data: [12,8,9,12,10,6,9,25,22], backgroundColor: alphaColor(P.gold,0.6), borderRadius:2 },
            { label: 'Transferts courants (APD+)', data: [8,8,9,8,9,10,10,9,8], backgroundColor: alphaColor(P.green,0.6), borderRadius:2 },
            { type:'line', label: 'Solde compte courant (%)', data: [-18,-26,-22,-23,-29,-34,-29,-8,-14], borderColor: P.blue, backgroundColor:'transparent', tension:0.3, pointRadius:4, borderWidth:2.5 }
        ]
    },
    options: { responsive:true, maintainAspectRatio:false, interaction:{mode:'index',intersect:false}, plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}}, scales:{y:{ticks:{callback:v=>v+'%'},grid:{color:g}},x:{grid:{color:g}}} }
});

// ── PILIER 5 ────────────────────────────────────────────
new Chart(document.getElementById('creditChart'), {
    type: 'bar',
    data: {
        labels: ['2012','2014','2016','2017','2018','2019','2020','2021','2022','2023'],
        datasets: [
            { label: 'Crédit ménages', data: [48,82,105,118,128,136,121,130,148,162], backgroundColor: alphaColor(P.blue,0.7), borderRadius:2 },
            { label: 'Crédit entreprises', data: [42,68,88,102,115,122,108,118,136,148], backgroundColor: alphaColor(P.teal,0.7), borderRadius:2 },
            { label: 'Microfinance', data: [12,18,22,26,30,33,28,32,38,42], backgroundColor: alphaColor(P.green,0.7), borderRadius:2 }
        ]
    },
    options: { responsive:true, maintainAspectRatio:false, interaction:{mode:'index',intersect:false}, plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}}, scales:{x:{stacked:true,grid:{color:g}},y:{stacked:true,ticks:{callback:v=>v+'M$'},grid:{color:g}}} }
});

new Chart(document.getElementById('ratesChart'), {
    type: 'line',
    data: {
        labels: ['2018','2019','2020','2021','2022','2023'],
        datasets: [
            { label: 'Taux débiteur moyen (%)', data: [16.2,15.8,14.9,14.2,13.8,12.5], borderColor: P.red, backgroundColor: alphaColor(P.red,0.06), tension:0.3, fill:true, pointRadius:4, borderWidth:2 },
            { label: 'Taux créditeur moyen (%)', data: [0.8,0.7,0.5,0.4,0.6,0.8], borderColor: P.green, backgroundColor: alphaColor(P.green,0.06), tension:0.3, fill:true, pointRadius:4, borderWidth:2 },
            { label: 'Spread (%)', data: [15.4,15.1,14.4,13.8,13.2,11.7], borderColor: P.orange, backgroundColor:'transparent', tension:0.3, borderDash:[6,3], pointRadius:3, borderWidth:2 }
        ]
    },
    options: { responsive:true, maintainAspectRatio:false, interaction:{mode:'index',intersect:false}, plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}}, scales:{y:{ticks:{callback:v=>v+'%'},grid:{color:g}},x:{grid:{color:g}}} }
});

new Chart(document.getElementById('prudentialChart'), {
    type: 'line',
    data: {
        labels: ['2019','2020','2021','2022','2023'],
        datasets: [
            { label: 'CAR — Ratio fonds propres (%)', data: [28.5,26.8,27.2,28.9,29.4], borderColor: P.green, backgroundColor:'transparent', tension:0.3, pointRadius:5, borderWidth:2 },
            { label: 'NPL / Total prêts (%)', data: [6.8,7.2,6.9,6.2,5.8], borderColor: P.red, backgroundColor:'transparent', tension:0.3, pointRadius:5, borderDash:[6,3], borderWidth:2 },
            { label: 'ROA (%)', data: [2.1,1.4,1.8,2.3,2.5], borderColor: P.gold, backgroundColor:'transparent', tension:0.3, pointRadius:5, borderWidth:2 },
            { label: 'Ratio liquidité (%)', data: [65,72,68,62,60], borderColor: P.blue, backgroundColor:'transparent', tension:0.3, pointRadius:5, borderDash:[4,2], borderWidth:2 }
        ]
    },
    options: { responsive:true, maintainAspectRatio:false, interaction:{mode:'index',intersect:false}, plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}}, scales:{y:{grid:{color:g},ticks:{callback:v=>v+'%'}},x:{grid:{color:g}}} }
});

// ── PILIER 6 ────────────────────────────────────────────
new Chart(document.getElementById('hazardRadar'), {
    type: 'radar',
    data: {
        labels: ['Glissements terrain', 'Inondations', 'Cyclones', 'Sécheresse', 'Séismes', 'Tsunamis', 'Montée mer', 'Feux forêts'],
        datasets: [
            { label: 'Exposition (prob. × intensité)', data: [92,82,62,68,58,45,72,55], borderColor: P.red, backgroundColor: alphaColor(P.red,0.1), borderWidth:2, pointBackgroundColor: P.red },
            { label: 'Capacité de réponse (inverse)', data: [28,35,42,30,38,25,32,40], borderColor: P.blue, backgroundColor: alphaColor(P.blue,0.05), borderWidth:1.5, borderDash:[5,3], pointBackgroundColor: P.blue }
        ]
    },
    options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}}, scales:{r:{min:0,max:100,grid:{color:g},angleLines:{color:g},pointLabels:{font:{size:10}}}} }
});

new Chart(document.getElementById('climateChart'), {
    type: 'bar',
    data: {
        labels: ['1980','1985','1990','1995','2000','2005','2010','2015','2018','2020','2022','2023'],
        datasets: [
            { label: 'Anomalie T° (°C)', data: [-0.1,0.0,0.1,0.2,0.4,0.5,0.6,0.9,1.0,1.1,1.2,1.4], backgroundColor: (ctx) => ctx.raw >= 0 ? alphaColor(P.red,0.65) : alphaColor(P.blue,0.55), borderRadius:2, order:2 },
            { type:'line', label: 'Anomalie précipitations (mm/mois)', data: [8,-5,12,-18,6,-22,-8,-30,-15,-12,-25,-18], borderColor: P.blue, backgroundColor:'transparent', tension:0.3, pointRadius:3, borderWidth:2, order:1 }
        ]
    },
    options: { responsive:true, maintainAspectRatio:false, interaction:{mode:'index',intersect:false}, plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}}, scales:{y:{grid:{color:g}},x:{grid:{color:g}}} }
});

new Chart(document.getElementById('disasterChart'), {
    type: 'bar',
    data: {
        labels: ['2000-04','2005-09','2010-14','2015-19','2020','2021','2022','2023'],
        datasets: [
            { label: 'Événements enregistrés', data: [8,12,18,22,5,6,4,5], backgroundColor: alphaColor(P.blue,0.65), borderRadius:2, yAxisID:'y' },
            { type:'line', label: 'Pertes éco. estimées (% PIB)', data: [0.4,0.6,1.1,0.9,2.8,1.4,0.6,0.5], borderColor: P.red, backgroundColor:'transparent', tension:0.3, pointRadius:4, borderWidth:2, yAxisID:'y1' }
        ]
    },
    options: {
        responsive:true, maintainAspectRatio:false,
        interaction:{mode:'index',intersect:false},
        plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}},
        scales:{
            y:{grid:{color:g},position:'left',title:{display:true,text:'Nb événements',color:'#8a8780',font:{size:10}}},
            y1:{grid:{display:false},position:'right',ticks:{callback:v=>v+'%'},title:{display:true,text:'% PIB',color:'#8a8780',font:{size:10}}}
        }
    }
});

new Chart(document.getElementById('energyChart'), {
    type: 'bar',
    data: {
        labels: ['Diesel/fuel', 'Solaire PV', 'Hydroélectricité', 'Bioénergie', 'Autre'],
        datasets: [
            { label: 'Mix actuel 2023 (%)', data: [86,9,3,1,1], backgroundColor: alphaColor(P.red,0.65), borderRadius:2 },
            { label: 'Objectif NDC 2030 (%)', data: [45,35,12,5,3], backgroundColor: alphaColor(P.green,0.65), borderRadius:2 }
        ]
    },
    options: {
        responsive:true, maintainAspectRatio:false,
        interaction:{mode:'index',intersect:false},
        plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:12}}},
        scales:{y:{ticks:{callback:v=>v+'%'},grid:{color:g},max:100},x:{grid:{color:g}}}
    }
});
</script>
</body>
</html>
