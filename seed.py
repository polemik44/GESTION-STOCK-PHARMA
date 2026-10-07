"""
seed.py
Peuple la base de données avec un jeu de données de démo réaliste.
À lancer isolément avec : python seed.py
 
Date de référence utilisée pour construire ce jeu de données : 2026-10-05.
Toutes les dates ci-dessous sont écrites en clair (AAAA-MM-JJ) ; le commentaire
à côté de chaque lot rappelle juste le contexte (périmé / proche / normal).
"""

from DATABASE import connecter_bd
 
 
def peupler_donnees_demo():
    conn, curs = connecter_bd()
 
    # --- 1. Vider les tables existantes ---
    curs.execute("DELETE FROM SORTIES")
    curs.execute("DELETE FROM LOTS")
    curs.execute("DELETE FROM ENTREES")
    curs.execute("DELETE FROM produits")
    # Remet les compteurs AUTOINCREMENT à zéro pour avoir des ID prévisibles (LOT-0001, etc.)
    curs.execute(
        "DELETE FROM sqlite_sequence WHERE name IN ('ENTREES','LOTS','SORTIES','produits')"
    )
    conn.commit()
 
    # --- 2. Produits (8 produits pharma) ---
    # (nom, dosage en mg, seuil d'alerte)
    produits = [
        ("Paracétamol", 500, 50),
        ("Ibuprofène", 200, 30),
        ("Amoxicilline", 500, 40),
        ("Doliprane", 1000, 40),
        ("Aspirine", 500, 25),
        ("Oméprazole", 20, 20),
        ("Ventoline", 100, 15),
        ("Insuline Lantus", 100, 10),
    ]
 
    for nom, dosage, seuil in produits:
        curs.execute(
            "INSERT INTO produits (nomProduit, dosage, SEUIL, STOCK) VALUES (?, ?, ?, 0)",
            (nom, dosage, seuil),
        )
    conn.commit()
 
    # Récupère les id générés pour les produits
    curs.execute("SELECT id, nomProduit FROM produits")
    id_produit = {nom: pid for pid, nom in curs.fetchall()}
 
    # --- 3. Lots par produit : dates écrites en clair (AAAA-MM-JJ) ---
    # Chaque tuple : (quantite, date_peremption, date_entree)
    lots_par_produit = {
        "Paracétamol": [
            (200, "2027-08-20", "2026-07-01"),  # normal, loin devant
            (80,  "2026-03-15", "2025-09-01"),  # déjà périmé
            (15,  "2026-10-22", "2026-09-20"),  # périme bientôt (~17 jours)
            (0,   "2027-01-10", "2026-06-15"),  # épuisé (quantité à 0)
        ],
        "Ibuprofène": [
            (10, "2027-05-01", "2026-08-25"),   # stock bas (total sous le seuil de 30)
            (60, "2027-12-01", "2026-09-28"),   # normal
            (25, "2026-10-18", "2026-09-30"),   # périme bientôt (~13 jours)
        ],
        "Amoxicilline": [
            (150, "2027-04-10", "2026-09-05"),  # normal
            (90,  "2027-11-15", "2026-09-18"),  # normal
            (60,  "2026-10-29", "2026-09-25"),  # périme bientôt (~24 jours)
            (40,  "2026-09-27", "2026-06-10"),  # déjà périmé (~8 jours)
        ],
        "Doliprane": [
            (300, "2027-09-15", "2026-08-20"),  # normal
            (120, "2028-01-01", "2026-09-30"),  # normal
            (0,   "2027-03-01", "2026-06-01"),  # épuisé
        ],
        "Aspirine": [
            (8,  "2027-08-01", "2026-09-10"),   # stock bas (sous le seuil de 25)
            (50, "2026-10-23", "2026-09-27"),   # périme bientôt (~18 jours)
        ],
        "Oméprazole": [
            (40, "2027-06-01", "2026-08-15"),   # normal
            (30, "2026-10-02", "2026-05-08"),   # déjà périmé (~3 jours)
            (25, "2026-11-02", "2026-09-07"),   # périme bientôt (~28 jours)
        ],
        "Ventoline": [
            (12, "2027-07-01", "2026-09-15"),   # stock bas (sous le seuil de 15)
            (35, "2028-02-01", "2026-09-30"),   # normal
        ],
        "Insuline Lantus": [
            (5,  "2026-10-20", "2026-10-02"),   # stock bas ET périme bientôt (~15 jours)
            (50, "2027-10-01", "2026-08-26"),   # normal
        ],
    }
 
    for nom_produit, lots in lots_par_produit.items():
        pid = id_produit[nom_produit]
        for quantite, date_peremption, date_entree in lots:
 
            # Table ENTREES : journal historique de la réception
            curs.execute(
                """INSERT INTO ENTREES
                   (IDPRODUITS, NOMPRODUIT, QUANTITE, DATEENTREE, DATEPEREMPTION)
                   VALUES (?, ?, ?, ?, ?)""",
                (pid, nom_produit, quantite, date_entree, date_peremption),
            )
 
            # Table LOTS : état courant du stock (sera décrémenté par les sorties)
            curs.execute(
                """INSERT INTO LOTS
                   (IDPRODUIT, NOMPRODUIT, DATEPEREMPTION, QUANTITE)
                   VALUES (?, ?, ?, ?)""",
                (pid, nom_produit, date_peremption, quantite),
            )
            idlots = curs.lastrowid
            reference = f"LOT-{idlots:04d}"
            curs.execute("UPDATE LOTS SET REFERENCELOT = ? WHERE IDLots = ?", (reference, idlots))
            conn.commit()
 
    # --- 4. Quelques sorties déjà enregistrées (pour démontrer l'historique) ---
    # (nom_produit, quantite_sortie, date_de_la_sortie)
    sorties_demo = [
        ("Paracétamol",  40, "2026-09-25"),
        ("Amoxicilline", 30, "2026-09-30"),
        ("Doliprane",    60, "2026-10-02"),
    ]
 
    for i, (nom_produit, quantite_sortie, date_sortie) in enumerate(sorties_demo, start=1):
        pid = id_produit[nom_produit]
 
        # Trouve un lot valide (non périmé, quantité suffisante) pour ce produit,
        # le plus urgent en premier (logique FEFO)
        curs.execute(
            """SELECT IDLots, QUANTITE FROM LOTS
               WHERE IDPRODUIT = ? AND QUANTITE >= ? AND DATEPEREMPTION >= ?
               ORDER BY DATEPEREMPTION ASC LIMIT 1""",
            (pid, quantite_sortie, date_sortie),
        )
        lot = curs.fetchone()
        if lot is None:
            continue  # sécurité, ne devrait pas arriver avec ce jeu de données
 
        idlots, quantite_lot = lot
 
        # Décrémente le lot
        curs.execute(
            "UPDATE LOTS SET QUANTITE = QUANTITE - ? WHERE IDLots = ?",
            (quantite_sortie, idlots),
        )
 
        # Enregistre la sortie dans l'historique
        reference = f"SOR-{i:04d}"
        curs.execute(
            """INSERT INTO SORTIES
               (REFERENCE, IDPRODUIT, NOMPRODUIT, QUANTITESortie, Date)
               VALUES (?, ?, ?, ?, ?)""",
            (reference, pid, nom_produit, quantite_sortie, date_sortie),
        )
 
    conn.commit()
 
    # --- 5. Met à jour le STOCK total de chaque produit (somme de ses lots) ---
    curs.execute("SELECT id FROM produits")
    for (pid,) in curs.fetchall():
        curs.execute(
            "SELECT COALESCE(SUM(QUANTITE), 0) FROM LOTS WHERE IDPRODUIT = ?", (pid,)
        )
        total = curs.fetchone()[0]
        curs.execute("UPDATE produits SET STOCK = ? WHERE id = ?", (total, pid))
 
    conn.commit()
    conn.close()
 
 
if __name__ == "__main__":
    peupler_donnees_demo()
    print("Base de données peuplée avec succès : 8 produits, 23 lots, 3 sorties de démo.")
    print("Relance ce script à tout moment pour réinitialiser les données de démo.")
 