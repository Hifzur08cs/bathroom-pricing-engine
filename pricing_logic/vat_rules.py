# pricing_logic/vat_rules.py
"""
French VAT Rules for renovation work with compliance checking
"""

from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class PropertyType(Enum):
    RESIDENTIAL_PRIMARY = "residential_primary"
    RESIDENTIAL_SECONDARY = "residential_secondary"
    COMMERCIAL = "commercial"
    SOCIAL_HOUSING = "social_housing"

class WorkType(Enum):
    RENOVATION = "renovation"
    NEW_CONSTRUCTION = "new_construction"
    MAINTENANCE = "maintenance"
    IMPROVEMENT = "improvement"
    ENERGY_RENOVATION = "energy_renovation"

class VATCalculatorForQuotes:
    """
    French VAT calculator for renovation quotes with compliance checking
    """
    
    def __init__(self):
        # French VAT rates (as of 2025)
        self.vat_rates = {
            "standard": 0.20,           # 20% - Standard rate
            "renovation": 0.10,         # 10% - Renovation rate (building >2 years)
            "energy_efficiency": 0.055, # 5.5% - Energy efficiency improvements
            "social_housing": 0.055,    # 5.5% - Social housing improvements
        }
        
        # Energy efficiency eligible materials
        self.energy_materials = [
            "insulation_materials",
            "heat_pump", 
            "solar_panels",
            "energy_efficient_windows",
            "programmable_thermostat",
            "heat_recovery_ventilation",
            "energy_efficient_boiler"
        ]
    
    def calculate_simple_renovation_vat(self, materials_cost: float, labor_cost: float,
                                      building_age_years: int = 5,
                                      is_energy_renovation: bool = False) -> Dict:
        """
        Simple VAT calculation for bathroom renovation quotes
        
        Args:
            materials_cost: Cost of materials
            labor_cost: Cost of labor
            building_age_years: Age of building in years
            is_energy_renovation: Whether this includes energy efficiency improvements
        """
        
        subtotal = materials_cost + labor_cost
        
        # Determine VAT rate based on renovation type
        if is_energy_renovation and building_age_years >= 2:
            vat_rate = self.vat_rates["energy_efficiency"]  # 5.5%
            rate_description = "Energy efficiency renovation (5.5%)"
        elif building_age_years >= 2:
            vat_rate = self.vat_rates["renovation"]  # 10%
            rate_description = "Renovation work on building >2 years (10%)"
        else:
            vat_rate = self.vat_rates["standard"]  # 20%
            rate_description = "New construction rate (20%)"
        
        vat_amount = subtotal * vat_rate
        total_including_vat = subtotal + vat_amount
        
        return {
            "materials_cost": materials_cost,
            "labor_cost": labor_cost,
            "subtotal": subtotal,
            "vat_rate": vat_rate,
            "vat_amount": round(vat_amount, 2),
            "total_including_vat": round(total_including_vat, 2),
            "rate_description": rate_description,
            "building_age_years": building_age_years,
            "is_energy_renovation": is_energy_renovation
        }
    
    def calculate_detailed_vat(self, items: List[Dict], work_context: Dict) -> Dict:
        """
        Detailed VAT calculation for multiple items with different rates
        
        Args:
            items: List of items with 'amount', 'category', 'type' fields
            work_context: Context including property_type, work_type, building_age, etc.
        """
        
        total_materials = 0
        total_labor = 0
        
        # Separate materials and labor
        for item in items:
            if item.get("type") == "materials":
                total_materials += item["amount"]
            elif item.get("type") == "labor":
                total_labor += item["amount"]
        
        # Determine applicable VAT rate
        vat_info = self._determine_vat_rate(work_context)
        
        # Calculate VAT
        subtotal = total_materials + total_labor
        vat_amount = subtotal * vat_info["rate"]
        total_with_vat = subtotal + vat_amount
        
        return {
            "materials_total": round(total_materials, 2),
            "labor_total": round(total_labor, 2),
            "subtotal": round(subtotal, 2),
            "vat_rate": vat_info["rate"],
            "vat_description": vat_info["description"],
            "vat_amount": round(vat_amount, 2),
            "total_including_vat": round(total_with_vat, 2),
            "compliance_requirements": vat_info["requirements"]
        }
    
    def _determine_vat_rate(self, context: Dict) -> Dict:
        """Determine appropriate VAT rate based on context"""
        
        work_type = context.get("work_type", WorkType.RENOVATION)
        property_type = context.get("property_type", PropertyType.RESIDENTIAL_PRIMARY)
        building_age = context.get("building_age_years", 5)
        has_energy_features = context.get("has_energy_features", False)
        
        # Social housing gets special rate
        if property_type == PropertyType.SOCIAL_HOUSING:
            return {
                "rate": self.vat_rates["social_housing"],
                "description": "Social housing improvements (5.5%)",
                "requirements": ["Social housing certification", "Qualified contractor"]
            }
        
        # Energy efficiency improvements
        if (work_type == WorkType.ENERGY_RENOVATION or has_energy_features) and building_age >= 2:
            return {
                "rate": self.vat_rates["energy_efficiency"],
                "description": "Energy efficiency improvements (5.5%)",
                "requirements": [
                    "Building age certificate (>2 years)",
                    "Energy efficiency certifications for materials",
                    "RGE certified contractor required",
                    "Customer declaration of building use"
                ]
            }
        
        # Standard renovation rate
        if building_age >= 2 and property_type in [PropertyType.RESIDENTIAL_PRIMARY, PropertyType.RESIDENTIAL_SECONDARY]:
            return {
                "rate": self.vat_rates["renovation"],
                "description": "Renovation work on building >2 years (10%)",
                "requirements": [
                    "Building age certificate (>2 years)",
                    "VAT-registered contractor required",
                    "Detailed materials/labor breakdown",
                    "Customer declaration of building use"
                ]
            }
        
        # Commercial or new construction - standard rate
        return {
            "rate": self.vat_rates["standard"],
            "description": "Standard VAT rate (20%)",
            "requirements": ["Standard VAT invoice required"]
        }
    
    def get_vat_optimization_suggestions(self, context: Dict) -> List[Dict]:
        """Suggest ways to optimize VAT rates"""
        
        suggestions = []
        building_age = context.get("building_age_years", 0)
        current_work_type = context.get("work_type", WorkType.RENOVATION)
        
        # Suggest energy efficiency upgrades
        if (current_work_type == WorkType.RENOVATION and 
            building_age >= 2 and 
            not context.get("has_energy_features", False)):
            
            current_rate = self.vat_rates["renovation"]  # 10%
            energy_rate = self.vat_rates["energy_efficiency"]  # 5.5%
            potential_savings_rate = current_rate - energy_rate
            
            suggestions.append({
                "type": "energy_efficiency_upgrade",
                "description": "Add energy efficiency improvements to qualify for 5.5% VAT rate",
                "potential_savings_rate": potential_savings_rate,
                "requirements": "Add insulation, efficient heating, or renewable energy components",
                "certification_needed": "RGE certified contractor required"
            })
        
        # Suggest delaying work if building too new
        if building_age < 2:
            suggestions.append({
                "type": "timing_optimization", 
                "description": "Wait until building is 2+ years old for reduced VAT rates",
                "potential_savings_rate": 0.10,  # From 20% to 10%
                "requirements": "Delay work until building age requirement is met"
            })
        
        return suggestions
    
    def validate_vat_compliance(self, quote_data: Dict) -> Dict:
        """Validate VAT compliance requirements for a quote"""
        
        compliance_issues = []
        documentation_required = []
        
        vat_rate = quote_data.get("vat_rate", 0.20)
        building_age = quote_data.get("building_age_years", 0)
        
        # Check for reduced rate requirements
        if vat_rate == 0.10:  # Renovation rate
            documentation_required.extend([
                "Building age certificate or construction permit showing building >2 years old",
                "Contractor VAT registration certificate", 
                "Detailed invoice separating materials and labor",
                "Customer declaration of residential use"
            ])
            
        elif vat_rate == 0.055:  # Energy efficiency rate
            documentation_required.extend([
                "Building age certificate showing building >2 years old",
                "Energy efficiency certifications for all materials",
                "RGE (Reconnu Garant de l'Environnement) contractor certification",
                "Energy performance improvement documentation",
                "Customer declaration of residential use and building age"
            ])
        
        # Validate contractor requirements
        if vat_rate < 0.20:  # Any reduced rate
            documentation_required.append("Contractor must be VAT registered in France")
        
        # Check building age consistency
        if vat_rate < 0.20 and building_age < 2:
            compliance_issues.append("Building age is <2 years but reduced VAT rate applied")
        
        return {
            "compliant": len(compliance_issues) == 0,
            "compliance_issues": compliance_issues,
            "documentation_required": documentation_required,
            "vat_rate_applied": vat_rate,
            "validation_date": datetime.now().isoformat()
        }
    
    def calculate_vat_savings_scenarios(self, base_amount: float, building_age: int) -> Dict:
        """Calculate potential VAT savings under different scenarios"""
        
        scenarios = {}
        
        # Standard rate (20%)
        standard_vat = base_amount * self.vat_rates["standard"]
        scenarios["standard"] = {
            "rate": self.vat_rates["standard"],
            "vat_amount": round(standard_vat, 2),
            "total": round(base_amount + standard_vat, 2),
            "description": "Standard rate (new construction/commercial)"
        }
        
        # Renovation rate (10%) - if building is old enough
        if building_age >= 2:
            renovation_vat = base_amount * self.vat_rates["renovation"]
            scenarios["renovation"] = {
                "rate": self.vat_rates["renovation"],
                "vat_amount": round(renovation_vat, 2),
                "total": round(base_amount + renovation_vat, 2),
                "description": "Renovation rate (building >2 years)",
                "savings_vs_standard": round(standard_vat - renovation_vat, 2)
            }
            
            # Energy efficiency rate (5.5%) - if building is old enough
            energy_vat = base_amount * self.vat_rates["energy_efficiency"]
            scenarios["energy_efficiency"] = {
                "rate": self.vat_rates["energy_efficiency"],
                "vat_amount": round(energy_vat, 2),
                "total": round(base_amount + energy_vat, 2),
                "description": "Energy efficiency rate (with certified improvements)",
                "savings_vs_standard": round(standard_vat - energy_vat, 2),
                "savings_vs_renovation": round(renovation_vat - energy_vat, 2)
            }
        
        return scenarios

def main():
    """Demo the VAT calculator"""
    
    print("🧾 French VAT Calculator Demo")
    print("=" * 40)
    
    calc = VATCalculatorForQuotes()
    
    # Test standard renovation
    print("\n💰 Standard Renovation (5-year-old building)")
    print("-" * 45)
    
    standard_vat = calc.calculate_simple_renovation_vat(
        materials_cost=1500.0,
        labor_cost=1200.0,
        building_age_years=5,
        is_energy_renovation=False
    )
    
    print(f"Materials: €{standard_vat['materials_cost']:,.2f}")
    print(f"Labor: €{standard_vat['labor_cost']:,.2f}")
    print(f"Subtotal: €{standard_vat['subtotal']:,.2f}")
    print(f"VAT ({standard_vat['vat_rate']:.1%}): €{standard_vat['vat_amount']:,.2f}")
    print(f"Total: €{standard_vat['total_including_vat']:,.2f}")
    print(f"Rate: {standard_vat['rate_description']}")
    
    # Test energy efficiency renovation
    print("\n🌱 Energy Efficiency Renovation")
    print("-" * 35)
    
    energy_vat = calc.calculate_simple_renovation_vat(
        materials_cost=1500.0,
        labor_cost=1200.0,
        building_age_years=5,
        is_energy_renovation=True
    )
    
    print(f"Materials: €{energy_vat['materials_cost']:,.2f}")
    print(f"Labor: €{energy_vat['labor_cost']:,.2f}")
    print(f"Subtotal: €{energy_vat['subtotal']:,.2f}")
    print(f"VAT ({energy_vat['vat_rate']:.1%}): €{energy_vat['vat_amount']:,.2f}")
    print(f"Total: €{energy_vat['total_including_vat']:,.2f}")
    print(f"Rate: {energy_vat['rate_description']}")
    
    # Calculate savings
    savings = standard_vat['vat_amount'] - energy_vat['vat_amount']
    print(f"\n💡 Energy Efficiency Savings: €{savings:,.2f}")
    
    # Test VAT scenarios
    print(f"\n📊 VAT Scenarios Comparison (€2,700 project)")
    print("-" * 50)
    
    scenarios = calc.calculate_vat_savings_scenarios(2700.0, 5)
    
    for scenario_name, data in scenarios.items():
        print(f"{scenario_name.replace('_', ' ').title()}:")
        print(f"  Rate: {data['rate']:.1%}")
        print(f"  VAT: €{data['vat_amount']:,.2f}")
        print(f"  Total: €{data['total']:,.2f}")
        if 'savings_vs_standard' in data:
            print(f"  Savings: €{data['savings_vs_standard']:,.2f}")
        print()
    
    # Test compliance validation
    print(f"Compliance Check")
    print("-" * 20)
    
    compliance = calc.validate_vat_compliance({
        "vat_rate": 0.10,
        "building_age_years": 5
    })
    
    print(f"Compliant: {'Yes' if compliance['compliant'] else 'No'}")
    print(f"Documentation required:")
    for doc in compliance['documentation_required'][:3]:  # Show first 3
        print(f"  - {doc}")
    if len(compliance['documentation_required']) > 3:
        print(f"  ... and {len(compliance['documentation_required']) - 3} more")

if __name__ == "__main__":
    main()