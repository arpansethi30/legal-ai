from typing import Dict, Any
import json
import os
import google.generativeai as genai


class ContractGenerator:
    """Generate legal documents based on templates and parameters"""

    def __init__(self, gemini_model):
        self.gemini_model = gemini_model
        self.templates_dir = "contract_templates"
        os.makedirs(self.templates_dir, exist_ok=True)
        self.load_templates()

    def load_templates(self):
        """Load available contract templates"""
        self.templates = {
            "nda": {
                "name": "Non-Disclosure Agreement",
                "description": "An agreement to protect confidential information shared between parties",
                "parameters": {
                    "party1_name": "First party's full legal name",
                    "party1_address": "First party's legal address",
                    "party2_name": "Second party's full legal name", 
                    "party2_address": "Second party's legal address",
                    "effective_date": "When the agreement becomes effective",
                    "confidential_info_description": "Description of the confidential information covered",
                    "purpose": "Purpose of sharing the confidential information",
                    "term_years": "Duration of the agreement in years",
                    "governing_law": "State/jurisdiction whose laws govern the agreement",
                    "include_non_solicitation": "Whether to include a non-solicitation clause (true/false)"
                }
            },
            "consulting": {
                "name": "Consulting Agreement",
                "description": "An agreement for professional consulting services",
                "parameters": {
                    "client_name": "Client's full legal name",
                    "client_address": "Client's legal address",
                    "consultant_name": "Consultant's full legal name",
                    "consultant_address": "Consultant's legal address",
                    "effective_date": "When the agreement becomes effective",
                    "services_description": "Detailed description of consulting services",
                    "compensation": "Payment terms (hourly rate, fixed fee, etc.)",
                    "term_months": "Duration of the agreement in months",
                    "termination_notice_days": "Days of notice required for termination",
                    "include_confidentiality": "Whether to include confidentiality provisions (true/false)",
                    "consultant_is_independent_contractor": "Whether the consultant is an independent contractor (true/false)"
                }
            },
            "employment": {
                "name": "Employment Agreement",
                "description": "An agreement between employer and employee",
                "parameters": {
                    "employer_name": "Employer's full legal name",
                    "employer_address": "Employer's legal address",
                    "employee_name": "Employee's full legal name",
                    "employee_address": "Employee's home address",
                    "start_date": "Employment start date",
                    "position_title": "Employee's job title",
                    "duties_description": "Description of job duties and responsibilities",
                    "salary": "Annual salary amount",
                    "payment_frequency": "How often payment is made (weekly, bi-weekly, monthly)",
                    "benefits_description": "Description of benefits provided",
                    "paid_time_off_days": "Number of paid time off days per year",
                    "term_type": "At-will or fixed term employment",
                    "term_length": "If fixed term, the length in months",
                    "include_non_compete": "Whether to include a non-compete clause (true/false)",
                    "include_confidentiality": "Whether to include confidentiality provisions (true/false)"
                }
            },
            "software_license": {
                "name": "Software License Agreement",
                "description": "An agreement granting rights to use software",
                "parameters": {
                    "licensor_name": "Licensor's full legal name",
                    "licensor_address": "Licensor's legal address",
                    "licensee_name": "Licensee's full legal name",
                    "licensee_address": "Licensee's legal address",
                    "effective_date": "When the agreement becomes effective",
                    "software_name": "Name of the software being licensed",
                    "software_description": "Description of the software and its purpose",
                    "license_type": "Type of license (perpetual, subscription, etc.)",
                    "license_fee": "Cost of the license",
                    "payment_terms": "When and how payment is to be made",
                    "permitted_users": "Who is allowed to use the software",
                    "includes_source_code": "Whether source code is included (true/false)",
                    "includes_maintenance": "Whether maintenance and support are included (true/false)",
                    "warranty_period_months": "Length of warranty period in months"
                }
            }
        }

    def get_available_templates(self) -> Dict[str, Any]:
        """Get available contract templates with metadata"""
        templates_info = {}
        for id, template in self.templates.items():
            templates_info[id] = {
                "name": template["name"],
                "description": template["description"],
                "parameters": template["parameters"]
            }
        return templates_info

    async def generate_contract(
        self, template_id: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a contract based on template and parameters
        Returns the generated contract text
        """
        if template_id not in self.templates:
            return {
                "success": False,
                "error": f"Template '{template_id}' not found"
            }
            
        template = self.templates[template_id]
        
        # Check that all required parameters are provided
        missing_params = []
        for param_name in template["parameters"]:
            if param_name not in parameters:
                missing_params.append(param_name)
                
        if missing_params:
            return {
                "success": False,
                "error": f"Missing required parameters: {', '.join(missing_params)}"
            }
            
        # Prepare prompt for Gemini
        prompt = f"""
        Generate a professional {template["name"]} with the following details:
        
        {json.dumps(parameters, indent=2)}
        
        The document should:
        1. Follow standard legal formatting
        2. Include all necessary sections typical for this type of agreement
        3. Use the provided parameters throughout the document
        4. Be legally sound and use appropriate legal terminology
        5. Be comprehensive but concise
        
        Please generate the complete document with proper section headers and structure.
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            contract_text = response.text
            
            return {
                "success": True,
                "template_id": template_id,
                "template_name": template["name"],
                "contract_text": contract_text,
                "parameters": parameters,
                "model": "gemini-1.5-pro"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "template_id": template_id
            } 