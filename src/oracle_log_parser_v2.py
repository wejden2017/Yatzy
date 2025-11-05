#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle Database Deployment Log Parser and HTML Report Generator
Analyseur de logs de déploiement Oracle et générateur de rapports HTML
"""

import re
import sys
from datetime import datetime
from collections import defaultdict, namedtuple
from pathlib import Path

# Structure pour stocker les informations de script
ScriptInfo = namedtuple('ScriptInfo', [
    'name', 'status', 'execution_time', 'rollback_available', 
    'already_executed', 'error_message', 'oracle_result'
])

# Structure pour stocker les informations de package
PackageInfo = namedtuple('PackageInfo', [
    'name', 'type', 'status', 'execution_time', 'error_message'
])

class OracleLogParser:
    def __init__(self):
        self.deployment_info = {}
        self.scripts = []
        self.packages = []
        self.errors = []
        self.warnings = []
        self.deployment_type = 'UNKNOWN'  # INSTALL ou ROLLBACK
        self.summary = {
            'total_scripts': 0,
            'executed_scripts': 0,
            'skipped_scripts': 0,
            'failed_scripts': 0,
            'total_packages': 0,
            'created_packages': 0,
            'failed_packages': 0
        }
        
    def parse_log_file(self, log_file_path):
        """Parse le fichier de log Oracle"""
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(log_file_path, 'r', encoding='latin-1') as f:
                content = f.read()
                
        lines = content.split('\n')
        self._parse_deployment_info(lines)
        self._parse_scripts_phase(lines)
        self._parse_packages_phase(lines)
        self._calculate_summary()
        
    def _parse_deployment_info(self, lines):
        """Extrait les informations de déploiement du début du log"""
        for line in lines:
            # Détecter le type de déploiement
            if 'install_dba_scripts_cloud.ksh' in line:
                self.deployment_type = 'INSTALL'
            elif 'rollback_dba_scripts_cloud.ksh' in line:
                self.deployment_type = 'ROLLBACK'
                
            # Ligne avec tous les paramètres
            if 'Parametres:' in line and 'SERVICE_NAME=' in line:
                # Extraire tous les paramètres de cette ligne
                service_match = re.search(r'SERVICE_NAME=(\w+)', line)
                user_match = re.search(r'USER=(\w+)', line)
                ip_match = re.search(r'IP_SERVER=([\d.]+)', line)
                package_match = re.search(r'PACKAGE=([^\s]+)', line)
                
                if service_match:
                    self.deployment_info['service_name'] = service_match.group(1)
                if user_match:
                    self.deployment_info['user'] = user_match.group(1)
                if ip_match:
                    self.deployment_info['ip_server'] = ip_match.group(1)
                if package_match:
                    self.deployment_info['package'] = package_match.group(1)
                    
            elif 'DEBUT SCRIPT CLOUD' in line:
                timestamp_match = re.search(r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})', line)
                if timestamp_match:
                    self.deployment_info['start_time'] = timestamp_match.group(1)
                    
    def _parse_scripts_phase(self, lines):
        """Parse la phase d'exécution des scripts SQL"""
        in_script_phase = False
        current_script = None
        script_start_time = None
        
        for i, line in enumerate(lines):
            # Détection du début de phase scripts
            if 'Nombre de scripts SQL detectes:' in line or 'Nombre de scripts ROLLBACK detectes:' in line:
                match = re.search(r'(\d+)', line)
                if match:
                    self.summary['total_scripts'] = int(match.group(1))
                in_script_phase = True
                continue
                
            # Fin de phase scripts
            if 'BILAN PHASE CATS-SCRIPT:' in line or 'BILAN PHASE ROLLBACK:' in line:
                in_script_phase = False
                self._parse_script_summary(lines[i:i+10])
                continue
                
            if not in_script_phase:
                continue
                
            # Traitement d'un script (pour install et rollback)
            script_match = re.search(r'Traitement script \d+/\d+ : (.+\.sql)', line)
            if not script_match and self.deployment_type == 'ROLLBACK':
                script_match = re.search(r'Execution rollback \d+/\d+ : (.+\.sql)', line)
                
            if script_match:
                current_script = script_match.group(1)
                timestamp_match = re.search(r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})', line)
                script_start_time = timestamp_match.group(1) if timestamp_match else None
                continue
                
            if current_script:
                # Vérification rollback (pour install uniquement)
                rollback_available = False
                if 'Rollback disponible:' in line and self.deployment_type == 'INSTALL':
                    rollback_available = True
                    
                # Script déjà exécuté
                if 'deja execute (STATUT=1) - passage au suivant' in line:
                    self.scripts.append(ScriptInfo(
                        name=current_script,
                        status='SKIPPED',
                        execution_time=script_start_time,
                        rollback_available=rollback_available,
                        already_executed=True,
                        error_message=None,
                        oracle_result=None
                    ))
                    current_script = None
                    continue
                    
                # Pour le rollback - script déjà rollback
                if 'deja rollback (STATUT=0) - passage au suivant' in line:
                    self.scripts.append(ScriptInfo(
                        name=current_script,
                        status='SKIPPED',
                        execution_time=script_start_time,
                        rollback_available=False,
                        already_executed=True,
                        error_message=None,
                        oracle_result=None
                    ))
                    current_script = None
                    continue
                    
                # Script non référencé - insertion en cours
                if 'Script non reference en base - insertion en cours' in line:
                    continue
                    
                # Succès d'enregistrement
                if 'SUCCESS: Script enregistre en base avec STATUT=0' in line:
                    continue
                    
                # Exécution en cours
                if f'EXECUTION du script {current_script} en cours' in line or f'ROLLBACK du script {current_script} en cours' in line:
                    continue
                    
                # Résultat Oracle
                oracle_result = self._extract_oracle_result(line)
                if oracle_result:
                    continue
                    
                # Script terminé avec succès
                if 'execute et marque comme termine (STATUT=1)' in line or 'rollback et marque comme termine (STATUT=0)' in line:
                    self.scripts.append(ScriptInfo(
                        name=current_script,
                        status='SUCCESS',
                        execution_time=script_start_time,
                        rollback_available=rollback_available,
                        already_executed=False,
                        error_message=None,
                        oracle_result=oracle_result if 'oracle_result' in locals() else None
                    ))
                    current_script = None
                    if 'oracle_result' in locals():
                        del oracle_result
                    
    def _parse_packages_phase(self, lines):
        """Parse la phase de compilation des packages PL/SQL"""
        in_package_phase = False
        current_package = None
        
        for line in lines:
            # Détection du début de phase packages
            if 'DEBUT PHASE CATS-PL/SQL' in line:
                in_package_phase = True
                continue
                
            if not in_package_phase:
                continue
                
            # Exécution d'un package
            execution_match = re.search(r'Execution (/[^/]+/pack_.+\.pk[sb])', line)
            if execution_match:
                current_package = execution_match.group(1)
                timestamp_match = re.search(r'(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})', line)
                package_time = timestamp_match.group(1) if timestamp_match else None
                continue
                
            # Résultat de package
            if current_package and 'Package created.' in line:
                package_type = 'PKS' if current_package.endswith('.pks') else 'PKB'
                self.packages.append(PackageInfo(
                    name=current_package,
                    type=package_type,
                    status='SUCCESS',
                    execution_time=package_time if 'package_time' in locals() else None,
                    error_message=None
                ))
                current_package = None
                
    def _extract_oracle_result(self, line):
        """Extrait les résultats Oracle (rows created, tables, etc.)"""
        patterns = [
            r'(\d+) rows? created\.',
            r'(\d+) rows? deleted\.',
            r'Table created\.',
            r'Table altered\.',
            r'PL/SQL procedure successfully completed\.',
            r'Commit complete\.'
        ]
        
        for pattern in patterns:
            if re.search(pattern, line):
                return line.strip()
        return None
        
    def _parse_script_summary(self, lines):
        """Parse le bilan de la phase scripts (install ou rollback)"""
        for i, line in enumerate(lines):
            if '- Scripts traites:' in line or '- Scripts rollback traites:' in line:
                match = re.search(r'- Scripts.*traites:\s*(\d+)', line)
                if match:
                    self.summary['total_scripts'] = int(match.group(1))
            elif '- Scripts executes:' in line or '- Scripts rollback executes:' in line:
                match = re.search(r'- Scripts.*executes:\s*(\d+)', line)
                if match:
                    self.summary['executed_scripts'] = int(match.group(1))
            elif '- Scripts ignores (deja executes):' in line or '- Scripts ignores (deja rollback):' in line:
                match = re.search(r'- Scripts ignores.*:\s*(\d+)', line)
                if match:
                    self.summary['skipped_scripts'] = int(match.group(1))
            elif line.strip() == '':
                break  # Fin du bilan
                    
    def _calculate_summary(self):
        """Calcule les statistiques finales"""
        # Compter les packages
        self.summary['total_packages'] = len(self.packages)
        self.summary['created_packages'] = len([p for p in self.packages if p.status == 'SUCCESS'])
        self.summary['failed_packages'] = len([p for p in self.packages if p.status == 'FAILED'])
        
        # Compter les erreurs
        self.summary['failed_scripts'] = len([s for s in self.scripts if s.status == 'FAILED'])
        
        # Si les données du bilan ne sont pas trouvées, calculer à partir des scripts parsés
        if self.summary['total_scripts'] == 0:
            self.summary['total_scripts'] = len(self.scripts)
        if self.summary['executed_scripts'] == 0:
            self.summary['executed_scripts'] = len([s for s in self.scripts if s.status == 'SUCCESS'])
        if self.summary['skipped_scripts'] == 0:
            self.summary['skipped_scripts'] = len([s for s in self.scripts if s.status == 'SKIPPED'])

class HTMLReportGenerator:
    def __init__(self, parser_result):
        self.parser = parser_result
        
    def generate_report(self, output_path):
        """Génère le rapport HTML"""
        html_content = self._build_html()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
    def _build_html(self):
        """Construit le contenu HTML complet"""
        return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de Déploiement Oracle - {self.parser.deployment_info.get('service_name', 'N/A')}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        {self._build_header()}
        {self._build_summary()}
        {self._build_deployment_info()}
        {self._build_scripts_section()}
        {self._build_packages_section()}
        {self._build_footer()}
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>
"""

    def _get_css_styles(self):
        """Retourne les styles CSS"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .summary-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .summary-card:hover {
            transform: translateY(-5px);
        }
        
        .summary-card .number {
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .summary-card .label {
            font-size: 1.1em;
            color: #666;
        }
        
        .success { color: #28a745; }
        .warning { color: #ffc107; }
        .danger { color: #dc3545; }
        .info { color: #17a2b8; }
        
        .section {
            background: white;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .section-header {
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #dee2e6;
        }
        
        .section-header h2 {
            color: #495057;
            margin-bottom: 5px;
        }
        
        .section-content {
            padding: 20px;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        
        .info-label {
            font-weight: bold;
            color: #495057;
        }
        
        .info-value {
            color: #6c757d;
        }
        
        .table-container {
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        
        th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        
        tr:hover {
            background-color: #f8f9fa;
        }
        
        .status-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 500;
            text-transform: uppercase;
        }
        
        .status-success {
            background-color: #d4edda;
            color: #155724;
        }
        
        .status-skipped {
            background-color: #fff3cd;
            color: #856404;
        }
        
        .status-failed {
            background-color: #f8d7da;
            color: #721c24;
        }
        
        .toggle-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 15px;
        }
        
        .toggle-btn:hover {
            background: #0056b3;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 0.9em;
        }
        
        .collapsible {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }
        
        .collapsible.show {
            max-height: none;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .summary-grid {
                grid-template-columns: 1fr;
            }
        }
        """
        
    def _build_header(self):
        """Construit l'en-tête du rapport"""
        service_name = self.parser.deployment_info.get('service_name', 'N/A')
        start_time = self.parser.deployment_info.get('start_time', 'N/A')
        deployment_type = self.parser.deployment_type
        
        type_emoji = "⬆️" if deployment_type == "INSTALL" else "⬇️" if deployment_type == "ROLLBACK" else "🗄️"
        type_label = "Installation" if deployment_type == "INSTALL" else "Rollback" if deployment_type == "ROLLBACK" else "Déploiement"
        
        return f"""
        <div class="header">
            <h1>{type_emoji} Rapport de {type_label} Oracle</h1>
            <div class="subtitle">
                Service: {service_name} | Type: {deployment_type} | Démarré le: {start_time}
            </div>
        </div>
        """
        
    def _build_summary(self):
        """Construit la section de résumé"""
        s = self.parser.summary
        deployment_type = self.parser.deployment_type
        
        # Adapter les libellés selon le type de déploiement
        if deployment_type == "ROLLBACK":
            executed_label = "Scripts Rollback"
            skipped_label = "Scripts Ignorés (déjà rollback)"
        else:
            executed_label = "Scripts Exécutés"
            skipped_label = "Scripts Ignorés (déjà exécutés)"
        
        return f"""
        <div class="summary-grid">
            <div class="summary-card">
                <div class="number info">{s['total_scripts']}</div>
                <div class="label">Scripts Total</div>
            </div>
            <div class="summary-card">
                <div class="number success">{s['executed_scripts']}</div>
                <div class="label">{executed_label}</div>
            </div>
            <div class="summary-card">
                <div class="number warning">{s['skipped_scripts']}</div>
                <div class="label">{skipped_label}</div>
            </div>
            <div class="summary-card">
                <div class="number success">{s['created_packages']}</div>
                <div class="label">Packages Créés</div>
            </div>
        </div>
        """
        
    def _build_deployment_info(self):
        """Construit la section d'informations de déploiement"""
        info = self.parser.deployment_info
        deployment_type = self.parser.deployment_type
        
        return f"""
        <div class="section">
            <div class="section-header">
                <h2>📋 Informations de Déploiement</h2>
            </div>
            <div class="section-content">
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Type:</span>
                        <span class="info-value">{deployment_type}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Service:</span>
                        <span class="info-value">{info.get('service_name', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Utilisateur:</span>
                        <span class="info-value">{info.get('user', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Serveur IP:</span>
                        <span class="info-value">{info.get('ip_server', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Package:</span>
                        <span class="info-value">{info.get('package', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Heure de début:</span>
                        <span class="info-value">{info.get('start_time', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Rapport généré:</span>
                        <span class="info-value">{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</span>
                    </div>
                </div>
            </div>
        </div>
        """
        
    def _build_scripts_section(self):
        """Construit la section des scripts"""
        if not self.parser.scripts:
            return ""
            
        table_rows = ""
        for script in self.parser.scripts:
            status_class = f"status-{script.status.lower()}"
            rollback_icon = "✅" if script.rollback_available else "❌"
            
            table_rows += f"""
            <tr>
                <td>{script.name}</td>
                <td><span class="status-badge {status_class}">{script.status}</span></td>
                <td>{script.execution_time or 'N/A'}</td>
                <td>{rollback_icon}</td>
                <td>{'Oui' if script.already_executed else 'Non'}</td>
                <td>{script.oracle_result or '-'}</td>
            </tr>
            """
            
        return f"""
        <div class="section">
            <div class="section-header">
                <h2>📜 Scripts SQL</h2>
                <button class="toggle-btn" onclick="toggleSection('scripts-table')">
                    Afficher/Masquer Détails
                </button>
            </div>
            <div class="section-content">
                <div id="scripts-table" class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Nom du Script</th>
                                <th>Statut</th>
                                <th>Heure d'Exécution</th>
                                <th>Rollback</th>
                                <th>Déjà Exécuté</th>
                                <th>Résultat Oracle</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """
        
    def _build_packages_section(self):
        """Construit la section des packages"""
        if not self.parser.packages:
            return ""
            
        table_rows = ""
        for package in self.parser.packages:
            status_class = f"status-{package.status.lower()}"
            
            table_rows += f"""
            <tr>
                <td>{package.name}</td>
                <td>{package.type}</td>
                <td><span class="status-badge {status_class}">{package.status}</span></td>
                <td>{package.execution_time or 'N/A'}</td>
                <td>{package.error_message or '-'}</td>
            </tr>
            """
            
        return f"""
        <div class="section">
            <div class="section-header">
                <h2>📦 Packages PL/SQL</h2>
                <button class="toggle-btn" onclick="toggleSection('packages-table')">
                    Afficher/Masquer Détails
                </button>
            </div>
            <div class="section-content">
                <div id="packages-table" class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Nom du Package</th>
                                <th>Type</th>
                                <th>Statut</th>
                                <th>Heure d'Exécution</th>
                                <th>Message d'Erreur</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """
        
    def _build_footer(self):
        """Construit le pied de page"""
        return f"""
        <div class="footer">
            <p>Rapport généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
            <p>Analyseur de logs Oracle Database Deployment</p>
        </div>
        """
        
    def _get_javascript(self):
        """Retourne le JavaScript pour l'interactivité"""
        return """
        function toggleSection(sectionId) {
            const section = document.getElementById(sectionId);
            if (section.classList.contains('show')) {
                section.classList.remove('show');
                section.style.maxHeight = '0';
            } else {
                section.classList.add('show');
                section.style.maxHeight = section.scrollHeight + 'px';
            }
        }
        
        // Initialiser les sections comme visibles
        document.addEventListener('DOMContentLoaded', function() {
            const tables = document.querySelectorAll('.table-container');
            tables.forEach(table => {
                table.classList.add('show');
                table.style.maxHeight = table.scrollHeight + 'px';
            });
        });
        """

def main():
    """Fonction principale"""
    if len(sys.argv) != 2:
        print("Usage: python oracle_log_parser.py <log_file_path>")
        print("Exemple: python oracle_log_parser.py deployment.log")
        sys.exit(1)
        
    log_file = sys.argv[1]
    
    if not Path(log_file).exists():
        print(f"Erreur: Le fichier {log_file} n'existe pas.")
        sys.exit(1)
        
    print(f"🔍 Analyse du fichier de log: {log_file}")
    
    # Parser le fichier de log
    parser = OracleLogParser()
    parser.parse_log_file(log_file)
    
    # Générer le rapport HTML
    output_file = Path(log_file).stem + "_rapport.html"
    generator = HTMLReportGenerator(parser)
    generator.generate_report(output_file)
    
    print(f"✅ Rapport généré: {output_file}")
    print(f"📊 Résumé:")
    print(f"   - Scripts total: {parser.summary['total_scripts']}")
    print(f"   - Scripts exécutés: {parser.summary['executed_scripts']}")
    print(f"   - Scripts ignorés: {parser.summary['skipped_scripts']}")
    print(f"   - Packages créés: {parser.summary['created_packages']}")

if __name__ == "__main__":
    main()
