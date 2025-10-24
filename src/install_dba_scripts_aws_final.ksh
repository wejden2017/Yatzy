#!/bin/ksh
#
#---------------------------------------------------------------------------
# Application Refonte LUCA - BATCH
#---------------------------------------------------------------------------
#
# SOPRA
#
# Function : Installe la partie dba d'une livraison
#
# Gestion Configuration CVS :
#
# Nom du shell............: $RCSfile install_dba_scripts_aws.ksh,v $
# Date de modification....: $Date: 2024/10/24 $
# Auteur.................: $Author: DevOps Team $
# Revision...............: $Revision: 2.0 $
# Classement.............: $Source: AWS Version $
#
# Parametres d'entree : $1 => SERVICE_NAME
#                       $2 => USER
#                       $3 => IP_SERVER
#                       $4 => PACKAGE
#
# Variable d'environnement requise :
#                       LUCA_PASSWORD => Mot de passe Oracle (depuis vault)
#
# Codes Retour :
#               0 => OK
#               1 => Sortie en erreur le dossier des scripts existe deja
#               2 => Sortie en erreur lors de la decompression de cats-script
#               3 => Sortie en erreur le dossier cats-scripts n'a pas ete trouve dans le tar
#               4 => Sortie en erreur un script n'a pas de script de rollback
#               5 => Sortie en erreur l'insertion d'une ligne dans SCRIPT_HISTORY a echoue
#               6 => Sortie en erreur l'execution du script a echoue
#               7 => Sortie en erreur la mise a jour d'une ligne dans SCRIPT_HISTORY a echoue
#               8 => Sortie en erreur la construction des packages a echoue
#               9 => Sortie en erreur le nombre de parametres est incorrect
#              10 => Sortie en erreur la variable d'environnement LUCA_PASSWORD n'est pas definie
#              11 => Sortie en erreur connexion Oracle impossible
#
#---------------------------------------------------------------------------
# WDA 28/10/2013 Creation du script shell
# JFE 12/11/2013 Ajout parametres pour lancer le shell et redirection des messages dans les logs
# CCM 19/12/2013 Appel de sqlplus avec ORACLE_SID a chaque fois
# JFE 30/12/2013 Gestion du rollback directement avec sqlplus
# 2024 Version AWS - Support service name, IP et variable d'environnement LUCA_PASSWORD

# Sécurisation - Effacer l'historique des commandes pour cette session
unset HISTFILE

# Configuration du fichier de log
rep_depart=$(pwd)
LOG_FILE=$rep_depart/install_dba_scripts_aws.log

# Création et sécurisation du fichier de log
touch $LOG_FILE
chmod 600 $LOG_FILE

# Redirection des sorties vers le log
exec 1>> $LOG_FILE
exec 2>> $LOG_FILE

echo `date +%y/%m/%d` `date +%H:%M:%S` "=== DEBUT SCRIPT AWS $0 ===" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "Parametres: SERVICE_NAME=$1 USER=$2 IP_SERVER=$3 PACKAGE=$4" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "Mot de passe: [LUCA_PASSWORD_FROM_ENVIRONMENT]" >> $LOG_FILE

# Verification du nombre de parametres
if [[ $# != 4 ]]
then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR: Nombre de parametres incorrect" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Usage: install_dba_scripts_aws.ksh <SERVICE_NAME> <USER> <IP_SERVER> <PACKAGE>" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Variable d'environnement requise: LUCA_PASSWORD" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Exemple: export LUCA_PASSWORD=\$(vault kv get -field=password secret/luca/oracle)" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 9" >> $LOG_FILE
    exit 9
fi

# Verification de la variable d'environnement LUCA_PASSWORD
if [[ -z "$LUCA_PASSWORD" ]]
then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR CRITIQUE: La variable d'environnement LUCA_PASSWORD n'est pas definie" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Veuillez definir LUCA_PASSWORD avant d'executer ce script" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Commande suggere: export LUCA_PASSWORD=\"votre_mot_de_passe\"" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 10" >> $LOG_FILE
    exit 10
fi

# Parametrage BDD
SERVICE_NAME=$1
USER=$2
IP_SERVER=$3
PACKAGE=$4
PASS=$LUCA_PASSWORD

# Validation des parametres
if [[ -z "$SERVICE_NAME" || -z "$USER" || -z "$IP_SERVER" || -z "$PACKAGE" ]]; then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR: Un ou plusieurs parametres sont vides" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 9" >> $LOG_FILE
    exit 9
fi

# Validation du package (ne peut pas être vide ou NULL)
if [[ "$PACKAGE" == "NULL" ]]; then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR: Le parametre PACKAGE ne peut pas etre NULL" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 9" >> $LOG_FILE
    exit 9
fi

# Construction de la chaine de connexion avec service name
# Format: user/password@//host:port/service_name
ORACLE_CONNECT_STRING="$USER/$PASS@//$IP_SERVER:1521/$SERVICE_NAME"

echo `date +%y/%m/%d` `date +%H:%M:%S` "Configuration Oracle: $USER@//$IP_SERVER:1521/$SERVICE_NAME" >> $LOG_FILE

# Test de connectivité Oracle OBLIGATOIRE
echo `date +%y/%m/%d` `date +%H:%M:%S` "Test de connectivite Oracle en cours..." >> $LOG_FILE
sqlplus -S $ORACLE_CONNECT_STRING <<! > /dev/null 2>&1
SELECT 'Connection OK' FROM DUAL;
exit;
!

if [[ $? -ne 0 ]]
then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR CRITIQUE: Impossible de se connecter a Oracle" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Verifications a effectuer:" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "  - SERVICE_NAME: $SERVICE_NAME" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "  - USER: $USER" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "  - IP_SERVER: $IP_SERVER" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Port: 1521 (par defaut)" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Variable LUCA_PASSWORD definie" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 11" >> $LOG_FILE
    exit 11
fi

echo `date +%y/%m/%d` `date +%H:%M:%S` "SUCCESS: Connectivite Oracle validee" >> $LOG_FILE

# Parametrage cats-script
rep_script=cats-script

# Parametrage cats-plsql
tar_plsql=cats-plsql.tar
buildAll=buildAll.sql

# Verification de la presence des fichiers requis
if [[ ! -f "$rep_script.tar" ]]; then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR: Fichier $rep_script.tar non trouve" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 2" >> $LOG_FILE
    exit 2
fi

if [[ ! -f "$tar_plsql" ]]; then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR: Fichier $tar_plsql non trouve" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 2" >> $LOG_FILE
    exit 2
fi

#=============================================================================
#                            PHASE CATS-SCRIPT
#=============================================================================

echo `date +%y/%m/%d` `date +%H:%M:%S` "========================================" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "DEBUT PHASE CATS-SCRIPT" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "========================================" >> $LOG_FILE

# Verification de la non existance du dossier a extraire
if [[ -d $rep_script ]]
then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ATTENTION: Le dossier $rep_script existe deja" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Suppression automatique du dossier existant..." >> $LOG_FILE
    rm -rf $rep_script
    if [[ $? -ne 0 ]]; then
        echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR: Impossible de supprimer le dossier existant $rep_script" >> $LOG_FILE
        echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 1" >> $LOG_FILE
        exit 1
    fi
fi

# Decompression de l'archive contenant les scripts
echo `date +%y/%m/%d` `date +%H:%M:%S` "Decompression de $rep_script.tar..." >> $LOG_FILE
tar xvf $rep_script.tar >> $LOG_FILE 2>&1
if [[ $? -ne 0 ]]
then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR: Echec de la decompression de $rep_script.tar" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 2" >> $LOG_FILE
    exit 2
fi

cd $rep_script
if [[ $? -ne 0 ]]
then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR: Le dossier $rep_script n'existe pas apres decompression" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Verifiez le contenu de l'archive $rep_script.tar" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 3" >> $LOG_FILE
    exit 3
fi

# Recuperation de la liste des scripts triee par ordre alphabetique
liste_scripts=$(ls -1 *.sql 2>/dev/null | sort)
if [[ -z "$liste_scripts" ]]; then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ATTENTION: Aucun fichier .sql trouve dans $rep_script" >> $LOG_FILE
    cd $rep_depart
    rm -rf $rep_script
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Phase CATS-SCRIPT terminee - aucun script a traiter" >> $LOG_FILE
else
    nb_scripts=$(echo "$liste_scripts" | wc -l)
    script_count=0
    script_success=0
    script_skipped=0

    echo `date +%y/%m/%d` `date +%H:%M:%S` "Nombre de scripts SQL detectes: $nb_scripts" >> $LOG_FILE

    # Pour chaque script extrait
    for script in $liste_scripts
    do
        script_count=$((script_count + 1))
        echo `date +%y/%m/%d` `date +%H:%M:%S` "----------------------------------------" >> $LOG_FILE
        echo `date +%y/%m/%d` `date +%H:%M:%S` "Traitement script $script_count/$nb_scripts : $script" >> $LOG_FILE

        # Verification de l'existence du fichier
        if [[ ! -f "$script" ]]; then
            echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR: Fichier $script non trouve" >> $LOG_FILE
            continue
        fi

        # Convention de nommage des fichiers rollback
        script_rollback=${script%'.sql'}_ROLLBACK.sql

        if [[ ! -f "rollback/$script_rollback" ]]
        then
            echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR CRITIQUE: Script de rollback manquant" >> $LOG_FILE
            echo `date +%y/%m/%d` `date +%H:%M:%S` "Script: $script" >> $LOG_FILE
            echo `date +%y/%m/%d` `date +%H:%M:%S` "Rollback attendu: rollback/$script_rollback" >> $LOG_FILE
            echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 4" >> $LOG_FILE
            exit 4
        fi

        echo `date +%y/%m/%d` `date +%H:%M:%S` "Rollback disponible: rollback/$script_rollback" >> $LOG_FILE

        # Recuperation de la version de la livraison
        version=$(echo $script | cut -d'_' -f1)
        if [[ $? -ne 0 || -z "$version" ]]
        then
            version='0'
        fi

        # Recuperation de l'id du fichier
        id=$(echo $script | cut -d'_' -f2)
        if [[ $? -ne 0 || -z "$id" ]]
        then
            id='1'
        fi

        echo `date +%y/%m/%d` `date +%H:%M:%S` "Analyse: VERSION=$version, ID=$id" >> $LOG_FILE

        # Recherche d'un enregistrement du script sur la base
        echo `date +%y/%m/%d` `date +%H:%M:%S` "Verification de l'etat du script en base..." >> $LOG_FILE
        statut=$(sqlplus -S $ORACLE_CONNECT_STRING <<! 2>/dev/null
            set PAGESIZE 0
            set FEEDBACK OFF
            set HEADING OFF
            set ECHO OFF
            SELECT NVL(STATUT, -1) FROM SCRIPT_HISTORY WHERE NOM_SCRIPT='$script';
            exit;
!
)

        # Nettoyage du résultat (suppression des espaces)
        statut=$(echo $statut | tr -d ' \n\r')

        if [[ -z "$statut" || "$statut" == "-1" ]]
        then
            statut=0
            echo `date +%y/%m/%d` `date +%H:%M:%S` "Script non reference en base - insertion en cours..." >> $LOG_FILE
            
            # Insertion d'une ligne dans SCRIPT_HISTORY
            sqlplus -S $ORACLE_CONNECT_STRING <<!
                WHENEVER SQLERROR EXIT FAILURE ROLLBACK;
                set ECHO OFF
                set FEEDBACK OFF
                INSERT INTO SCRIPT_HISTORY (VERSION,ID,NOM_SCRIPT,STATUT,DATE_LIVRAISON, CATS_PACKAGE) 
                VALUES ('$version','$id','$script',$statut,SYSDATE, '$PACKAGE');
                COMMIT;
                exit;
!

            if [[ $? -ne 0 ]]
            then
                echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR: Echec de l'insertion dans SCRIPT_HISTORY" >> $LOG_FILE
                echo `date +%y/%m/%d` `date +%H:%M:%S` "Script: $script, Package: $PACKAGE" >> $LOG_FILE
                echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 5" >> $LOG_FILE
                exit 5
            fi
            echo `date +%y/%m/%d` `date +%H:%M:%S` "SUCCESS: Script enregistre en base avec STATUT=0" >> $LOG_FILE
        fi

        if [[ $statut -eq 1 ]]
        then
            echo `date +%y/%m/%d` `date +%H:%M:%S` "INFO: Script $script deja execute (STATUT=1) - passage au suivant" >> $LOG_FILE
            script_skipped=$((script_skipped + 1))
        elif [[ $statut -eq 0 ]]
        then
            # Execution du script
            echo `date +%y/%m/%d` `date +%H:%M:%S` "EXECUTION du script $script en cours..." >> $LOG_FILE
            
            sqlplus -S $ORACLE_CONNECT_STRING <<!
                WHENEVER SQLERROR EXIT FAILURE ROLLBACK;
                set ECHO ON
                set SQLBLANKLINES ON
                set PAGESIZE 50000
                SPOOL $script.execution.log
                @$script;
                SPOOL OFF
                exit;
!

            if [[ $? -ne 0 ]]
            then
                echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR CRITIQUE: Echec de l'execution du script $script" >> $LOG_FILE
                echo `date +%y/%m/%d` `date +%H:%M:%S` "Consultez le fichier $script.execution.log pour plus de details" >> $LOG_FILE
                echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 6" >> $LOG_FILE
                exit 6
            fi

            # Mise a jour du statut à succès
            echo `date +%y/%m/%d` `date +%H:%M:%S` "Mise a jour du statut en base..." >> $LOG_FILE
            sqlplus -S $ORACLE_CONNECT_STRING <<!
                WHENEVER SQLERROR EXIT FAILURE ROLLBACK;
                set ECHO OFF
                set FEEDBACK OFF
                UPDATE SCRIPT_HISTORY 
                SET STATUT=1, DATE_LIVRAISON=SYSDATE 
                WHERE NOM_SCRIPT='$script';
                COMMIT;
                exit;
!

            if [[ $? -ne 0 ]]
            then
                echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR: Echec de la mise a jour du statut dans SCRIPT_HISTORY" >> $LOG_FILE
                echo `date +%y/%m/%d` `date +%H:%M:%S` "Script: $script" >> $LOG_FILE
                echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 7" >> $LOG_FILE
                exit 7
            fi

            echo `date +%y/%m/%d` `date +%H:%M:%S` "SUCCESS: Script $script execute et marque comme termine (STATUT=1)" >> $LOG_FILE
            script_success=$((script_success + 1))
        else
            echo `date +%y/%m/%d` `date +%H:%M:%S` "ATTENTION: Script $script a un statut inattendu: $statut" >> $LOG_FILE
        fi
    done

    # Suppression des fichiers extraits
    cd $rep_depart
    rm -rf $rep_script

    echo `date +%y/%m/%d` `date +%H:%M:%S` "========================================" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "BILAN PHASE CATS-SCRIPT:" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Scripts traites: $script_count" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Scripts executes: $script_success" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Scripts ignores (deja executes): $script_skipped" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "========================================" >> $LOG_FILE
fi

#=============================================================================
#                            PHASE CATS-PL/SQL
#=============================================================================

echo `date +%y/%m/%d` `date +%H:%M:%S` "========================================" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "DEBUT PHASE CATS-PL/SQL" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "========================================" >> $LOG_FILE

rep_temp=temp_plsql

# Creation du dossier temporaire
mkdir $rep_temp
if [[ $? -ne 0 ]]; then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR: Impossible de creer le dossier temporaire $rep_temp" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 8" >> $LOG_FILE
    exit 8
fi

# Copie du tar vers le dossier temporaire
cp $tar_plsql $rep_temp
if [[ $? -ne 0 ]]; then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR: Impossible de copier $tar_plsql vers $rep_temp" >> $LOG_FILE
    rm -rf $rep_temp
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 8" >> $LOG_FILE
    exit 8
fi

cd $rep_temp

# Decompression de l'archive contenant les packages
echo `date +%y/%m/%d` `date +%H:%M:%S` "Decompression de $tar_plsql..." >> $LOG_FILE
tar xvf $tar_plsql >> $LOG_FILE 2>&1
if [[ $? -ne 0 ]]; then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR: Echec de la decompression de $tar_plsql" >> $LOG_FILE
    cd $rep_depart
    rm -rf $rep_temp
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 8" >> $LOG_FILE
    exit 8
fi

# Verification de la presence du buildAll
if [[ ! -f "$buildAll" ]]; then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR: Fichier $buildAll non trouve apres decompression" >> $LOG_FILE
    cd $rep_depart
    rm -rf $rep_temp
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 8" >> $LOG_FILE
    exit 8
fi

# Execution du buildAll
echo `date +%y/%m/%d` `date +%H:%M:%S` "EXECUTION de $buildAll en cours..." >> $LOG_FILE
sqlplus -S $ORACLE_CONNECT_STRING <<!
    WHENEVER SQLERROR EXIT FAILURE;
    set ECHO ON
    set PAGESIZE 50000
    SPOOL buildAll.execution.log
    @$buildAll
    SPOOL OFF
    exit;
!

if [[ $? -ne 0 ]]
then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "ERREUR CRITIQUE: Echec de l'execution de $buildAll" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Consultez le fichier buildAll.execution.log pour plus de details" >> $LOG_FILE
    cd $rep_depart
    rm -rf $rep_temp
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: 8" >> $LOG_FILE
    exit 8
fi

echo `date +%y/%m/%d` `date +%H:%M:%S` "SUCCESS: $buildAll execute avec succes" >> $LOG_FILE

# Suppression des fichiers extraits
cd $rep_depart
rm -rf $rep_temp

echo `date +%y/%m/%d` `date +%H:%M:%S` "========================================" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "PHASE CATS-PL/SQL TERMINEE AVEC SUCCES" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "========================================" >> $LOG_FILE

#=============================================================================
#                              BILAN FINAL
#=============================================================================

echo `date +%y/%m/%d` `date +%H:%M:%S` "=======================================" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "INSTALLATION TERMINEE AVEC SUCCES" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "=======================================" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "Parametres du deploiement:" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Service Name: $SERVICE_NAME" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Utilisateur: $USER" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Serveur IP: $IP_SERVER" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Package deploye: $PACKAGE" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Fichier de log: $LOG_FILE" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "=======================================" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "=== FIN SCRIPT AWS === Code retour: 0" >> $LOG_FILE

# Nettoyage final - effacer la variable mot de passe de l'environnement
unset PASS
unset LUCA_PASSWORD

exit 0
