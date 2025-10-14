import urllib.request
import json
import csv

# Paramètres
cookie = "_vwo_uuid_v2=D34FE80A835AF0AA0A202D11D2A422214|8b60199529b27edf0ebae917932d4eee; _vwo_uuid=J2AF9B133A2946A8AC493FA516802D2A9; _vwo_ds=3%241760012774%3A92.89453516%3A%3A; _gcl_au=1.1.1822995109.1760012776; _ga=GA1.1.1022074758.1760012776; OptanonAlertBoxClosed=2025-10-09T12:26:18.695Z; _mkto_trk=id:691-SMD-711&token:_mch-tdsynnex.com-3df09f984d8c42dc6763e4054d3ada2f; visid_incap_1823732=rcyx3tdGRHSyKwe+K82BJ/Dm52gAAAAAQUIPAAAAAAC2UGzpiMz6XLVRlK17NFWW; visid_incap_998278=zadZwjHHTliTk2RgbmDO0/Dm52gAAAAAQUIPAAAAAABRT3nJ4bWZWbPATMCPh7JN; visid_incap_2641754=vnVTmoDYRgal0uDzA82K6fvm52gAAAAAQUIPAAAAAABfuQTNb45qWgwQGS2Y34IL; dtCookie=v_4_srv_8_sn_D8BA3D85218B42086A484E556667D242_perc_100000_ol_0_mul_1_app-3Aaad28fc6d3730d92_1_rcs-3Acss_0; rxVisitor=1760098075697988A693AMO84S1B3UA1JFQSBU80KJ9UA; nlbi_998278=0TolHYfBYlBQ7LlNejQ4wAAAAADqVX+M3zBy3jDkD7OQFX2H; nlbi_998278_2867207=KRXeIzue9gUIpEnRejQ4wAAAAAA0Y6pMg1JDzOqSFVTb4gHW; _ga_LQGNR10P17=GS2.1.s1760102879$o4$g1$t1760104478$j60$l0$h563226090; incap_ses_978_998278=1mJpWIz2swGlkDrj742SDbbw7GgAAAAAVYLzxPlzhkI8gPnmKYecJA==; incap_ses_978_2641754=ik1ePQrnnGzrnjrj742SDbfw7GgAAAAApll2gPZ3Q/kfqtrZfLtlYg==; incap_ses_978_1823732=kC8iEZ5kCCYPrNvl742SDbEy7WgAAAAA9aBU/b24kBVm9tdKMSkn4w==; incap_ses_975_1823732=FYx4djMq3DNzxmBVduWHDZ0N7mgAAAAA+Dq/R3CibJy6j3BUrhuSrQ==; incap_ses_975_998278=j+zzDjcUsVa3cLhVduWHDbcV7mgAAAAApC1G63nv0mSOphprW7uICg==; dtSa=-; _vis_opt_s=2%7C; _vis_opt_test_cookie=1; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Oct+14+2025+11%3A19%3A55+GMT%2B0200+(heure+d%E2%80%99%C3%A9t%C3%A9+d%E2%80%99Europe+centrale)&version=202501.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=0d1d88e6-b784-4088-87e4-448d81accf7f&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0004%3A0%2CC0001%3A1%2CC0003%3A0%2CC0002%3A0%2CC0012%3A0&intType=undefined&geolocation=FR%3BIDF&AwaitingReconsent=false; _vwo_sn=420818%3A3; rxvt=1760435463677|1760431519735; dtPC=8$33661984_16h26vCOUHPFGLOTGPJOPTORMUHVJMNDVRCHSQ-0e0"
headers = {
    "Content-Type": "application/json",
    "Cookie": cookie,
    "Accept-Language": "fr-FR",
    "Site": "FR",
    "Consumer": "INTOUCH"
}
URL_SEARCH = "https://intouch.tdsynnex.com/ui/ui-intouch-search/v1/public/fullsearch"
URL_PRICE = "https://intouch.tdsynnex.com/ui/ui-intouch-search/v3/public/price"

# Catégorie: Ordinateurs tout-en-un
CATEGORY_ID = "FCS"
CATEGORY_VALUE_ID = "FCS_SUBCLASS_PCALLIN1_COMDESK"
PAGE_SIZE = 50
SORT_TYPE = "STOCK"
OUTPUT_CSV = "produits_allinone.csv"

def post_json(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    return json.loads(urllib.request.urlopen(req).read())

# 1) Produits par pagination
tous_produits, page = [], 1
while True:
    data = {
        "page": page,
        "pageSize": PAGE_SIZE,
        "searchType": "Category",
        "getRefinements": True,
        "sort": {"type": SORT_TYPE},
        "refinementGroups": [{
            "group": "Categories",
            "refinements": [{"id": CATEGORY_ID, "valueId": CATEGORY_VALUE_ID}]
        }]
    }
    produits_page = post_json(URL_SEARCH, data)["products"]
    if not produits_page:
        break
    tous_produits.extend(produits_page)
    page += 1

# 2) Prix
ids = [p["id"] for p in tous_produits]
prix_data = post_json(URL_PRICE, {"ids": ids})

# 3) Colonnes de spécifications (toutes uniques)
specs_set = {
    s["name"]
    for p in tous_produits
    for s in p.get("mainSpecifications", [])
    if s.get("name") and s.get("value")
}
spec_cols = sorted(specs_set)

# 4) Lignes CSV
rows = []
for p in tous_produits:
    specs = {s["name"]: s["value"] for s in p.get("mainSpecifications", []) if s.get("name") and s.get("value")}
    prix_str = prix_data[p["id"]]["listPrice"]
    prix = "" if prix_str == "N/A" else float(prix_str.replace(" ", "").replace(",", ".").replace("\u202f", "").replace("\u00a0", ""))
    row = {
        "id": p["id"],
        "nom": p["displayName"],
        "marque": p["manufacturerGA"],
        "caracteristiques": p.get("description", ""),
        "prix": prix
    }
    for col in spec_cols:
        row[col] = specs.get(col, "")
    rows.append(row)

# 5) Écriture CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    if rows:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

print(f"Terminé ! {len(rows)} produits sauvegardés en CSV: {OUTPUT_CSV}")


