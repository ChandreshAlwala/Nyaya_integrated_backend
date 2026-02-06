"""
Legal Data Loader for Nyaya AI Backend
Loads and processes legal data from jurisdiction-specific JSON datasets
"""
import json
import os
import re
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

class LegalDataLoader:
    """Handles loading and querying legal data from JSON datasets"""
    
    def __init__(self, data_directory: str = "Nyaya_AI/db"):
        self.data_directory = data_directory
        self.domain_maps = {}
        self.law_datasets = {}
        self._load_domain_maps()
        self._load_law_datasets()
        # Initialize fallback provisions
        self.fallback_provisions = {
            'UAE': {
                'murder': {
                    'type': 'criminal_law',
                    'law': 'Federal Penal Code Law No. 3 of 1987',
                    'section': 'Articles related to homicide and murder',
                    'title': 'Homicide and Murder Offences',
                    'offence': 'Intentional killing of another person or causing death through criminal negligence',
                    'definition': 'The unlawful killing of a human being with malice aforethought, including premeditated murder, voluntary manslaughter, and other forms of homicide under UAE Federal Penal Code',
                    'elements': [
                        'Intentional act causing death of another person',
                        'Malice aforethought or criminal negligence',
                        'Absence of legal justification or excuse',
                        'Causation between act and death'
                    ],
                    'punishment': {
                        'murder': 'Death penalty or life imprisonment for premeditated murder',
                        'manslaughter': 'Imprisonment from 3 to 15 years for voluntary manslaughter',
                        'negligent_homicide': 'Imprisonment up to 10 years for criminal negligence causing death'
                    },
                    'process': [
                        'Immediate police investigation and crime scene preservation',
                        'Medical examiner autopsy and cause of death determination',
                        'Collection of forensic evidence and witness statements',
                        'Public prosecution review and charging decision',
                        'Criminal court trial with right to legal representation',
                        'Supreme Court jurisdiction for death penalty cases',
                        'Possibility of royal pardon or sentence reduction'
                    ],
                    'citations': [
                        'UAE Federal Penal Code Law No. 3 of 1987, relevant articles on homicide',
                        'UAE Constitution Article 18 - Right to life protection',
                        'UAE Criminal Procedure Code for trial procedures',
                        'Sharia law principles applicable to homicide cases'
                    ]
                },
                'killed': {
                    'type': 'criminal_law',
                    'law': 'Federal Penal Code Law No. 3 of 1987',
                    'section': 'Homicide and related offences',
                    'title': 'Causing Death Through Criminal Acts',
                    'offence': 'Causing death of another person through intentional or negligent criminal acts',
                    'definition': 'Any criminal act that directly or indirectly results in the death of another person, including murder, manslaughter, and death caused through other criminal offences',
                    'elements': [
                        'Criminal act or omission',
                        'Death of another person',
                        'Causal connection between act and death',
                        'Criminal intent or negligence'
                    ],
                    'punishment': {
                        'intentional': 'Death penalty or life imprisonment',
                        'negligent': 'Imprisonment from 1 to 10 years',
                        'aggravated': 'Enhanced penalties for specific circumstances'
                    },
                    'process': [
                        'Emergency response and crime scene investigation',
                        'Forensic analysis and evidence collection',
                        'Witness interrogation and suspect identification',
                        'Prosecution case building and charging',
                        'Trial in criminal court with full legal rights',
                        'Appeal process through court hierarchy',
                        'Execution or imprisonment based on verdict'
                    ],
                    'citations': [
                        'UAE Federal Penal Code Law No. 3 of 1987',
                        'UAE Criminal Procedure Law',
                        'UAE Evidence Law for criminal proceedings',
                        'International human rights standards applicable'
                    ]
                }
            }
        }
    
    def _load_domain_maps(self):
        """Load all domain mapping files"""
        domain_files = {
            'IN': 'indian_domain_map.json',
            'UAE': 'uae_domain_map.json', 
            'UK': 'uk_domain_map.json'
        }
        
        for jurisdiction, filename in domain_files.items():
            filepath = os.path.join(self.data_directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.domain_maps[jurisdiction] = json.load(f)
            except FileNotFoundError:
                print(f"Warning: Domain map not found for {jurisdiction}: {filepath}")
            except Exception as e:
                print(f"Error loading domain map for {jurisdiction}: {e}")
    
    def _load_law_datasets(self):
        """Load all law dataset files"""
        dataset_files = {
            'IN': 'indian_law_dataset.json',
            'UAE': 'uae_law_dataset.json',
            'UK': 'uk_law_dataset.json'
        }
        
        for jurisdiction, filename in dataset_files.items():
            filepath = os.path.join(self.data_directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.law_datasets[jurisdiction] = json.load(f)
            except FileNotFoundError:
                print(f"Warning: Law dataset not found for {jurisdiction}: {filepath}")
            except Exception as e:
                print(f"Error loading law dataset for {jurisdiction}: {e}")
    
    def detect_jurisdiction(self, query: str, jurisdiction_hint: Optional[str] = None) -> str:
        """Detect jurisdiction from query or hint"""
        # Priority: explicit hint > query content > default
        if jurisdiction_hint:
            jurisdiction_map = {
                'IN': 'IN', 'INDIA': 'IN', 'INDIAN': 'IN',
                'UAE': 'UAE', 'DUBAI': 'UAE', 'ABU DHABI': 'UAE',
                'UK': 'UK', 'UNITED KINGDOM': 'UK', 'BRITAIN': 'UK'
            }
            hint_upper = jurisdiction_hint.upper()
            if hint_upper in jurisdiction_map:
                return jurisdiction_map[hint_upper]
        
        # Check query for jurisdiction indicators
        query_upper = query.upper()
        if any(term in query_upper for term in ['INDIA', 'INDIAN']):
            return 'IN'
        elif any(term in query_upper for term in ['UAE', 'DUBAI', 'ABU DHABI', 'SHARJAH']):
            return 'UAE'
        elif any(term in query_upper for term in ['UK', 'UNITED KINGDOM', 'BRITAIN', 'ENGLAND']):
            return 'UK'
        
        # Default to India
        return 'IN'
    
    def classify_domain(self, query: str, jurisdiction: str) -> Tuple[str, str, float]:
        """Classify query domain and subdomain using domain mapping with improved semantic matching"""
        if jurisdiction not in self.domain_maps:
            return 'civil', 'general', 0.5
        
        domain_map = self.domain_maps[jurisdiction]
        keyword_mapping = domain_map.get('keyword_mapping', {})
        
        # Count keyword matches for each subdomain with semantic weights
        domain_scores = defaultdict(float)
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for subdomain, keywords in keyword_mapping.items():
            # Exact phrase matches get higher weight
            exact_matches = 0
            partial_matches = 0
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # Check for exact phrase match
                if keyword_lower in query_lower:
                    exact_matches += 1
                
                # Check for word matches
                keyword_words = set(keyword_lower.split())
                intersection = query_words.intersection(keyword_words)
                partial_matches += len(intersection)
            
            # Calculate weighted score
            if exact_matches > 0:
                # Prioritize exact matches
                domain_scores[subdomain] = min(1.0, (exact_matches * 2 + partial_matches) / len(keywords))
            elif partial_matches > 0:
                domain_scores[subdomain] = min(0.8, partial_matches / len(keywords))
        
        # Find best matching subdomain
        if domain_scores:
            best_subdomain = max(domain_scores, key=domain_scores.get)
            confidence = domain_scores[best_subdomain]
            
            # Map subdomain to main domain
            domain_mapping = domain_map.get('domain_mapping', {})
            for main_domain, config in domain_mapping.items():
                if best_subdomain in config.get('subdomains', []):
                    return main_domain, best_subdomain, confidence
        
        # Fallback to default
        fallback = domain_map.get('fallback_rules', {})
        default_domain = fallback.get('default_domain', 'civil')
        return default_domain, 'general', 0.3
    
    def search_law_data(self, query: str, jurisdiction: str, domain: str, subdomain: str) -> List[Dict]:
        """Search for relevant legal data in the dataset"""
        if jurisdiction not in self.law_datasets:
            return []
        
        dataset = self.law_datasets[jurisdiction]
        results = []
        
        # Search strategy varies by jurisdiction
        if jurisdiction == 'IN':
            results = self._search_indian_law(query, dataset, domain, subdomain)
        elif jurisdiction == 'UAE':
            results = self._search_uae_law(query, dataset, domain, subdomain)
        elif jurisdiction == 'UK':
            results = self._search_uk_law(query, dataset, domain, subdomain)
        
        return results
    
    def _evaluate_relevance(self, query: str, legal_title: str, legal_content: str) -> bool:
        """Evaluate if a legal provision is truly relevant to the query"""
        query_lower = query.lower()
        title_lower = legal_title.lower()
        content_lower = legal_content.lower()
        
        # Check for semantic relevance - if the query contains tech terms but the result is about personal status/family law
        tech_query_terms = {'phone', 'mobile', 'device', 'access', 'unauthorized', 'cyber', 'hacking', 
                           'computer', 'digital', 'electronic', 'privacy', 'data', 'security'}
        personal_status_terms = {'divorce', 'marriage', 'family', 'personal status', 'child support', 
                                'custody', 'spouse', 'inheritance', 'will', 'estate', 'property division'}
        
        query_has_tech = any(term in query_lower for term in tech_query_terms)
        result_has_personal = any(term in (title_lower + " " + content_lower) for term in personal_status_terms)
        
        # If query is about technology but result is about personal/family law, it's likely irrelevant
        if query_has_tech and result_has_personal:
            return False
            
        # Check if both relate to similar topics
        if query_has_tech:
            tech_result_terms = {'computer', 'digital', 'electronic', 'phone', 'mobile', 'device', 'access', 
                               'unauthorized', 'cyber', 'hacking', 'data', 'privacy', 'telecommunication',
                               'internet', 'network', 'fraud', 'theft', 'unauthorized access', 'intrusion',
                               'hacking', 'malware', 'virus', 'identity theft', 'phishing'}
            tech_in_result = any(term in (title_lower + " " + content_lower) for term in tech_result_terms)
            return tech_in_result
            
        return True  # Default to true for non-tech queries

    def _search_indian_law(self, query: str, dataset: Dict, domain: str, subdomain: str) -> List[Dict]:
        """Search Indian law dataset with improved semantic matching"""
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Look for technology-related terms
        tech_terms = {'computer', 'digital', 'electronic', 'phone', 'mobile', 'device', 'access', 
                     'unauthorized', 'cyber', 'hacking', 'data', 'privacy', 'telecommunication',
                     'smartphone', 'tablet', 'laptop', 'internet', 'network', 'wifi', 'bluetooth',
                     'malware', 'virus', 'trojan', 'spyware', 'phishing', 'identity theft',
                     'online', 'e-commerce', 'digital signature', 'encryption'}
        
        # Enhanced tech query mapping - map common tech queries to relevant legal concepts
        tech_query_mapping = {
            'unauthorized access': ['unauthorized access', 'computer misuse', 'cyber theft', 'data theft', 'intrusion', 'hacking'],
            'phone': ['phone', 'mobile', 'device', 'electronic', 'telecommunication'],
            'privacy': ['privacy', 'data protection', 'personal information'],
            'hacking': ['hacking', 'cyber attack', 'intrusion', 'unauthorized access'],
            'computer': ['computer', 'digital', 'electronic', 'device']
        }
        
        # Fallback provisions for common queries by jurisdiction
        fallback_provisions = {
            'UAE': {
                'murder': {
                    'type': 'criminal_law',
                    'law': 'Federal Penal Code Law No. 3 of 1987',
                    'section': 'Articles related to homicide and murder',
                    'title': 'Homicide and Murder Offences',
                    'offence': 'Intentional killing of another person or causing death through criminal negligence',
                    'definition': 'The unlawful killing of a human being with malice aforethought, including premeditated murder, voluntary manslaughter, and other forms of homicide under UAE Federal Penal Code',
                    'elements': [
                        'Intentional act causing death of another person',
                        'Malice aforethought or criminal negligence',
                        'Absence of legal justification or excuse',
                        'Causation between act and death'
                    ],
                    'punishment': {
                        'murder': 'Death penalty or life imprisonment for premeditated murder',
                        'manslaughter': 'Imprisonment from 3 to 15 years for voluntary manslaughter',
                        'negligent_homicide': 'Imprisonment up to 10 years for criminal negligence causing death'
                    },
                    'process': [
                        'Immediate police investigation and crime scene preservation',
                        'Medical examiner autopsy and cause of death determination',
                        'Collection of forensic evidence and witness statements',
                        'Public prosecution review and charging decision',
                        'Criminal court trial with right to legal representation',
                        'Supreme Court jurisdiction for death penalty cases',
                        'Possibility of royal pardon or sentence reduction'
                    ],
                    'citations': [
                        'UAE Federal Penal Code Law No. 3 of 1987, relevant articles on homicide',
                        'UAE Constitution Article 18 - Right to life protection',
                        'UAE Criminal Procedure Code for trial procedures',
                        'Sharia law principles applicable to homicide cases'
                    ]
                },
                'killed': {
                    'type': 'criminal_law',
                    'law': 'Federal Penal Code Law No. 3 of 1987',
                    'section': 'Homicide and related offences',
                    'title': 'Causing Death Through Criminal Acts',
                    'offence': 'Causing death of another person through intentional or negligent criminal acts',
                    'definition': 'Any criminal act that directly or indirectly results in the death of another person, including murder, manslaughter, and death caused through other criminal offences',
                    'elements': [
                        'Criminal act or omission',
                        'Death of another person',
                        'Causal connection between act and death',
                        'Criminal intent or negligence'
                    ],
                    'punishment': {
                        'intentional': 'Death penalty or life imprisonment',
                        'negligent': 'Imprisonment from 1 to 10 years',
                        'aggravated': 'Enhanced penalties for specific circumstances'
                    },
                    'process': [
                        'Emergency response and crime scene investigation',
                        'Forensic analysis and evidence collection',
                        'Witness interrogation and suspect identification',
                        'Prosecution case building and charging',
                        'Trial in criminal court with full legal rights',
                        'Appeal process through court hierarchy',
                        'Execution or imprisonment based on verdict'
                    ],
                    'citations': [
                        'UAE Federal Penal Code Law No. 3 of 1987',
                        'UAE Criminal Procedure Law',
                        'UAE Evidence Law for criminal proceedings',
                        'International human rights standards applicable'
                    ]
                }
            }
        }
        fallback_tech_provisions = {
            'unauthorized access to phone': {
                'type': 'it_act_section',
                'section': 'IT Act Section 43, 66',
                'title': 'Unauthorized Access to Electronic Devices',
                'description': 'Unauthorized access to computer resources, electronic devices, or communication systems including mobile phones, smartphones, and other digital devices',
                'definition': 'Any person who, without permission, accesses or attempts to access any computer resource, electronic device, or communication system including mobile phones, smartphones, tablets, laptops, or network systems',
                'elements': [
                    'Unauthorized access to electronic device or system',
                    'Knowledge of lack of authorization',
                    'Actual or attempted access',
                    'Damage or potential damage to system or data'
                ],
                'penalties': {
                    'compensation': 'Up to Rs. 1 crore under Section 43',
                    'imprisonment': 'Up to 3 years under Section 66',
                    'fine': 'As determined by court under Section 66'
                },
                'process': [
                    'File complaint with local Cyber Crime Cell or Police Station',
                    'Submit digital evidence (screenshots, logs, device information)',
                    'Police investigation including device examination',
                    'Digital forensics analysis by certified experts',
                    'Collection of network logs and communication records',
                    'Summoning of witnesses and technical experts',
                    'Trial in designated Cyber Crime Court or Special Court',
                    'Possibility of compensation order under Section 43'
                ],
                'citations': [
                    'Information Technology Act, 2000, Section 43 - Penalty for damage to computer systems',
                    'Information Technology Act, 2000, Section 66 - Computer related offences',
                    'Indian Penal Code, Section 420 - Cheating and dishonestly inducing delivery of property (if applicable)',
                    'Bharatiya Nyaya Sanhita, Section 303-307 - Theft (if data theft involved)'
                ]
            },
            'phone hacking': {
                'type': 'it_act_section',
                'section': 'IT Act Section 66, 72',
                'title': 'Phone Hacking and Data Theft',
                'description': 'Hacking into mobile devices, unauthorized interception of electronic communications, breach of data confidentiality, and unauthorized access to personal information stored on mobile devices',
                'definition': 'Unauthorized intrusion into mobile devices, interception of electronic communications, extraction of personal data without consent, or manipulation of device functions without authorization',
                'elements': [
                    'Unauthorized access to mobile device or its data',
                    'Interception of electronic communications',
                    'Extraction or manipulation of personal data',
                    'Knowledge of unauthorized nature of access',
                    'Damage or potential damage to victim or data'
                ],
                'penalties': {
                    'imprisonment': 'Up to 3 years under Section 66',
                    'fine': 'As determined by court under Section 66',
                    'privacy_breach': 'Up to 2 years imprisonment under Section 72'
                },
                'process': [
                    'Lodge First Information Report (FIR) with Cyber Cell',
                    'Immediate preservation of digital evidence from device',
                    'Forensic examination of mobile device and SIM card',
                    'Analysis of call logs, messages, and app data',
                    'Network provider cooperation for tower records',
                    'Technical expert testimony on hacking methods',
                    'Cross-examination of digital evidence',
                    'Special court trial with cyber crime expertise'
                ],
                'citations': [
                    'Information Technology Act, 2000, Section 66 - Computer related offences',
                    'Information Technology Act, 2000, Section 72 - Breach of confidentiality and privacy',
                    'Indian Telegraph Act, Section 25 - Interception of electronic communications',
                    'Bharatiya Nyaya Sanhita, Section 463-468 - Forgery (if data manipulation involved)'
                ]
            },
            'cyber crime phone': {
                'type': 'it_act_section',
                'section': 'IT Act Chapter IX',
                'title': 'Cyber Crime Involving Mobile Devices',
                'description': 'Various cyber offences committed through mobile phones including unauthorized access, data theft, privacy violations, financial fraud, and digital harassment using mobile technology',
                'definition': 'Any criminal activity involving mobile devices, digital networks, or electronic communications that violates cyber laws, privacy rights, or causes digital harm to individuals or organizations',
                'elements': [
                    'Use of mobile device or digital network for criminal activity',
                    'Violation of cyber laws or privacy rights',
                    'Digital harm to person, property, or reputation',
                    'Knowledge of illegal nature of activity',
                    'Actual or attempted commission of cyber offence'
                ],
                'penalties': {
                    'imprisonment': '3 years to life imprisonment for serious cyber crimes',
                    'fine': 'Substantial monetary penalties as determined by court',
                    'compensation': 'Civil compensation to victims as ordered by court'
                },
                'process': [
                    'Report to Cyber Crime Cell or National Cyber Crime Reporting Portal',
                    'Comprehensive digital forensics investigation',
                    'Preservation of all electronic evidence and communications',
                    'Coordination with telecom providers and internet service providers',
                    'Expert analysis of malware, phishing, or other cyber techniques',
                    'Victim impact assessment and damage evaluation',
                    'Prosecution in designated cyber courts with specialized judges',
                    'Possibility of international cooperation for cross-border crimes'
                ],
                'citations': [
                    'Information Technology Act, 2000, Chapter IX - Offences',
                    'Information Technology (Amendment) Act, 2008 - Enhanced cyber crime provisions',
                    'Indian Penal Code, relevant sections for specific offences',
                    'Bharatiya Nyaya Sanhita, cyber crime related sections'
                ]
            },
            'digital device intrusion': {
                'type': 'it_act_section',
                'section': 'IT Act Section 43, 66',
                'title': 'Digital Device Intrusion and Cyber Security Violations',
                'description': 'Unauthorized intrusion into digital devices, computer systems, networks, and electronic storage devices including hacking, malware installation, and unauthorized data access',
                'definition': 'Any unauthorized entry, access, or manipulation of digital devices, computer systems, networks, databases, or electronic storage systems through technical means including hacking, malware, phishing, or other cyber attack methods',
                'elements': [
                    'Unauthorized access to digital device or system',
                    'Use of technical methods (hacking, malware, etc.)',
                    'Invasion of digital privacy or security',
                    'Knowledge of unauthorized nature of intrusion',
                    'Damage or potential damage to system, data, or user'
                ],
                'penalties': {
                    'compensation': 'Up to Rs. 1 crore under Section 43',
                    'imprisonment': 'Up to 3 years under Section 66',
                    'fine': 'Court-determined penalties under Section 66'
                },
                'process': [
                    'Immediate reporting to Cyber Security Cell or CERT-In',
                    'Digital forensics examination of affected systems',
                    'Network intrusion analysis and threat assessment',
                    'Preservation of malware samples and attack vectors',
                    'Device seizure and comprehensive investigation',
                    'Technical expert evaluation of security breach',
                    'Coordination with cybersecurity agencies',
                    'Specialized cyber court prosecution'
                ],
                'citations': [
                    'Information Technology Act, 2000, Section 43 - Compensation for damage to computer systems',
                    'Information Technology Act, 2000, Section 66 - Computer related offences',
                    'Information Technology (Certification of Electronic Records and Digital Signature) Rules, 2000',
                    'Cyber Security Framework and Guidelines - CERT-In'
                ]
            }
        }
        
        # Check for direct fallback matches
        direct_matches = []
        for pattern, provision in fallback_tech_provisions.items():
            if pattern in query_lower or any(term in query_lower for term in pattern.split()):
                # Create a copy with relevance score
                matched_provision = provision.copy()
                matched_provision['relevance_score'] = 0.9
                matched_provision['confidence'] = 0.9
                direct_matches.append(matched_provision)
        
        # Return direct matches if found (highest priority)
        if direct_matches:
            for match in direct_matches[:3]:  # Top 3 matches
                results.append(match)
            return results
        
        # Search for IT Act sections if tech-related query
        if any(term in query_words for term in tech_terms):
            if 'special_laws' in dataset and 'it_act' in dataset['special_laws']:
                it_act_data = dataset['special_laws']['it_act']
                sections = it_act_data.get('sections', [])
                offences = it_act_data.get('offences', [])
                process_steps = it_act_data.get('process_steps', [])
                
                # Calculate relevance based on tech terms in IT Act data
                it_act_content = ' '.join(offences + sections + process_steps).lower()
                it_act_words = set(it_act_content.split())
                
                # Enhanced matching for tech queries
                tech_query_matches = 0
                for query_term, legal_terms in tech_query_mapping.items():
                    if query_term in query_lower:
                        for legal_term in legal_terms:
                            if legal_term in it_act_content:
                                tech_query_matches += 1
                                break
                
                # Regular word matching
                common_words = query_words.intersection(it_act_words)
                relevance_score = (len(common_words) + tech_query_matches) / max(len(query_words), len(it_act_words))
                
                if relevance_score > 0.05:  # Lower threshold since it's general law area
                    results.append({
                        'type': 'it_act_section',
                        'section': ', '.join(sections),
                        'title': 'Information Technology Act, 2000 - Cyber Crimes',
                        'description': f"Relevant offences: {', '.join(offences)}",
                        'penalties': 'Varies by section - Refer to IT Act 2000',
                        'process': process_steps,
                        'confidence': min(0.85, relevance_score * 2),  # Adjust confidence
                        'relevance_score': relevance_score
                    })
        
        # Search BNS sections (criminal law)
        if 'bns_sections' in dataset:
            for offence, details in dataset['bns_sections'].items():
                # Calculate relevance score based on semantic similarity
                offence_lower = f"{offence} {details.get('offence', '')}".lower()
                offence_words = set(offence_lower.split())
                
                # Calculate overlap
                common_words = query_words.intersection(offence_words)
                tech_overlap = tech_terms.intersection(common_words)
                
                # Calculate relevance score
                relevance_score = len(common_words) / max(len(query_words), len(offence_words))
                
                # Prioritize tech-related matches
                if tech_overlap:
                    relevance_score *= 2.0  # Boost tech matches
                
                # Evaluate semantic relevance
                if relevance_score > 0.1:  # Minimum relevance threshold
                    # Check semantic relevance
                    legal_title = f"{offence} {details.get('offence', '')}"
                    legal_content = f"{details.get('punishment', '')} {details.get('elements_required', [])} {details.get('process_steps', [])}"
                    if self._evaluate_relevance(query, legal_title, legal_content):
                        results.append({
                            'type': 'bns_section',
                            'offence': offence,
                            'section': details.get('section', ''),
                            'punishment': details.get('punishment', ''),
                            'elements': details.get('elements_required', []),
                            'process': details.get('process_steps', []),
                            'confidence': min(0.95, relevance_score),
                            'relevance_score': relevance_score
                        })
        
        # Search IPC sections
        if 'ipc_sections' in dataset:
            for section, details in dataset['ipc_sections'].items():
                # Calculate relevance score based on semantic similarity
                section_lower = f"{section} {details.get('title', '')} {details.get('description', '')}".lower()
                section_words = set(section_lower.split())
                
                # Calculate overlap
                common_words = query_words.intersection(section_words)
                tech_overlap = tech_terms.intersection(common_words)
                
                # Calculate relevance score
                relevance_score = len(common_words) / max(len(query_words), len(section_words))
                
                # Prioritize tech-related matches
                if tech_overlap:
                    relevance_score *= 2.0  # Boost tech matches
                
                if relevance_score > 0.1:  # Minimum relevance threshold
                    # Check semantic relevance
                    legal_title = f"{section} {details.get('title', '')}"
                    legal_content = f"{details.get('description', '')} {details.get('punishment', '')}"
                    if self._evaluate_relevance(query, legal_title, legal_content):
                        results.append({
                            'type': 'ipc_section',
                            'section': section,
                            'title': details.get('title', ''),
                            'description': details.get('description', ''),
                            'punishment': details.get('punishment', ''),
                            'confidence': min(0.9, relevance_score),
                            'relevance_score': relevance_score
                        })
        
        # Search civil procedure code
        if 'cpc_sections' in dataset and domain == 'civil':
            for section, details in dataset['cpc_sections'].items():
                # Calculate relevance score based on semantic similarity
                section_lower = f"{section} {details.get('title', '')}".lower()
                section_words = set(section_lower.split())
                
                # Calculate overlap
                common_words = query_words.intersection(section_words)
                tech_overlap = tech_terms.intersection(common_words)
                
                # Calculate relevance score
                relevance_score = len(common_words) / max(len(query_words), len(section_words))
                
                # Prioritize tech-related matches
                if tech_overlap:
                    relevance_score *= 2.0  # Boost tech matches
                
                if relevance_score > 0.1:  # Minimum relevance threshold
                    # Check semantic relevance
                    legal_title = f"{section} {details.get('title', '')}"
                    legal_content = f"{details.get('procedure', '')}"
                    if self._evaluate_relevance(query, legal_title, legal_content):
                        results.append({
                            'type': 'cpc_section',
                            'section': section,
                            'title': details.get('title', ''),
                            'procedure': details.get('procedure', ''),
                            'confidence': min(0.8, relevance_score),
                            'relevance_score': relevance_score
                        })
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:3]  # Return top 3 matches
    
    def _search_uae_law(self, query: str, dataset: Dict, domain: str, subdomain: str) -> List[Dict]:
        """Search UAE law dataset with improved semantic matching"""
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Check for direct fallback matches for UAE
        uae_fallbacks = self.fallback_provisions.get('UAE', {})
        direct_matches = []
        
        for pattern, provision in uae_fallbacks.items():
            if pattern in query_lower or any(term in query_lower for term in pattern.split()):
                matched_provision = provision.copy()
                matched_provision['relevance_score'] = 0.9
                matched_provision['confidence'] = 0.9
                direct_matches.append(matched_provision)
        
        if direct_matches:
            for match in direct_matches[:3]:  # Top 3 matches
                results.append(match)
            return results
        
        # Look for technology-related terms
        tech_terms = {'computer', 'digital', 'electronic', 'phone', 'mobile', 'device', 'access', 
                     'unauthorized', 'cyber', 'hacking', 'data', 'privacy', 'telecommunication',
                     'smartphone', 'tablet', 'laptop', 'internet', 'network', 'wifi', 'bluetooth',
                     'malware', 'virus', 'trojan', 'spyware', 'phishing', 'identity theft',
                     'online', 'e-commerce', 'digital signature', 'encryption'}
        
        # Search civil law articles
        if 'civil_law' in dataset:
            for law_name, articles in dataset['civil_law'].items():
                for article_id, details in articles.items():
                    # Calculate relevance score based on semantic similarity
                    article_lower = f"{article_id} {details.get('offence', '')} {details.get('title', '')} {details.get('description', '')}".lower()
                    article_words = set(article_lower.split())
                    
                    # Calculate overlap
                    common_words = query_words.intersection(article_words)
                    tech_overlap = tech_terms.intersection(common_words)
                    
                    # Calculate relevance score
                    relevance_score = len(common_words) / max(len(query_words), len(article_words))
                    
                    # Prioritize tech-related matches
                    if tech_overlap:
                        relevance_score *= 2.0  # Boost tech matches
                    
                    if relevance_score > 0.1:  # Minimum relevance threshold
                        # Check semantic relevance
                        legal_title = f"{law_name} {article_id} {details.get('offence', '')}"
                        legal_content = f"{details.get('remedies', [])} {details.get('process_steps', [])} {details.get('description', '')}"
                        if self._evaluate_relevance(query, legal_title, legal_content):
                            results.append({
                                'type': 'civil_law',
                                'law': law_name,
                                'article': article_id,
                                'offence': details.get('offence', ''),
                                'remedies': details.get('civil_remedies', []),
                                'process': details.get('process_steps', []),
                                'confidence': min(0.9, relevance_score),
                                'relevance_score': relevance_score
                            })
        
        # Search criminal law
        if 'criminal_law' in dataset:
            for law_name, sections in dataset['criminal_law'].items():
                for section_id, details in sections.items():
                    # Calculate relevance score based on semantic similarity
                    section_lower = f"{section_id} {details.get('offence', '')} {details.get('title', '')} {details.get('description', '')}".lower()
                    section_words = set(section_lower.split())
                    
                    # Calculate overlap
                    common_words = query_words.intersection(section_words)
                    tech_overlap = tech_terms.intersection(common_words)
                    
                    # Calculate relevance score
                    relevance_score = len(common_words) / max(len(query_words), len(section_words))
                    
                    # Prioritize tech-related matches
                    if tech_overlap:
                        relevance_score *= 2.0  # Boost tech matches
                    
                    if relevance_score > 0.1:  # Minimum relevance threshold
                        # Check semantic relevance
                        legal_title = f"{law_name} {section_id} {details.get('offence', '')}"
                        legal_content = f"{details.get('punishment', '')} {details.get('description', '')}"
                        if self._evaluate_relevance(query, legal_title, legal_content):
                            results.append({
                                'type': 'criminal_law',
                                'law': law_name,
                                'section': section_id,
                                'offence': details.get('offence', ''),
                                'punishment': details.get('punishment', ''),
                                'confidence': min(0.95, relevance_score),
                                'relevance_score': relevance_score
                            })
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:3]
    
    def _search_uk_law(self, query: str, dataset: Dict, domain: str, subdomain: str) -> List[Dict]:
        """Search UK law dataset with improved semantic matching"""
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Look for technology-related terms
        tech_terms = {'computer', 'digital', 'electronic', 'phone', 'mobile', 'device', 'access', 
                     'unauthorized', 'cyber', 'hacking', 'data', 'privacy', 'telecommunication',
                     'smartphone', 'tablet', 'laptop', 'internet', 'network', 'wifi', 'bluetooth',
                     'malware', 'virus', 'trojan', 'spyware', 'phishing', 'identity theft',
                     'online', 'e-commerce', 'digital signature', 'encryption'}
        
        # Search criminal law
        if 'criminal_law' in dataset:
            for section, details in dataset['criminal_law'].items():
                # Calculate relevance score based on semantic similarity
                section_lower = f"{section} {details.get('offence', '')} {details.get('title', '')} {details.get('description', '')}".lower()
                section_words = set(section_lower.split())
                
                # Calculate overlap
                common_words = query_words.intersection(section_words)
                tech_overlap = tech_terms.intersection(common_words)
                
                # Calculate relevance score
                relevance_score = len(common_words) / max(len(query_words), len(section_words))
                
                # Prioritize tech-related matches
                if tech_overlap:
                    relevance_score *= 2.0  # Boost tech matches
                
                if relevance_score > 0.1:  # Minimum relevance threshold
                    # Check semantic relevance
                    legal_title = f"{section} {details.get('offence', '')} {details.get('title', '')}"
                    legal_content = f"{details.get('description', '')} {details.get('punishment', '')}"
                    if self._evaluate_relevance(query, legal_title, legal_content):
                        results.append({
                            'type': 'criminal_law',
                            'section': section,
                            'offence': details.get('offence', ''),
                            'punishment': details.get('punishment', ''),
                            'confidence': min(0.95, relevance_score),
                            'relevance_score': relevance_score
                        })
        
        # Search civil law
        if 'civil_law' in dataset:
            for section, details in dataset['civil_law'].items():
                # Calculate relevance score based on semantic similarity
                section_lower = f"{section} {details.get('title', '')} {details.get('description', '')}".lower()
                section_words = set(section_lower.split())
                
                # Calculate overlap
                common_words = query_words.intersection(section_words)
                tech_overlap = tech_terms.intersection(common_words)
                
                # Calculate relevance score
                relevance_score = len(common_words) / max(len(query_words), len(section_words))
                
                # Prioritize tech-related matches
                if tech_overlap:
                    relevance_score *= 2.0  # Boost tech matches
                
                if relevance_score > 0.1:  # Minimum relevance threshold
                    # Check semantic relevance
                    legal_title = f"{section} {details.get('title', '')}"
                    legal_content = f"{details.get('description', '')} {details.get('procedure', '')}"
                    if self._evaluate_relevance(query, legal_title, legal_content):
                        results.append({
                            'type': 'civil_law',
                            'section': section,
                            'title': details.get('title', ''),
                            'procedure': details.get('procedure', ''),
                            'confidence': min(0.9, relevance_score),
                            'relevance_score': relevance_score
                        })
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:3]
    
    def format_response(self, query: str, jurisdiction: str, domain: str, subdomain: str, 
                       legal_data: List[Dict], confidence: float) -> Dict:
        """Format the final response with comprehensive legal data"""
        if not legal_data:
            return {
                "status": "no_data_found",
                "message": f"No specific legal data found for '{query}' in {jurisdiction} {domain} law",
                "jurisdiction": jurisdiction,
                "domain": domain,
                "confidence": 0.1,
                "legal_guidance": "Please consult with a qualified legal professional for specific advice."
            }
        
        # Format the legal data into comprehensive guidance
        guidance_sections = []
        all_citations = []
        
        for item in legal_data:
            section_data = {}
            
            if item['type'] == 'bns_section':
                section_data = {
                    "title": f"BNS Section {item['section']} - {item['offence']}",
                    "definition": item.get('definition', 'Refer to Bharatiya Nyaya Sanhita for complete definition'),
                    "content": f"Punishment: {item['punishment']}",
                    "elements": item.get('elements', []),
                    "process": item.get('process', []),
                    "penalties": {
                        "imprisonment": item['punishment'],
                        "fine": "As determined by court"
                    }
                }
                all_citations.append(f"Bharatiya Nyaya Sanhita Section {item['section']}")
                
            elif item['type'] == 'ipc_section':
                section_data = {
                    "title": f"IPC {item['section']} - {item['title']}",
                    "definition": item.get('definition', 'Refer to Indian Penal Code for complete definition'),
                    "content": item.get('description', ''),
                    "elements": item.get('elements_required', []),
                    "process": item.get('process_steps', []),
                    "penalties": {
                        "imprisonment": item.get('punishment', 'Refer to IPC section for details'),
                        "fine": "As determined by court"
                    }
                }
                all_citations.append(f"Indian Penal Code Section {item['section']}")
                
            elif item['type'] == 'cpc_section':
                section_data = {
                    "title": f"CPC {item['section']} - {item['title']}",
                    "definition": "Civil procedure provision",
                    "procedure": item.get('procedure', []),
                    "process": item.get('process_steps', [])
                }
                all_citations.append(f"Civil Procedure Code Section {item['section']}")
                
            elif item['type'] == 'it_act_section':
                section_data = {
                    "title": f"IT Act {item['section']} - {item['title']}",
                    "definition": item.get('definition', 'Refer to Information Technology Act for complete definition'),
                    "content": item.get('description', ''),
                    "elements": item.get('elements', []),
                    "process": item.get('process', []),
                    "penalties": item.get('penalties', {
                        "compensation": "As per IT Act provisions",
                        "imprisonment": "As per IT Act provisions",
                        "fine": "As determined by court"
                    }),
                    "citations": item.get('citations', [
                        f"Information Technology Act, 2000, {item['section']}"
                    ])
                }
                # Add specific citations if provided
                if 'citations' in item:
                    all_citations.extend(item['citations'])
                else:
                    all_citations.append(f"Information Technology Act Section {item['section']}")
                
            elif item['type'] == 'civil_law':
                section_data = {
                    "title": f"{item['law']} - {item['article']}",
                    "definition": "Civil law provision",
                    "content": item.get('offence', ''),
                    "remedies": item.get('remedies', []),
                    "process": item.get('process', []),
                    "elements": item.get('elements_required', [])
                }
                all_citations.append(f"{item['law']} {item['article']}")
            
            elif item['type'] == 'criminal_law':
                section_data = {
                    "title": f"{item['law']} - {item['title']}",
                    "definition": item.get('definition', 'Refer to criminal code for complete definition'),
                    "content": item.get('offence', ''),
                    "elements": item.get('elements', []),
                    "process": item.get('process', []),
                    "penalties": item.get('punishment', {
                        "imprisonment": "As prescribed by law",
                        "fine": "As determined by court"
                    }),
                    "citations": item.get('citations', [])
                }
                # Add specific citations if provided
                if 'citations' in item:
                    all_citations.extend(item['citations'])
                else:
                    all_citations.append(f"{item['law']} - {item['title']}")
            
            # Add common fields
            section_data["type"] = item['type']
            section_data["confidence"] = item.get('confidence', confidence)
            section_data["relevance_score"] = item.get('relevance_score', 0.5)
            
            guidance_sections.append(section_data)
        
        return {
            "status": "legal_data_retrieved",
            "message": f"Comprehensive legal guidance for '{query}' in {jurisdiction} {domain} law",
            "jurisdiction": jurisdiction,
            "domain": domain,
            "subdomain": subdomain,
            "confidence": confidence,
            "legal_guidance": guidance_sections,
            "citations": all_citations,
            "disclaimer": "This comprehensive legal information is for general guidance only. Consult qualified legal counsel for specific legal advice and representation.",
            "legal_summary": {
                "total_sections": len(guidance_sections),
                "primary_jurisdiction": jurisdiction,
                "legal_domain": domain,
                "confidence_level": f"{confidence * 100:.1f}%",
                "key_provisions_count": len([s for s in guidance_sections if s.get('elements') or s.get('penalties')])
            }
        }

# Global instance
legal_data_loader = LegalDataLoader()