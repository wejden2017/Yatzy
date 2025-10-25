#!/bin/ksh
#
#---------------------------------------------------------------------------
# Application Refonte LUCA - BATCH - ROLLBACK
#---------------------------------------------------------------------------
#
# SOPRA
#
# Function : Rollback la partie dba d'une livraison
#
# Gestion Configuration CVS :
#
# Nom du shell............: $RCSfile rollback_dba_scripts.ksh,v $
# Date de modification....: $Date: 2025/10/25 $
# Auteur.................: $Author: aws_migration $
# Revision...............: $Revision: 2.0 $
# Classement.............: $Source: $
#
# Parametres d'entree : $1 => SERVICE_NAME
#                       $2 => USER
#                       $3 => IP_SERVER  
#                       $4 => PACKAGE
#                       
# Variables environnement: LUCA_PASSWORD => Mot de passe Oracle
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
#               10 => Sortie en erreur variable LUCA_PASSWORD non definie
#               11 => Sortie en erreur connexion Oracle impossible
#               12 => Sortie en erreur aucun script de rollback trouve
#
#---------------------------------------------------------------------------
# WDA 28/10/2013 Creation du script shell
# JFE 12/11/2013 Ajout parametres pour lancer le shell et redirection des messages dans les logs
# CCM 19/12/2013 Appel de sqlplus avec ORACLE_SID a chaque fois
# JFE 30/12/2013 Gestion du rollback directement avec sqlplus
# AWS 25/10/2025 Migration vers service name avec IP et sécurisation mot de passe

# Fichier de log
rep_depart=$(pwd)
fic_shell_sans_ext=$(basename $0 ".ksh")
LOG_FILE=$rep_depart/${fic_shell_sans_ext}.log
exec 1>> $LOG_FILE
exec 2>> $LOG_FILE

echo `date +%y/%m/%d` `date +%H:%M:%S` "===== DEBUT ROLLBACK DBA SCRIPTS =====" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "Debut Shell $0 $1 $2 <password_masked> $3 $4" >> $LOG_FILE

# Verification du nombre de parametres
if [[ $# != 4 ]]
then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Usage: rollback_dba_scripts.ksh <SERVICE_NAME> <USER> <IP_SERVER> <PACKAGE>" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Utilisation de la variable d'environnement LUCA_PASSWORD pour le mot de passe" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: <9>" >> $LOG_FILE
    exit 9
fi

# Verification de la variable d'environnement LUCA_PASSWORD
if [[ -z "$LUCA_PASSWORD" ]]
then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Erreur: Variable d'environnement LUCA_PASSWORD non definie" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: <10>" >> $LOG_FILE
    exit 10
fi

# Parametrage BDD
SERVICE_NAME=$1
USER=$2
IP_SERVER=$3
CATS_PKG=$4

echo `date +%y/%m/%d` `date +%H:%M:%S` "Parametres du rollback:" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Service Name: $SERVICE_NAME" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Utilisateur: $USER" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Serveur IP: $IP_SERVER" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Package rollback: $CATS_PKG" >> $LOG_FILE

# Test de connexion Oracle
echo `date +%y/%m/%d` `date +%H:%M:%S` "Test de connexion Oracle..." >> $LOG_FILE
TEST_CONN=$(sqlplus -S $USER/$LUCA_PASSWORD@$IP_SERVER/$SERVICE_NAME <<EOF
set pagesize 0
set echo off
SELECT 'CONNECTION_OK' FROM DUAL;
exit;
EOF
)

if [[ "$TEST_CONN" != "CONNECTION_OK" ]]
then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Erreur: Impossible de se connecter a Oracle" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Service: $SERVICE_NAME, User: $USER, IP: $IP_SERVER" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: <11>" >> $LOG_FILE
    exit 11
fi

echo `date +%y/%m/%d` `date +%H:%M:%S` "Connexion Oracle reussie" >> $LOG_FILE

# Parametrage cats-script rollback
rep_script=cats-script
tar_script=cats-script.tar

# Verification de l'existence du dossier a extraire
if [[ -d $rep_script ]]
then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Erreur le dossier a extraire \"$rep_script\" existe deja, veuillez le supprimer et relancer le script" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: <1>" >> $LOG_FILE
    exit 1
fi

echo `date +%y/%m/%d` `date +%H:%M:%S` "======================================" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "=== DEBUT PHASE ROLLBACK SCRIPTS ===" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "======================================" >> $LOG_FILE

# Decompression de l'archive contenant les scripts de rollback
echo `date +%y/%m/%d` `date +%H:%M:%S` "Decompression de $tar_script..." >> $LOG_FILE
tar xvf $rep_script/$tar_script >> $LOG_FILE 2>&1
if [[ $? -ne 0 ]]
then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Erreur lors de la decompression" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: <2>" >> $LOG_FILE
    exit 2
fi

cd $rep_script/rollback
if [[ $? -ne 0 ]]
then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Erreur le dossier $rep_script/rollback n'a pas ete trouve dans le tar $rep_script.tar" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: <3>" >> $LOG_FILE
    exit 3
fi

# Recuperation de la liste des scripts de rollback tries par ordre alphabetique inverse
# pour defaire dans l'ordre inverse de l'installation
liste_scripts=$(ls -1r *.sql 2>/dev/null | sort -r)

if [[ -z "$liste_scripts" ]]
then
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Aucun script de rollback trouve dans le repertoire" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: <12>" >> $LOG_FILE
    exit 12
fi

echo `date +%y/%m/%d` `date +%H:%M:%S` "Scripts de rollback trouves:" >> $LOG_FILE
for script in $liste_scripts
do
    echo `date +%y/%m/%d` `date +%H:%M:%S` "  - $script" >> $LOG_FILE
done

scripts_traites=0
scripts_executes=0
scripts_ignores=0

# Pour chaque script de rollback extrait
for script in $liste_scripts
do
    scripts_traites=$((scripts_traites + 1))
    
    # Suppression de l'extension pour chercher dans SCRIPT_HISTORY
    orig_script=$(echo $script | sed 's/_ROLLBACK//')
    
    # Recuperation de la version de la livraison
    version=$(echo $script | cut -d'_' -f1)
    if [[ $? -ne 0 ]]
    then
        version='0'
    fi
    
    # Recuperation de l'id du fichier
    id=$(echo $script | cut -d'_' -f2)
    if [[ $? -ne 0 ]]
    then
        id='1'
    fi
    
    echo `date +%y/%m/%d` `date +%H:%M:%S` "--------------------------------" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Traitement script $scripts_traites/$(echo $liste_scripts | wc -w): $script" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Script original disponible: rollback/$script" >> $LOG_FILE
    echo `date +%y/%m/%d` `date +%H:%M:%S` "Analyse: VERSION=$version, ID=$id" >> $LOG_FILE
    
    # Recherche d'un enregistrement du script original sur la base
    statut=$(sqlplus -S $USER/$LUCA_PASSWORD@$IP_SERVER/$SERVICE_NAME <<EOF
set pagesize 0
set echo off
SELECT (SELECT STATUT FROM SCRIPT_HISTORY WHERE NOM_SCRIPT='$orig_script' and CATS_PACKAGE='$CATS_PKG') FROM DUAL;
exit;
EOF
)
    
    if [[ "$statut" -eq 1 ]]
    then
        echo `date +%y/%m/%d` `date +%H:%M:%S` "Script $orig_script deja execute dans la version $CATS_PKG --> rollback necessaire" >> $LOG_FILE
    fi
    
    if [[ "$statut" -eq 1 ]]
    then
        # Le script original a été joué en base, on peut le défaire.
        # Execution du script de rollback
        echo `date +%y/%m/%d` `date +%H:%M:%S` "Verification de l'etat du script en base..." >> $LOG_FILE
        echo `date +%y/%m/%d` `date +%H:%M:%S` "INFO: Script $orig_script deja execute (STATUT=1) - passage au rollback" >> $LOG_FILE
        
        echo `date +%y/%m/%d` `date +%H:%M:%S` "Execution du script de rollback $script" >> $LOG_FILE
        
        sqlplus -s $USER/$LUCA_PASSWORD@$IP_SERVER/$SERVICE_NAME <<EOF
WHENEVER SQLERROR EXIT FAILURE ROLLBACK;
set echo on
set SQLBLANKLINES ON
@$script;
commit;
exit;
EOF
        
        if [[ $? -ne 0 ]]
        then
            echo `date +%y/%m/%d` `date +%H:%M:%S` "Erreur lors de l'execution du script de rollback $script" >> $LOG_FILE
            echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: <6>" >> $LOG_FILE
            exit 6
        fi
        
        # Mise a jour de la ligne correspondant au script original dans SCRIPT_HISTORY
        sqlplus -s $USER/$LUCA_PASSWORD@$IP_SERVER/$SERVICE_NAME <<EOF
WHENEVER SQLERROR EXIT FAILURE ROLLBACK;
set echo on
DELETE FROM SCRIPT_HISTORY WHERE NOM_SCRIPT='$orig_script' and CATS_PACKAGE='$CATS_PKG';
INSERT INTO ROLLBACK_HISTORY (VERSION,ID,NOM_SCRIPT,STATUT,DATE_ROLLBACK,CATS_PACKAGE) VALUES ('$version','$id','$script',1,sysdate,'$CATS_PKG');
COMMIT;
exit;
EOF
        
        if [[ $? -ne 0 ]]
        then
            echo `date +%y/%m/%d` `date +%H:%M:%S` "Erreur lors de la mise a jour dans SCRIPT_HISTORY ou ROLLBACK_HISTORY" >> $LOG_FILE
            echo `date +%y/%m/%d` `date +%H:%M:%S` "Sortie en erreur. Code retour: <7>" >> $LOG_FILE
            exit 7
        fi
        
        echo `date +%y/%m/%d` `date +%H:%M:%S` "Script $script execute avec succes" >> $LOG_FILE
        scripts_executes=$((scripts_executes + 1))
        
    else
        echo `date +%y/%m/%d` `date +%H:%M:%S` "INFO: Script $orig_script non execute (STATUT=$statut) - pas de rollback necessaire" >> $LOG_FILE
        scripts_ignores=$((scripts_ignores + 1))
    fi
    
    statut=''
done

# Suppression des fichiers extraits
cd $rep_depart
rm -r $rep_script

echo `date +%y/%m/%d` `date +%H:%M:%S` "======================================" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "=== BILAN PHASE ROLLBACK SCRIPTS ===" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "======================================" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Scripts traites: $scripts_traites" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Scripts executes: $scripts_executes" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Scripts ignores (deja rollback): $scripts_ignores" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "======================================" >> $LOG_FILE

echo `date +%y/%m/%d` `date +%H:%M:%S` "======================================" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "=== ROLLBACK TERMINEE AVEC SUCCES ===" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "======================================" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "Parametres du deploiement:" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Service Name: $SERVICE_NAME" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Utilisateur: $USER" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Serveur IP: $IP_SERVER" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Package rollback: $CATS_PKG" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "  - Fichier de log: $LOG_FILE" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "======================================" >> $LOG_FILE
echo `date +%y/%m/%d` `date +%H:%M:%S` "=== FIN SCRIPT ROLLBACK === Code retour: 0" >> $LOG_FILE

exit 0
