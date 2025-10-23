import urllib.request
import json
import csv
import re
import time

# Configuration
cookie = "XXXXXXX"

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
