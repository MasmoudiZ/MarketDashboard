# marketdash/data/macro_map.py
MACRO_GROUPS = {
    "Actions Monde": [
        ("MSCI WORLD", "URTH"),
        ("MSCI World EUR", "EUNL.DE"),
        ("Vix Index", "^VIX"),
    ],
    "Actions États-Unis": [
        ("S&P 500 INDEX", "^GSPC"),
        ("RUSSELL 2000 INDEX", "^RUT"),
        ("NASDAQ COMPOSITE", "^IXIC"),
    ],
    "Actions Europe": [
        ("Euro Stoxx 50 Pr", "^STOXX50E"),
        ("STXE 600 (EUR) Pr", "^STOXX"),
        ("DAX INDEX", "^GDAXI"),
        ("CAC 40 INDEX", "^FCHI"),
        ("CAC Small Index", "^SBF120"),
        ("CAC Mid & Small INDEX", "CM100.PA"),
        ("FTSE MIB INDEX", "FTSEMIB.MI"),
        ("FTSE 100 INDEX", "^FTSE"),
    ],
    "Actions Asie / Emergents": [
        ("NIKKEI 225", "^N225"),
        ("HANG SENG INDEX", "^HSI"),
        ("CSI 300 INDEX", "000300.SS"),
        ("BRAZIL IBOVESPA INDEX", "^BVSP"),
    ],
    "Obligations": [
        ("US IG", "LQD"),
        ("US HY", "HYG"),
        ("EU IG", "IEAC.L"),
        ("EU HY", "IHYU.L"),
    ],
    "Taux": [
        ("US 10 Y", "^TNX"),
        ("Bund 10", "IBGL.L"),
        ("French 10Y", "EUNA.L"),
        ("Japon 10 Y", "2840.T"),
        ("UK 10Y", "IGLT.L"),
    ],
    "Changes": [
        ("EUR/USD", "EURUSD=X"),
        ("EUR/CNY", "EURCNY=X"),
        ("EUR/CHF", "EURCHF=X"),
        ("EUR/JPY", "EURJPY=X"),
        ("EUR/GBP", "EURGBP=X"),
    ],
    "Matières 1ères": [
        ("Or", "GC=F"),
        ("Vaneck Gold Miners", "GDX"),
        ("Bitcoin", "BTC-USD"),
        ("Pétrole", "CL=F"),
        ("Argent", "SI=F"),
        ("Agriculture", "DBA"),
    ],
}
