import urllib.request
import json

# Cookie - REMPLACER PAR VOTRE COOKIE
cookie = "_vwo_uuid_v2=D34FE80A835AF0AA0A202D11D2A422214|8b60199529b27edf0ebae917932d4eee; _vwo_uuid=J2AF9B133A2946A8AC493FA516802D2A9; _vwo_ds=3%241760012774%3A92.89453516%3A%3A; _vis_opt_s=1%7C; _gcl_au=1.1.1822995109.1760012776; _ga=GA1.1.1022074758.1760012776; OptanonAlertBoxClosed=2025-10-09T12:26:18.695Z; _mkto_trk=id:691-SMD-711&token:_mch-tdsynnex.com-3df09f984d8c42dc6763e4054d3ada2f; visid_incap_1823732=rcyx3tdGRHSyKwe+K82BJ/Dm52gAAAAAQUIPAAAAAAC2UGzpiMz6XLVRlK17NFWW; visid_incap_998278=zadZwjHHTliTk2RgbmDO0/Dm52gAAAAAQUIPAAAAAABRT3nJ4bWZWbPATMCPh7JN; visid_incap_2641754=vnVTmoDYRgal0uDzA82K6fvm52gAAAAAQUIPAAAAAABfuQTNb45qWgwQGS2Y34IL; dtCookie=v_4_srv_8_sn_D8BA3D85218B42086A484E556667D242_perc_100000_ol_0_mul_1_app-3Aaad28fc6d3730d92_1_rcs-3Acss_0; rxVisitor=1760098075697988A693AMO84S1B3UA1JFQSBU80KJ9UA; nlbi_998278=0TolHYfBYlBQ7LlNejQ4wAAAAADqVX+M3zBy3jDkD7OQFX2H; nlbi_998278_2867207=KRXeIzue9gUIpEnRejQ4wAAAAAA0Y6pMg1JDzOqSFVTb4gHW; incap_ses_978_998278=zpO9Hn2EsiZqTTHJ742SDeEJ6WgAAAAAAaltT0E+WTMDXI27XeOWDg==; incap_ses_978_2641754=d//eFdK7UFgCjjHJ742SDeYJ6WgAAAAAt92B5m05PQvetueh/Rm0Jg==; _ga_LQGNR10P17=GS2.1.s1760102879$o4$g1$t1760104478$j60$l0$h563226090; dtSa=-; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Oct+10+2025+16%3A02%3A09+GMT%2B0200+(heure+d%E2%80%99%C3%A9t%C3%A9+d%E2%80%99Europe+centrale)&version=202501.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=0d1d88e6-b784-4088-87e4-448d81accf7f&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0004%3A0%2CC0001%3A1%2CC0003%3A0%2CC0002%3A0%2CC0012%3A0&intType=undefined&geolocation=FR%3BIDF&AwaitingReconsent=false; incap_ses_978_1823732=QNuXLudRqiQ5DhLL742SDSc86WgAAAAAOFM0Z9mfPDNcesx7uvTdlQ==; incap_ses_975_1823732=gZc8I4yN9R+hYrA4duWHDTY96mgAAAAAS1DFwJrxDWqOQrnOMarnlA==; incap_ses_975_998278=aszbcS5W+kO3LtQ4duWHDVdC6mgAAAAAkb6WgMAWeRfVmzS+oD+kzQ==; rxvt=1760184672593|1760181560400; dtPC=8$382870965_253h23vGFWLCIAPVRAFHRGUKMMLHHNABOHNDKQF-0e0"

# URLs
url_produits = "https://intouch.tdsynnex.com/ui/ui-intouch-search/v1/public/fullsearch"
url_prix = "https://intouch.tdsynnex.com/ui/ui-intouch-search/v3/public/price"

# Headers
headers = {
    "Content-Type": "application/json",
    "Cookie": cookie,
    "Accept-Language": "fr-FR",
    "Site": "FR",
    "Consumer": "INTOUCH"
}

print("Récupération des produits...")

# Récupérer TOUS les produits avec pagination
tous_produits = []
page = 1

while True:
    print(f"Page {page}...")
    
    data = {
        "page": page,
        "pageSize": 100,
        "searchType": "Category",
        "getRefinements": True,
        "refinementGroups": [{
            "group": "Categories",
            "refinements": [{
                "id": "FCS",
                "valueId": "FCS_SUBCLASS_EXTSSD_PERSTOR"
            }]
        }]
    }
    
    req = urllib.request.Request(url_produits, data=json.dumps(data).encode(), headers=headers)
    reponse = urllib.request.urlopen(req)
    donnees = json.loads(reponse.read())
    produits_page = donnees["products"]
    
    if len(produits_page) == 0:
        break
    
    tous_produits.extend(produits_page)
    print(f"Page {page}: +{len(produits_page)} produits (Total: {len(tous_produits)})")
    
    page += 1

print(f"Trouvé {len(tous_produits)} produits au total")

# Récupérer les prix
ids = [p["id"] for p in tous_produits]
data_prix = {"ids": ids}

req_prix = urllib.request.Request(url_prix, data=json.dumps(data_prix).encode(), headers=headers)
reponse_prix = urllib.request.urlopen(req_prix)
prix_data = json.loads(reponse_prix.read())

print("Récupération des prix...")

# Créer les produits finaux
produits_finaux = []

for produit in tous_produits:
    id_prod = produit["id"]
    nom = produit["displayName"]
    marque = produit["manufacturerGA"]
    
    # Caractéristiques détaillées
    caracteristiques = produit.get("description", "")
    
    # Prix avec correction des caractères invisibles
    prix_str = prix_data[id_prod]["listPrice"]
    if prix_str != "N/A":
        # Supprimer tous les caractères invisibles et espaces
        prix_clean = prix_str.replace(" ", "").replace(",", ".").replace("\u202f", "").replace("\u00a0", "")
        prix = float(prix_clean)
    else:
        prix = None
    
    # Ajouter le produit
    produits_finaux.append({
        "id": id_prod,
        "nom": nom,
        "marque": marque,
        "caracteristiques": caracteristiques,
        "prix": prix
    })

# Sauvegarder
with open("produits.json", "w", encoding="utf-8") as f:
    json.dump(produits_finaux, f, ensure_ascii=False, indent=2)

print(f"Terminé ! {len(produits_finaux)} produits sauvegardés")
print("Fichier: produits.json")