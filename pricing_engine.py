# pricing_engine.py

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Import our modular components
from pricing_logic.material_db import MaterialDatabase
from pricing_logic.labor_calc import LaborCalculator, SkillLevel
from pricing_logic.vat_rules import VATCalculatorForQuotes
from pricing_logic.transcript_parser import SmartTranscriptParser
from dotenv import load_dotenv
load_dotenv()  # This loads .env file
@dataclass
class Quote:
    project_id: str
    zone: str
    city: str
    total_area_sqm: float
    tasks: List[Dict]
    subtotal_materials: float
    subtotal_labor: float
    vat_amount: float
    total_price: float
    margin_percentage: float
    confidence_score: float
    parsing_method: str
    created_at: str

class PricingEngine:
    """
    Main pricing engine that orchestrates all components
    Clean implementation with proper separation of concerns
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        # Initialize all components
        self.material_db = MaterialDatabase()
        self.labor_calc = LaborCalculator()
        self.vat_calculator = VATCalculatorForQuotes()
        self.transcript_parser = SmartTranscriptParser(openai_api_key)
        
        # Task definitions mapping transcript tasks to our pricing logic
        self.task_definitions = {
            "demolition": {
                "skill_level": SkillLevel.BASIC,
                "hours_per_sqm": 1.5,
                "materials": {
                    "demolition_materials": 1.0
                }
            },
            "tiling": {
                "skill_level": SkillLevel.SKILLED,
                "hours_per_sqm": 2.8,
                "materials": {
                    "ceramic_floor_basic": 1.1,  # 10% waste
                    "tile_adhesive": 1.5,
                    "waterproof_membrane": 1.0
                }
            },
            "plumbing": {
                "skill_level": SkillLevel.SPECIALIST,
                "hours_per_sqm": 2.5,
                "materials": {
                    "shower_mixer_basic": 0.25,  # 1 per 4m²
                    "toilet_standard": 0.25,
                    "pipes_pvc": 3.0
                }
            },
            "installation": {
                "skill_level": SkillLevel.SKILLED,
                "hours_per_sqm": 1.8,
                "materials": {
                    "vanity_unit_60cm": 0.25
                }
            },
            "painting": {
                "skill_level": SkillLevel.BASIC,
                "hours_per_sqm": 1.0,
                "materials": {
                    "bathroom_paint_basic": 0.2,
                    "primer": 0.15
                }
            },
            "electrical": {
                "skill_level": SkillLevel.SPECIALIST,
                "hours_per_sqm": 2.0,
                "materials": {
                    "electrical_supplies": 0.5
                }
            }
        }
    
    def generate_quote(self, transcript: str) -> Quote:
       
        
        try:
            # Step 1: Parse transcript using OpenAI or patterns
            parsed_data = self.transcript_parser.parse_transcript(transcript)
            
            # Step 2: Generate detailed tasks with materials and labor
            tasks = self._generate_detailed_tasks(parsed_data)
            
            # Step 3: Calculate final costs with VAT
            quote = self._calculate_final_quote(parsed_data, tasks)
            
            # Step 4: Save quote to output
            self._save_quote(quote)
            
            return quote
            
        except Exception as e:
            print(f"❌ Quote generation failed: {e}")
            # Return a basic fallback quote
            return self._generate_fallback_quote(transcript, str(e))
    
    def _generate_detailed_tasks(self, parsed_data: Dict) -> List[Dict]:
        """Generate detailed tasks with materials and labor calculations"""
        
        detailed_tasks = []
        area = parsed_data.get("area_sqm", 4.0)
        city = parsed_data.get("city", "marseille")
        
        for task in parsed_data.get("tasks", []):
            task_type = task.get("type")
            
            if task_type not in self.task_definitions:
                continue
            
            task_def = self.task_definitions[task_type]
            
            # Calculate materials needed
            materials = []
            total_materials_cost = 0.0
            
            for material_id, qty_per_sqm in task_def["materials"].items():
                quantity = area * qty_per_sqm
                
                # Get material cost from our material database
                cost_info = self.material_db.get_cost_with_margin(
                    material_id, quantity, city
                )
                
                if not cost_info.get("error"):
                    materials.append({
                        "name": cost_info["name"],
                        "quantity": cost_info["quantity"],
                        "unit": cost_info["unit"],
                        "unit_cost": cost_info["unit_cost"],
                        "total_cost": cost_info["total_cost"]
                    })
                    total_materials_cost += cost_info["total_cost"]
            
            # Calculate labor using our labor calculator
            labor_result = self.labor_calc.calculate_task_labor(
                task_type=task_type.replace("_", ""),  # Remove underscores for task mapping
                area_or_units=area,
                region=city,
                complexity_factors=task.get("complexity_factors", [])
            )
            
            if not labor_result.get("error"):
                detailed_tasks.append({
                    "task_type": task_type,
                    "description": task.get("description", f"{task_type.title()} work"),
                    "area_sqm": area,
                    "labor_hours": labor_result["billable_hours"],
                    "labor_cost": labor_result["base_labor_cost"],
                    "materials": materials,
                    "materials_cost": round(total_materials_cost, 2),
                    "skill_required": labor_result["skill_required"],
                    "complexity_factors": task.get("complexity_factors", [])
                })
        
        return detailed_tasks
    
    def _calculate_final_quote(self, parsed_data: Dict, tasks: List[Dict]) -> Quote:
        """Calculate final quote with margins and VAT"""
        
        # Calculate subtotals
        subtotal_materials = sum(task["materials_cost"] for task in tasks)
        subtotal_labor = sum(task["labor_cost"] for task in tasks)
        
        # Apply margin based on budget consciousness
        budget_conscious = parsed_data.get("budget_conscious", False)
        margin_percentage = 0.15 if budget_conscious else 0.25
        
        subtotal_with_margin = (subtotal_materials + subtotal_labor) * (1 + margin_percentage)
        
        # Calculate VAT using our VAT calculator
        building_age = 5  # Assume 5 years for renovation rate
        is_energy = any("energy" in str(task).lower() for task in tasks)
        
        vat_calculation = self.vat_calculator.calculate_simple_renovation_vat(
            materials_cost=subtotal_materials * (1 + margin_percentage),
            labor_cost=subtotal_labor * (1 + margin_percentage),
            building_age_years=building_age,
            is_energy_renovation=is_energy
        )
        
        return Quote(
            project_id=f"BTH_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            zone="bathroom",
            city=parsed_data.get("city", "marseille"),
            total_area_sqm=parsed_data.get("area_sqm", 4.0),
            tasks=tasks,
            subtotal_materials=round(subtotal_materials, 2),
            subtotal_labor=round(subtotal_labor, 2),
            vat_amount=vat_calculation["vat_amount"],
            total_price=vat_calculation["total_including_vat"],
            margin_percentage=margin_percentage,
            confidence_score=parsed_data.get("confidence_score", 0.5),
            parsing_method=parsed_data.get("parsing_method", "unknown"),
            created_at=datetime.now().isoformat()
        )
    
    def _generate_fallback_quote(self, transcript: str, error: str) -> Quote:
        """Generate a basic fallback quote when main processing fails"""
        
        return Quote(
            project_id=f"BTH_FALLBACK_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            zone="bathroom",
            city="marseille",
            total_area_sqm=4.0,
            tasks=[{
                "task_type": "general_renovation",
                "description": "General bathroom renovation (fallback estimate)",
                "area_sqm": 4.0,
                "labor_hours": 20.0,
                "labor_cost": 800.0,
                "materials": [{"name": "Mixed materials", "total_cost": 1200.0}],
                "materials_cost": 1200.0,
                "skill_required": "skilled",
                "error": error
            }],
            subtotal_materials=1200.0,
            subtotal_labor=800.0,
            vat_amount=200.0,
            total_price=2200.0,
            margin_percentage=0.20,
            confidence_score=0.1,
            parsing_method="fallback",
            created_at=datetime.now().isoformat()
        )
    
    def _save_quote(self, quote: Quote):
        """Save quote to output directory"""
        
        try:
            # Ensure output directory exists
            os.makedirs("output", exist_ok=True)
            
            # Save individual quote
            filename = f"output/{quote.project_id}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(asdict(quote), f, indent=2, ensure_ascii=False)
            
            print(f"Quote saved: {filename}")
            
        except Exception as e:
            print(f"Could not save quote: {e}")

def main():
    """Demo the complete pricing engine"""
    
    print("Smart Bathroom Renovation Pricing Engine")
    print("=" * 60)
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("OpenAI API key detected - AI parsing enabled")
    else:
        print("No OpenAI API key detected")
    
    # Initialize engine
    engine = PricingEngine(openai_api_key=api_key)
    
    # Test transcripts
    test_transcripts = [
        {
            "name": "Standard Renovation",
            "transcript": """
            Client wants to renovate a small 4m² bathroom in Marseille. 
            They need to remove old tiles, redo plumbing for the shower, 
            replace toilet, install vanity, repaint walls, and lay new ceramic tiles. 
            Budget-conscious project.
            """
        },
        {
            "name": "Complex Paris Project", 
            "transcript": """
            Luxury bathroom renovation in Paris, 5.5m² space. Premium fixtures, 
            waterproofing needed, small mosaic tiles, custom vanity installation, 
            new electrical for lighting. No budget constraints.
            """
        }
    ]
    
    for i, test in enumerate(test_transcripts, 1):
        print(f"\nTest {i}: {test['name']}")
        print("-" * 50)
        
        quote = engine.generate_quote(test['transcript'])
        
        print(f"Project: {quote.project_id}")
        print(f"Location: {quote.city.title()}")
        print(f"Area: {quote.total_area_sqm}m²")
        print(f"Tasks: {len(quote.tasks)} tasks detected")
        print(f"Method: {quote.parsing_method}")
        print(f"Confidence: {quote.confidence_score:.1%}")
        print(f"Total: €{quote.total_price:,.2f}")
        print(f"VAT: €{quote.vat_amount:,.2f}")
        print(f"Margin: {quote.margin_percentage:.0%}")
        
        task_types = [task["task_type"] for task in quote.tasks]
        print(f"Task breakdown: {', '.join(task_types)}")
    
    print(f"\nQuotation generated successfully! Check the 'output/' folder for saved quotes.")

if __name__ == "__main__":
    main()