import urllib.request
import json
import csv
import re
import time

# Configuration
cookie = "_vwo_uuid_v2=D34FE80A835AF0AA0A202D11D2A422214|8b60199529b27edf0ebae917932d4eee; _vwo_uuid=J2AF9B133A2946A8AC493FA516802D2A9; _vwo_ds=3%241760012774%3A92.89453516%3A%3A; _gcl_au=1.1.1822995109.1760012776; _ga=GA1.1.1022074758.1760012776; OptanonAlertBoxClosed=2025-10-09T12:26:18.695Z; _mkto_trk=id:691-SMD-711&token:_mch-tdsynnex.com-3df09f984d8c42dc6763e4054d3ada2f; visid_incap_1823732=rcyx3tdGRHSyKwe+K82BJ/Dm52gAAAAAQUIPAAAAAAC2UGzpiMz6XLVRlK17NFWW; visid_incap_998278=zadZwjHHTliTk2RgbmDO0/Dm52gAAAAAQUIPAAAAAABRT3nJ4bWZWbPATMCPh7JN; visid_incap_2641754=vnVTmoDYRgal0uDzA82K6fvm52gAAAAAQUIPAAAAAABfuQTNb45qWgwQGS2Y34IL; dtCookie=v_4_srv_8_sn_D8BA3D85218B42086A484E556667D242_perc_100000_ol_0_mul_1_app-3Aaad28fc6d3730d92_1_rcs-3Acss_0; rxVisitor=1760098075697988A693AMO84S1B3UA1JFQSBU80KJ9UA; nlbi_998278=0TolHYfBYlBQ7LlNejQ4wAAAAADqVX+M3zBy3jDkD7OQFX2H; nlbi_998278_2867207=KRXeIzue9gUIpEnRejQ4wAAAAAA0Y6pMg1JDzOqSFVTb4gHW; _ga_LQGNR10P17=GS2.1.s1760102879$o4$g1$t1760104478$j60$l0$h563226090; incap_ses_975_998278=j+zzDjcUsVa3cLhVduWHDbcV7mgAAAAApC1G63nv0mSOphprW7uICg==; _vis_opt_s=2%7C; _vis_opt_test_cookie=1; nlbi_2641754_2622349=Xn/1aSWxeAPcKwiMIMbaGgAAAAC7nf189qkBpEqhITXf+JXb; incap_ses_978_2641754=J6ArGnsSxR4/skfs742SDaoc7mgAAAAAN5A3meKqGlu8cfxKElZcDw==; incap_ses_978_998278=2kQlckP0mg7fvKLt742SDWdA7mgAAAAAWlWEirLphKFmxOZfZO3ABA==; incap_ses_978_1823732=sJvzKDIpTCeytB3w742SDZSA7mgAAAAA2oMf6ekhrdsyx4li5jtd2w==; incap_ses_975_1823732=CwUHPFNElxPIp5VfduWHDadc72gAAAAAO41Jx8ququAOoSZNh6x7OA==; incap_ses_969_1823732=4eZ5B0FVIyZUl7w8fJRyDYtl72gAAAAATD9OqyOxyDr7z+ZTK635Qg==; incap_ses_969_998278=IJJgDXeeXQJAFsc8fJRyDWdm72gAAAAA/hDKdGA/lPh4NltzgUB2Iw==; incap_ses_975_2641754=Y2+LMxuu9W9/jvhfduWHDW1m72gAAAAANudDZefoc7p5xoMMry1bIw==; dtSa=-; _vwo_sn=507004%3A5; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Oct+15+2025+11%3A16%3A58+GMT%2B0200+(heure+d%E2%80%99%C3%A9t%C3%A9+d%E2%80%99Europe+centrale)&version=202501.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=0d1d88e6-b784-4088-87e4-448d81accf7f&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0004%3A0%2CC0001%3A1%2CC0003%3A0%2CC0002%3A0%2CC0012%3A0&intType=undefined&geolocation=FR%3BIDF&AwaitingReconsent=false; rxvt=1760521618330|1760519424114; dtPC=8$119814897_183h31vPKKBRRJFKUARNMJIUKNCFUOPBLGEMTMW-0e0"

headers = {
    "Content-Type": "application/json",
    "Cookie": cookie,
    "Accept-Language": "fr-FR",
    "Site": "FR",
    "Consumer": "INTOUCH",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

URL_SEARCH = "https://intouch.tdsynnex.com/ui/ui-intouch-search/v1/public/fullsearch"
URL_PRICE = "https://intouch.tdsynnex.com/ui/ui-intouch-search/v3/public/price"

# Catégories à scraper
CATEGORIES = [
    ("FCS_SUBCLASS_PCALLIN1_COMDESK", "PC All-in-One"),
    ("FCS_SUBCLASS_KEYBOARD_KEYBMICE", "Claviers"),
    ("FCS_SUBCLASS_MONITORS_PERMONIT", "Moniteurs"),
    ("FCS_SUBCLASS_EXTSSD_PERSTOR", "SSD Externes"),
    ("FCS_SUBCLASS_MULTIFU_PRIMULTFU", "Multifonctions"),
    ("FCS_SUBCLASS_MEMORY_COMPCOMPU", "Mémoires"),
    ("FCS_SUBCLASS_NOTEBOOKS_COMPORT", "Notebooks"),
    ("FCS_SUBCLASS_NOTEBWS_COMPORT", "Notebooks WS"),
    ("FCS_SUBCLASS_HUBSWITCH_NWLAN", "Hub/Switch"),
    ("FCS_SUBCLASS_TELMOB_TELMOBILE", "Téléphonie Mobile"),
    ("FCS_CLASS_COMDESK_COMPUTERS", "Ordinateurs de Bureau")
]

def post_json(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    return json.loads(urllib.request.urlopen(req).read())

def parse_price(value):
    if value in (None, "", "N/A", "-.--"):
        return ""
    s = str(value).strip().replace("\u202f", "").replace("\u00a0", "").replace(" ", "").replace(",", ".")
    return float(s) if re.match(r"^-?\d+(?:\.\d+)?$", s) else ""

def get_products(response):
    """Extrait les produits de la réponse"""
    if not isinstance(response, dict):
        return []
    return response.get("products", []) or response.get("content", {}).get("products", [])

def scrape_category(category_value_id, category_name):
    """Scrape tous les produits d'une catégorie"""
    print(f"\n{category_name} ({category_value_id})")
    
    produits, page = [], 1
    while True:
        data = {
            "page": page,
            "pageSize": 100,
            "searchType": "Category",
            "getRefinements": True,
            "sort": {"type": "STOCK"},
            "refinementGroups": [{
                "group": "Categories",
                "refinements": [{"id": "FCS", "valueId": category_value_id}]
            }]
        }
        
        try:
            response = post_json(URL_SEARCH, data)
            produits_page = get_products(response)
            if not produits_page:
                break
            produits.extend(produits_page)
            print(f"  Page {page}: {len(produits_page)} produits")
            page += 1
            time.sleep(1)
        except Exception as e:
            print(f"  Erreur page {page}: {e}")
            break
    
    print(f"  ✅ Total: {len(produits)} produits")
    return produits

# ===== SCRIPT PRINCIPAL =====

print("=== SCRAPER 11 CATÉGORIES ===")
print(f"Catégories: {len(CATEGORIES)}")

# Scraping
tous_produits = []
for i, (value_id, name) in enumerate(CATEGORIES, 1):
    print(f"\n[{i}/{len(CATEGORIES)}] {name}")
    try:
        produits = scrape_category(value_id, name)
        for p in produits:
            p['categorie'] = name
        tous_produits.extend(produits)
    except Exception as e:
        print(f"  ❌ Erreur: {e}")

print(f"\nTotal: {len(tous_produits)} produits")

if not tous_produits:
    print("❌ Aucun produit trouvé")
    exit()

# Prix
print("\nRécupération des prix...")
prix_data = {}
for i in range(0, len(tous_produits), 100):
    batch_ids = [p["id"] for p in tous_produits[i:i+100]]
    try:
        prix_data.update(post_json(URL_PRICE, {"ids": batch_ids}))
        print(f"  Lot {i//100 + 1}: {len(batch_ids)} produits")
        time.sleep(1)
    except Exception as e:
        print(f"  Erreur lot {i//100 + 1}: {e}")

# CSV
print("\nGénération CSV...")
specs = {s["name"] for p in tous_produits for s in p.get("mainSpecifications", []) if s.get("name") and s.get("value")}
spec_cols = sorted(specs)

rows = []
for p in tous_produits:
    specs_dict = {s["name"]: s["value"] for s in p.get("mainSpecifications", []) if s.get("name") and s.get("value")}
    prix = parse_price(prix_data.get(p["id"], {}).get("listPrice", "N/A"))
    row = {
        "id": p["id"],
        "nom": p["displayName"],
        "marque": p.get("manufacturerGA", ""),
        "caracteristiques": p.get("description", ""),
        "prix": prix,
        "categorie": p.get("categorie", "")
    }
    for col in spec_cols:
        row[col] = specs_dict.get(col, "")
    rows.append(row)

with open("produits_toutes_categories.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"\n✅ Terminé !")
print(f"📁 Fichier: produits_toutes_categories.csv")
print(f"📊 Produits: {len(rows)}")
print(f"📋 Colonnes: {len(spec_cols)} spécifications + 6 colonnes de base")

# Résumé
print(f"\n=== RÉSUMÉ ===")
for cat in sorted(set(p['categorie'] for p in tous_produits)):
    count = sum(1 for p in tous_produits if p['categorie'] == cat)
    print(f"  {cat}: {count} produits")
