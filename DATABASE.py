import sqlite3
import os
from datetime import datetime

#----fonction pour se connecter à la base de données

def connecter_bd():
    chemin_bd = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DATABASE.db")
    conn = sqlite3.connect(chemin_bd)
    curs = conn.cursor()
    return conn, curs

#---- FONCTION POUR CREER LES TABLES AU DEMARRAGE DE L'APPLICAITON ----

def creer_tables():
    conn, curs = connecter_bd()

    curs.execute("""
        CREATE TABLE IF NOT EXISTS "produits" (
            "id" INTEGER NOT NULL UNIQUE,
            "nomProduit" TEXT NOT NULL UNIQUE,
            "dosage" INTEGER,
            "SEUIL" INTEGER,
            "STOCK" INTEGER NOT NULL,
            PRIMARY KEY("id" AUTOINCREMENT)
        )
    """)

    curs.execute("""
        CREATE TABLE IF NOT EXISTS "SORTIES" (
            "id" INTEGER NOT NULL UNIQUE,
            "REFERENCE" INTEGER UNIQUE,
            "IDPRODUIT" INTEGER NOT NULL,
            "NOMPRODUIT" TEXT NOT NULL,
            "QUANTITESortie" INTEGER NOT NULL,
            "Date" TEXT NOT NULL,
            PRIMARY KEY("id" AUTOINCREMENT)
        )
    """)

    curs.execute("""
        CREATE TABLE IF NOT EXISTS "LOTS" (
            "IDLots" INTEGER NOT NULL UNIQUE,
            "IDPRODUIT" INTEGER NOT NULL,
            "NOMPRODUIT" TEXT NOT NULL,
            "DATEPEREMPTION" TEXT NOT NULL,
            "QUANTITE" INTEGER NOT NULL,
            "REFERENCELOT" TEXT,
            PRIMARY KEY("IDLots" AUTOINCREMENT)
        )
    """)

    curs.execute("""
        CREATE TABLE IF NOT EXISTS "ENTREES" (
            "IDLots" INTEGER NOT NULL UNIQUE,
            "IDPRODUITS" INTEGER NOT NULL,
            "NOMPRODUIT" TEXT,
            "QUANTITE" INTEGER NOT NULL,
            "DATEENTREE" TEXT NOT NULL,
            "DATEPEREMPTION" TEXT NOT NULL,
            PRIMARY KEY("IDLots" AUTOINCREMENT)
        )
    """)

    conn.commit()
    conn.close()

#---fonction pour enregistrer un nouveau lot de produits existants deja dans la base---

def enreg_entree(id_prod,qte,date,perim):
    from datetime import datetime 
    conn,curs=connecter_bd()
   
#Verifier que l'id entré est valide

    curs.execute("select id from produits where id=?",[id_prod])
    res=curs.fetchone()
    if res is None:
        raise ValueError("aucun produit correspondant à cet indentifiant")
    
         #utilisation de la fonction (try....except) pour prevoir les erreurs de saisie
    try:
        date_valider=datetime.strptime(date,"%Y-%m-%d") 
        datesql=datetime.strftime(date_valider,"%Y-%m-%d")
    except ValueError:
        raise ValueError("format de date non pris en charge") 
        
    #entrer la date de peremption au bon format pour sql
        
    try:
        perim_valide=datetime.strptime(perim,"%Y-%m-%d")
        perimsql=datetime.strftime(perim_valide,"%Y-%m-%d")
    except ValueError:
        raise ValueError("format de date non pris en charge")

    #ajout des elements dans la base
    
        #Ajouter le nom du produit automatiquement grace à l'id
    curs.execute("select nomProduit from produits where id=?",[id_prod]) 
    (nom,)=curs.fetchone()
        
        #enregistrement dans la base de données
    try:
        #pour renseigner l'historique des entrées
        
        curs.execute('insert into ENTREES(IDPRODUITS,NOMPRODUIT,QUANTITE,DATEENTREE, DATEPEREMPTION) values(?,?,?,?,?)',(id_prod,nom,qte,datesql,perimsql))
        conn.commit() #pour actualiser la valeur entrée dans la base de donnée
        
        #renseigner la table des lots disponibles
        curs.execute("insert into LOTS(IDPRODUIT,NOMPRODUIT,QUANTITE,DATEPEREMPTION) values(?,?,?,?)",(id_prod,nom,qte,perimsql))
        conn.commit
            
        #-----ACTUALISATION DU STOCK APRES NOUVELLE ENTREE------
        #ajout de la nouvelle valeur dans la table
        
        curs.execute("update produits set STOCK = STOCK + ?  where id=? ",(qte,id_prod))
        conn.commit() #valider la modfification 
        
        #anticiper une valeur manquante dans la saisie 
    except UnboundLocalError:
        raise UnboundLocalError("valeur manquante")
    conn.close()

#------fonction pour enregistrer un nouveau produit-----

def nouveau_produit(nom,qte,qte_seuil,date,perim):
    from datetime import datetime
    conn,curs=connecter_bd()
    #utilisation de la fonction (try....except) pour prevoir les erreurs de saisie
    
        #PREVOIR LES ERREURS DE SAISIE
    try:
        date_valider=datetime.strptime(date,"%Y-%m-%d") 
        datesql=datetime.strftime(date_valider,"%Y-%m-%d")
    except ValueError:
        raise ValueError("format  de date non pris en charge") 
        
    #entrer la date de peremption au bon format pour sql
        
    try:
        perim_valide=datetime.strptime(perim,"%Y-%m-%d")
        perimsql=datetime.strftime(perim_valide,"%Y-%m-%d")
    except ValueError:
        raise ValueError("format de date non pris en charge")

    #ajout des elements dans la base
    
        #enregistrement dans la base de données
    try:
        #pour renseigner l'historique des entrées
        curs.execute("insert into produits(NomProduit,STOCK,SEUIL) values(?,?,?)",(nom,qte,qte_seuil))
        conn.commit()
        curs.execute("select id from produits where NomProduit=?",(nom,))
        (id_prod,)=curs.fetchone()
        curs.execute('insert into ENTREES(IDPRODUITS,NOMPRODUIT,QUANTITE,DATEENTREE, DATEPEREMPTION) values(?,?,?,?,?)',(id_prod,nom,qte,datesql,perimsql))
        conn.commit() #pour actualiser la valeur entrée dans la base de donnée
        
        #renseigner la table des stocks disponibles
        curs.execute("insert into LOTS(IDPRODUIT,NOMPRODUIT,QUANTITE,DATEPEREMPTION) values(?,?,?,?)",(id_prod,nom,qte,perimsql))
        conn.commit
            
        #ACTUALISATION DU STOCK APRES NOUVELLE ENTREE------
        
        #ajout de la nouvelle valeur dans la table produits
        
        curs.execute("update produits set STOCK = STOCK + ?  where id=? ",(qte,id_prod))
        conn.commit() #valider la modfification 
        
        #anticiper une valeur manquante dans la saisie 
    except UnboundLocalError:
        raise UnboundLocalError("valeur manquante")
    conn.close()

#---fonction pour afficher les produits----

def afficher_table_produits():
    conn,curs=connecter_bd()
    produits=[]
    curs.execute("select id,nomproduit,stock,seuil from produits")
    res=curs.fetchall()
    for i,j,k,l in res:
        produits.append({"identifiant":i,"nom":j,"quantite":k,"seuil":l})
    conn.close()
    return produits


#-----FONCTION POUR ENREGISTRER LES SORTIES-----

def enreg_sortie(id_prod,qte):
    from datetime import date
    conn,curs=connecter_bd()
    #enregistrement de la commande

    #test sur le stock disponible 
    curs.execute("select IDLots,QUANTITE from LOTS where IDPRODUIT=? AND QUANTITE > 0 AND DATEPEREMPTION >= ? ORDER BY DATEPEREMPTION ASC",(id_prod,date.today().isoformat()))
    stock_dispo=curs.fetchall()
    if stock_dispo is None :
        return "ce produit est indisponible"
    total=0
    for i in stock_dispo:
        total=total + i[1]
        
        #STOCK INSUFFISANT 
    if qte>total:
        raise ValueError(f"stock restant insuffisant, restant:{total}")
        
    #UTILISATION DES STOCKS PRESQUE PERIME EN PREMIER
    reste=qte
    for j in stock_dispo:
        if reste==0:
            break
            
        if reste >= j[1]:
            curs.execute("update LOTS set QUANTITE = ? where IDLots=?",(0,j[0]))
            conn.commit()
            reste=reste-j[1]
        else:
                curs.execute("update LOTS set QUANTITE = QUANTITE - ? where IDLots=?",(reste,j[0]))
                conn.commit()
                reste=0
            
    #recupérer le nom du produit
    curs.execute("select nomProduit from produits where id=?",[id_prod]) 
    (nom,)=curs.fetchone()
    curs.execute("update produits set STOCK = STOCK - ? where id=?",(qte,id_prod))
    conn.commit()
    
    curs.execute("insert into SORTIES(IDPRODUIT,NOMPRODUIT,QUANTITESortie,DATE) values(?,?,?,?)",(id_prod,nom,qte,date.today()))
    conn.commit()
    
    new_id=curs.lastrowid
    reference=f"SOR-{new_id:04d}"
    
    curs.execute("update SORTIES set REFERENCE=? where id=?",(reference,new_id))
    conn.commit()
    #
    conn.close()

#-----FONCTION POUR AFFICHER LES SORTIES-----

def afficher_sorties():
    conn,curs=connecter_bd()
    sortie=[]
    curs.execute("select REFERENCE, IDPRODUIT, NOMPRODUIT,QUANTITESortie, Date from SORTIES")
    res=curs.fetchall()
    for i,j,k,l,m in res:
        sortie.append({"reference":i,"id_produit":j,"nom":k,"quantite sortie":l,"Date":m})
    conn.close()
    return sortie

#----HISTORIQUE DES SORTIES PAR PRODUITS----

def sorties_produit(id_prod):
    conn,curs=connecter_bd()
    sortie=[]
    curs.execute("select REFERENCE, IDPRODUIT, NOMPRODUIT,QUANTITESortie, Date from SORTIES WHERE IDPRODUIT=?",[id_prod])
    res=curs.fetchall()
    for i,j,k,l,m in res:
        sortie.append({"reference":i,"id_produit":j,"nom":k,"quantite sortie":l,"Date":m})
    conn.close()
    return sortie
    

#-----FONCTION POUR LES ALERTE DE STOCK BAS-----

def alerte_stock():
    conn,curs=connecter_bd()
    curs.execute("select nomProduit, STOCK from produits where STOCK < SEUIL")
    res=curs.fetchall()
    
    alerte=[]
    for i,j in res:
        alerte.append({"Nom du produit":i,"Stock actuel":j})
    conn.close()
    return alerte

#-----FONCTION POUR LES HISTORIQUES D'ENTREES----

def afficher_entrees():
    conn,curs=connecter_bd()
    curs.execute("select [idLots],idproduits,nomproduit,quantite,dateentree,dateperemption from ENTREES")
    entree=[]
    res=curs.fetchall()
    for i,j,k,l,m,n in res:
        entree.append({"Reference_entrée":f"ENT-{i:04d}","identifiant produit":j,"nom":k,"quantite":l,"date d'enregistrement":m,"date de peremption":n})
    conn.close()
    return entree

#-----FONCTION POUR AFFICHER LES LOTS DISPONIBLES-----

def afficher_LOTS():
    conn,curs=connecter_bd()
    curs.execute("select IDLOTS, nomproduit, quantite, dateperemption from LOTS")
    lots=[]
    res=curs.fetchall()
    for i,j,k,l in res:
        lots.append({"Reference_lot":f"LOT-{i:04d}","nom":j,"quantité":k,"date de peremeption":l})
    conn.close()
    return lots

#----FONCTION POUR ALERTE DATE DE PEREMPTION PROCHE----

def alerte_peremption(seuil_jours=30):
    from datetime import date
    conn,curs=connecter_bd()
    curs.execute("select IDLots,NOMPRODUIT,QUANTITE,DATEPEREMPTION from LOTS")
    lots=curs.fetchall()
    today=date.today()
    resultats=[]
    for i,j,k,l in lots:
        perim=date.fromisoformat(l)
        jours_restants=(perim-today).days

        if 0 <= jours_restants <= seuil_jours:
            resultats.append({
                "reference LOTS":f"LOT-{i:04d}",
                "produit": j,
                "date de peremption": l,
                "quantite": k,
                "jours restants": jours_restants
            })
    conn.close()
    return resultats

#----FONCTION ALERTE PRODUITS PERIMES----

def alerte_perime():
    from datetime import date
    conn,curs=connecter_bd()
    curs.execute("select IDLots,NOMPRODUIT,QUANTITE,DATEPEREMPTION from LOTS")
    lots=curs.fetchall()
    today=date.today()
    resultats=[]
    for i,j,k,l in lots:
        perim=date.fromisoformat(l)
        jours=(perim-today).days
        if 0 > jours:
            resultats.append({
                "reference LOTS": f"LOT-{i:04d}",
                "produit": j,
                "date de peremption": l,
                "quantite": k,
                "périmé depuis": f"{jours}"
            })
    conn.close()
    return resultats

#-----FONCTION POUR TRACER UN LOT----

def tracer_lot(ref_Lot):
    conn, curs = connecter_bd()
    curs.execute("select referencelot,idlots,nomproduit,quantite,dateperemption from lots where referencelot=?",[ref_Lot])
    lots=curs.fetchall()
    if lots == [] :
        return []
    resultat=[]
    for r in lots:
        lot_id=r[1]
    curs.execute("select dateentree from entrees where idlots=?",[lot_id])
    for j in curs.fetchone():
        date=j
    for i,j,k,l,m in lots:
        resultat.append({"reference Lot":i,"id Lot":j,"nom":k,"quantite":l,"DATE ENTREE":date,"DATE DE PEREMPTION":m})

    return resultat
