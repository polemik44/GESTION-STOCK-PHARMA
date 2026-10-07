"""
app.py
Interface Streamlit pour le logiciel de gestion de stock pharmaceutique.
 
ATTENTION : les clés de dictionnaire utilisées ci-dessous (ex. "id", "nomProduit")
sont des hypothèses basées sur tes captures précédentes. Vérifie-les contre ce que
tes fonctions renvoient réellement (fais un print() rapide dans Jupyter si besoin)
et corrige les lignes marquées "# <-- vérifie cette clé" si nécessaire.
"""
 
import streamlit as st
from DATABASE import (
    connecter_bd,
    enreg_entree,
    nouveau_produit,
    afficher_table_produits,
    enreg_sortie,
    afficher_sorties,
    sorties_produit,
    afficher_entrees,
    afficher_LOTS,
    alerte_peremption,
    alerte_perime,
    alerte_stock,
    tracer_lot,
    creer_tables
)
from seed import peupler_donnees_demo
 
st.set_page_config(page_title="Gestion de stock pharmaceutique", layout="wide")
 
# --- Initialisation automatique de la base si elle est vide ---
# Utile pour le déploiement en ligne (filesystem éphémère) : au premier lancement,
# si aucun produit n'existe, on peuple automatiquement avec les données de démo.
creer_tables()
produits_existants = afficher_table_produits()
if not produits_existants:
    peupler_donnees_demo()
 
# --- Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Aller à",
    ["Tableau de bord", "Nouveau produit", "Réception de lot", "Sortie de stock",
     "Traçabilité", "Historique", "Réinitialisation"],
)
 
st.title("GESTION DE STOCK PHARMACEUTIQUE ")
 
 
# ============================================================
# PAGE : TABLEAU DE BORD
# ============================================================
if page == "Tableau de bord":
    
    
    st.header("Vue d'ensemble du stock")
 
    produits = afficher_table_produits()
    st.dataframe(produits)
 
    st.header("⚠️ Alertes")
 
    col1, col2, col3 = st.columns(3)
 
    with col1:
        st.subheader("Stock bas")
        stock_bas = alerte_stock()
        st.metric("", len(stock_bas))
        if stock_bas:
            st.dataframe(stock_bas)
        else:
            st.success("Aucun produit sous le seuil.")
 
    with col2:
        st.subheader("Péremption proche (30 jours)")
        peremption_proche = alerte_peremption(seuil_jours=30)
        if peremption_proche:
            st.dataframe(peremption_proche)
        else:
            st.success("Aucun lot ne périme bientôt.")
 
    with col3:
        st.subheader("Lots périmés")
        perimes = alerte_perime()
        if perimes:
            st.dataframe(perimes)
            
        else:
            st.success("Aucun lot périmé.")
 
 
# ============================================================
# PAGE : NOUVEAU PRODUIT
# ============================================================
elif page == "Nouveau produit":
    st.header("Enregistrer un nouveau produit (avec son premier lot)")
 
    with st.form("form_nouveau_produit"):
        nom = st.text_input("Nom du produit")
        dosage = st.number_input("Dosage (mg)", min_value=0, step=5)
        qte_seuil = st.number_input("Seuil d'alerte", min_value=0, step=5)
        qte = st.number_input("Quantité du premier lot", min_value=0, step=10)
        date_entree = st.date_input("Date d'entrée")
        date_peremption = st.date_input("Date de péremption")
 
        submit = st.form_submit_button("Créer le produit")
 
    if submit:
        if nom.strip() == "":
            st.error("Le nom du produit ne peut pas être vide.")
        else:
            try:
                nouveau_produit(
                    nom, qte, qte_seuil, str(date_entree), str(date_peremption)
                    # <-- ajoute dosage ici dans l'ordre exact de ta fonction
                    # une fois le paramètre dosage ajouté à nouveau_produit()
                )
                st.success(f"Produit '{nom}' créé avec succès.")
            except ValueError as e:
                st.error(str(e))
 
 
# ============================================================
# PAGE : RÉCEPTION DE LOT (produit existant)
# ============================================================
elif page == "Réception de lot":
    st.header("Réceptionner un lot pour un produit existant")
 
    produits = afficher_table_produits()
    noms_produits = [p["nom"] for p in produits]  # <-- vérifie cette clé
 
    with st.form("form_reception"):
        choix_nom = st.selectbox("Produit", noms_produits)
        quantite = st.number_input("Quantité reçue", min_value=0, step=1)
        date_entree = st.date_input("Date d'entrée")
        date_peremption = st.date_input("Date de péremption")
 
        submit = st.form_submit_button("Enregistrer la réception")
 
    if submit:
        try:
            produit_id = next(
                p["identifiant"] for p in produits if p["nom"] == choix_nom
            )  # <-- vérifie ces clés
            enreg_entree(produit_id, quantite, str(date_entree), str(date_peremption))
            st.success(f"Lot reçu pour {choix_nom}.")
        except ValueError as e:
            st.error(str(e))
 

# ============================================================
# PAGE : SORTIE DE STOCK
# ============================================================
elif page == "Sortie de stock":
    st.header("Enregistrer une sortie de stock (FEFO automatique)")
 
    produits = afficher_table_produits()
    noms_produits = [p["nom"] for p in produits]  # <-- vérifie cette clé
 
    with st.form("form_sortie"):
        choix_nom = st.selectbox("Produit", noms_produits)
        quantite = st.number_input("Quantité à sortir", min_value=1, step=1)
 
        submit = st.form_submit_button("Valider la sortie")
 
    if submit:
        try:
            produit_id = next(
                p["identifiant"] for p in produits if p["nom"] == choix_nom
            )  # <-- vérifie ces clés
            enreg_sortie(produit_id, quantite)
            st.success(f"Sortie de {quantite} unités enregistrée pour {choix_nom}.")
        except ValueError as e:
            st.error(str(e))
 
    st.subheader("Historique des sorties")
    produits_pour_filtre = afficher_table_produits()
    noms = [p["nom"] for p in produits_pour_filtre]  # <-- vérifie cette clé
    filtre_nom = st.selectbox("Filtrer par produit", ["Tous"] + noms, key="filtre_sorties")
 
    if filtre_nom == "Tous":
        st.dataframe(afficher_sorties())
    else:
        produit_id_filtre = next(
            p["identifiant"] for p in produits_pour_filtre if p["nom"] == filtre_nom
        )  # <-- vérifie ces clés
        resultat = sorties_produit(produit_id_filtre)
        if resultat:
            st.dataframe(resultat)
        else:
            st.info(f"Aucune sortie enregistrée pour {filtre_nom}.")
 
 
# ============================================================
# PAGE : TRAÇABILITÉ
# ============================================================
elif page == "Traçabilité":
    st.header("Rechercher l'historique d'un lot")
 
    ref_lot = st.text_input("Référence du lot (ex. LOT-0012)")
 
    if st.button("Rechercher"):
        if ref_lot.strip() == "":
            st.warning("Entre une référence de lot.")
        else:
            resultat = tracer_lot(ref_lot)
            if resultat:
                st.dataframe(resultat)
            else:
                st.info(f"Aucun lot trouvé pour la référence '{ref_lot}'.")
 
 
# ============================================================
# PAGE : HISTORIQUE
# ============================================================
elif page == "Historique":
    st.header("Historique complet")
 
    tab1, tab2, tab3 = st.tabs(["ENTREES", "LOTS","SORTIES"])
 
    with tab1:
        st.dataframe(afficher_entrees())
 
    with tab2:
        st.dataframe(afficher_LOTS())

    with tab3:
        st.dataframe(afficher_sorties())
 
 
# ============================================================
# PAGE : RÉINITIALISATION
# ============================================================
elif page == "Réinitialisation":
    st.header("Réinitialiser les données de démonstration")
    st.warning(
        "Cette action efface toutes les données actuelles (produits, lots, "
        "entrées, sorties) et les remplace par le jeu de données de démo d'origine."
    )
 
    confirmation = st.checkbox("Je comprends que cette action est irréversible")
 
    if st.button("Réinitialiser", disabled=not confirmation):
        peupler_donnees_demo()
        st.success("Les données ont été réinitialisées avec succès.")
        st.rerun()