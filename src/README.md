# Analyseur de Logs de Déploiement Oracle - Version 2.0

## Description

Ce script Python analyse les fichiers de logs de mise à jour ET de rollback de base de données Oracle générés par vos rôles Ansible `update_database` et `rollback_database` et produit des rapports HTML détaillés et visuellement attrayants.

## 🆕 Nouveautés Version 2.0

✅ **Support dual des rôles Ansible**
- Compatible avec les logs d'`update_database` (install_dba_scripts_cloud.log)
- Compatible avec les logs de `rollback_database` (rollback_dba_scripts_cloud.log)
- Détection automatique du type de déploiement
- Libellés et icônes adaptés selon le type

✅ **Rapports différenciés**
- 🔺 **Installation** : "⬆️ Rapport d'Installation Oracle"
- 🔻 **Rollback** : "⬇️ Rapport de Rollback Oracle"
- Terminologie adaptée (Scripts Rollback vs Scripts Exécutés)
- Statuts spécifiques (déjà rollback vs déjà exécutés)

## Fonctionnalités

✅ **Parsing complet des logs Oracle**
- Extraction automatique des informations de déploiement
- Support des deux phases : CATS-SCRIPT et CATS-PL/SQL
- Analyse des scripts avec rollback disponible (installation uniquement)
- Suivi des packages PL/SQL compilés

✅ **Détection intelligente**
- Reconnaissance automatique install vs rollback
- Parsing du bilan officiel pour statistiques précises
- Gestion des statuts STATUT=0 (rollback) et STATUT=1 (installé)

✅ **Rapport HTML professionnel**
- Design moderne responsive
- Cartes de résumé avec métriques visuelles
- Tableaux détaillés avec statuts colorés
- Sections pliables interactives

## Installation

Aucune dépendance externe ! Utilise uniquement les modules Python standards.

## Utilisation

### Utilisation universelle
```bash
python oracle_log_parser_v2.py <fichier_log>
```

### Exemples concrets avec vos rôles Ansible

**Pour un déploiement (update_database) :**
```bash
python oracle_log_parser_v2.py install_dba_scripts_cloud.log
# → Génère: install_dba_scripts_cloud_rapport.html
```

**Pour un rollback (rollback_database) :**
```bash
python oracle_log_parser_v2.py rollback_dba_scripts_cloud.log
# → Génère: rollback_dba_scripts_cloud_rapport.html
```

## Format de logs supportés

### Logs d'installation (update_database)
```
25/11/05 16:07:05 === DEBUT SCRIPT CLOUD ./install_dba_scripts_cloud.ksh ===
25/11/05 16:07:05 Parametres: SERVICE_NAME=CATSDEVPDB1 USER=luca IP_SERVER=10.105.57.186 PACKAGE=cats_7.01.03_001
...
25/11/05 16:07:06 DEBUT PHASE CATS-SCRIPT
25/11/05 16:07:06 Nombre de scripts SQL detectes: 26
25/11/05 16:07:06 Traitement script 1/26 : script.sql
25/11/05 16:07:06 Rollback disponible: rollback/script_ROLLBACK.sql
...
25/11/05 16:07:11 BILAN PHASE CATS-SCRIPT:
25/11/05 16:07:11    - Scripts traites: 26
25/11/05 16:07:11    - Scripts executes: 3
25/11/05 16:07:11    - Scripts ignores (deja executes): 23
```

### Logs de rollback (rollback_database)
```
25/11/05 18:15:22 === DEBUT SCRIPT CLOUD ./rollback_dba_scripts_cloud.ksh ===
25/11/05 18:15:22 Parametres: SERVICE_NAME=CATSDEVPDB1 USER=luca IP_SERVER=10.105.57.186 PACKAGE=cats_7.01.03_001
...
25/11/05 18:15:23 DEBUT PHASE ROLLBACK
25/11/05 18:15:23 Nombre de scripts ROLLBACK detectes: 15
25/11/05 18:15:23 Execution rollback 1/15 : script_ROLLBACK.sql
...
25/11/05 18:15:25 BILAN PHASE ROLLBACK:
25/11/05 18:15:25    - Scripts rollback traites: 15
25/11/05 18:15:25    - Scripts rollback executes: 3
25/11/05 18:15:25    - Scripts ignores (deja rollback): 12
```

## Structure des rapports générés

### Installation (install_dba_scripts_cloud.log)
- **En-tête** : "⬆️ Rapport d'Installation Oracle"
- **Type** : INSTALL
- **Métriques** : Scripts Exécutés, Scripts Ignorés (déjà exécutés)
- **Rollback** : Indicateur ✅/❌ de disponibilité

### Rollback (rollback_dba_scripts_cloud.log) 
- **En-tête** : "⬇️ Rapport de Rollback Oracle"
- **Type** : ROLLBACK  
- **Métriques** : Scripts Rollback, Scripts Ignorés (déjà rollback)
- **Rollback** : Non applicable

## Intégration avec vos rôles Ansible

Le script est conçu pour s'intégrer parfaitement avec vos rôles existants :

### Variables supportées
```yaml
# Variables de vos rôles update_database/rollback_database
cats_path: "/opt/cats"
deploy_folder: "deploy"  
oracle_user: "luca"
oracle_port: "1521"
oracle_logs_dir: "/opt/cats/logs"
oracle_install_script_log: "install_dba_scripts_cloud.log"
oracle_rollback_script_log: "rollback_dba_scripts_cloud.log"
```

### Workflow recommandé
1. Exécution du rôle Ansible (`update_database` ou `rollback_database`)
2. Génération automatique du log dans `{{ oracle_logs_dir }}`
3. Exécution du parser : `python oracle_log_parser_v2.py {{ oracle_logs_dir }}/{{ log_file }}`
4. Consultation du rapport HTML généré

## Exemple de sorties

**Installation :**
```
🔍 Analyse du fichier de log: install_dba_scripts_cloud.log
✅ Rapport généré: install_dba_scripts_cloud_rapport.html
📊 Résumé:
   - Scripts total: 26
   - Scripts exécutés: 3
   - Scripts ignorés: 23
   - Packages créés: 7
```

**Rollback :**
```
🔍 Analyse du fichier de log: rollback_dba_scripts_cloud.log
✅ Rapport généré: rollback_dba_scripts_cloud_rapport.html
📊 Résumé:
   - Scripts total: 15
   - Scripts exécutés: 3
   - Scripts ignorés: 12
   - Packages créés: 0
```

## Fichiers inclus

- `oracle_log_parser_v2.py` : Script principal amélioré
- `exemple_log_oracle_rapport.html` : Exemple de rapport d'installation
- `exemple_rollback_oracle_rapport.html` : Exemple de rapport de rollback
- `README.md` : Cette documentation

## Support et évolutions

✅ **Testé avec vos rôles Ansible existants**
✅ **Compatible install_dba_scripts_cloud.ksh et rollback_dba_scripts_cloud.ksh**
✅ **Parsing intelligent des deux types de bilans**
✅ **Génération de rapports différenciés**

Le script est prêt à être utilisé en production avec vos déploiements Oracle !

---
*Générateur de rapports Oracle Database Deployment - Version 2.0*
*Compatible rôles Ansible update_database et rollback_database*
