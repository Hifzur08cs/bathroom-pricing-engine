# pricing_logic/material_db.py
"""
Material Database with Regional Pricing
Clean implementation without duplication
"""

import json
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict

@dataclass
class Material:
    """Material data structure with pricing and metadata"""
    name: str
    category: str
    unit: str
    base_cost: float
    supplier_margin: float
    quality_grade: str  # basic, standard, premium
    availability_score: float  # 0-1, based on regional availability
    last_updated: str
    supplier_id: Optional[str] = None

class MaterialDatabase:
    """
    Material database with regional pricing and supplier integration
    """
    
    def __init__(self, data_file: Optional[str] = None):
        self.materials = {}
        self.regional_multipliers = {}
        
        if data_file:
            self.load_from_file(data_file)
        else:
            self._initialize_default_materials()
            self._setup_regional_pricing()
    
    def _initialize_default_materials(self):
        """Initialize with default French building materials"""
        
        # Create materials with consistent naming for pricing engine
        default_materials = {
            # Tiles and Flooring
            "ceramic_floor_basic": Material(
                name="Ceramic Floor Tiles - Basic",
                category="flooring",
                unit="m²",
                base_cost=22.0,
                supplier_margin=0.15,
                quality_grade="basic",
                availability_score=0.95,
                last_updated=datetime.now().isoformat()
            ),
            "ceramic_floor_standard": Material(
                name="Ceramic Floor Tiles - Standard",
                category="flooring", 
                unit="m²",
                base_cost=35.0,
                supplier_margin=0.18,
                quality_grade="standard",
                availability_score=0.90,
                last_updated=datetime.now().isoformat()
            ),
            "wall_tiles_standard": Material(
                name="Wall Tiles - Standard",
                category="tiling",
                unit="m²", 
                base_cost=28.0,
                supplier_margin=0.15,
                quality_grade="standard",
                availability_score=0.90,
                last_updated=datetime.now().isoformat()
            ),
            
            # Installation materials
            "tile_adhesive": Material(
                name="Flexible Tile Adhesive",
                category="consumables",
                unit="kg",
                base_cost=2.8,
                supplier_margin=0.10,
                quality_grade="standard",
                availability_score=0.95,
                last_updated=datetime.now().isoformat()
            ),
            "waterproof_membrane": Material(
                name="Waterproof Membrane",
                category="consumables", 
                unit="m²",
                base_cost=12.0,
                supplier_margin=0.15,
                quality_grade="standard",
                availability_score=0.90,
                last_updated=datetime.now().isoformat()
            ),
            
            # Plumbing Components
            "shower_mixer_basic": Material(
                name="Shower Mixer - Basic Chrome",
                category="plumbing",
                unit="unit",
                base_cost=85.0,
                supplier_margin=0.25,
                quality_grade="basic",
                availability_score=0.95,
                last_updated=datetime.now().isoformat()
            ),
            "shower_mixer_premium": Material(
                name="Shower Mixer - Premium Thermostatic",
                category="plumbing",
                unit="unit",
                base_cost=220.0,
                supplier_margin=0.30,
                quality_grade="premium",
                availability_score=0.75,
                last_updated=datetime.now().isoformat()
            ),
            "toilet_standard": Material(
                name="Wall-hung Toilet - Standard",
                category="plumbing",
                unit="unit",
                base_cost=280.0,
                supplier_margin=0.20,
                quality_grade="standard", 
                availability_score=0.85,
                last_updated=datetime.now().isoformat()
            ),
            "vanity_unit_60cm": Material(
                name="Vanity Unit 60cm with Basin",
                category="installation",
                unit="unit",
                base_cost=320.0,
                supplier_margin=0.25,
                quality_grade="standard",
                availability_score=0.80,
                last_updated=datetime.now().isoformat()
            ),
            "pipes_pvc": Material(
                name="PVC Pipes and Fittings",
                category="plumbing",
                unit="m",
                base_cost=8.5,
                supplier_margin=0.15,
                quality_grade="standard",
                availability_score=0.95,
                last_updated=datetime.now().isoformat()
            ),
            
            # Paint and Finishing
            "bathroom_paint_basic": Material(
                name="Bathroom Paint - Anti-mold Basic",
                category="painting",
                unit="liter",
                base_cost=15.0,
                supplier_margin=0.12,
                quality_grade="basic",
                availability_score=0.95,
                last_updated=datetime.now().isoformat()
            ),
            "primer": Material(
                name="Wall Primer - Bathroom",
                category="painting",
                unit="liter", 
                base_cost=12.0,
                supplier_margin=0.12,
                quality_grade="standard",
                availability_score=0.95,
                last_updated=datetime.now().isoformat()
            ),
            
            # Consumables and tools
            "demolition_materials": Material(
                name="Demolition Supplies",
                category="consumables",
                unit="m²",
                base_cost=5.0,
                supplier_margin=0.10,
                quality_grade="basic",
                availability_score=0.95,
                last_updated=datetime.now().isoformat()
            ),
            "electrical_supplies": Material(
                name="Electrical Supplies - Bathroom",
                category="electrical",
                unit="unit",
                base_cost=45.0,
                supplier_margin=0.20,
                quality_grade="standard",
                availability_score=0.90,
                last_updated=datetime.now().isoformat()
            )
        }
        
        self.materials = default_materials
    
    def _setup_regional_pricing(self):
        """Setup regional pricing multipliers for major French cities"""
        
        self.regional_multipliers = {
            "paris": 1.35,
            "lyon": 1.15,
            "marseille": 1.0,  # Base rate
            "toulouse": 1.08,
            "nice": 1.25,
            "nantes": 1.05,
            "strasbourg": 1.18,
            "bordeaux": 1.12,
            "lille": 1.10,
            "montpellier": 1.03,
            "rennes": 1.06,
            "reims": 1.02
        }
    
    def get_material(self, material_id: str, region: str = "marseille") -> Optional[Material]:
        """
        Get material with regional pricing applied
        
        Args:
            material_id: Material identifier
            region: City/region for pricing
        """
        
        if material_id not in self.materials:
            return None
        
        base_material = self.materials[material_id]
        regional_multiplier = self.regional_multipliers.get(region.lower(), 1.0)
        
        # Create material with regional pricing applied
        regional_material = Material(
            name=base_material.name,
            category=base_material.category,
            unit=base_material.unit,
            base_cost=base_material.base_cost * regional_multiplier,
            supplier_margin=base_material.supplier_margin,
            quality_grade=base_material.quality_grade,
            availability_score=base_material.availability_score,
            last_updated=base_material.last_updated,
            supplier_id=base_material.supplier_id
        )
        
        return regional_material
    
    def get_cost_with_margin(self, material_id: str, quantity: float, 
                           region: str = "marseille") -> Dict:
        """Calculate total cost including supplier margins"""
        
        material = self.get_material(material_id, region)
        if not material:
            return {"error": f"Material {material_id} not found"}
        
        base_cost = material.base_cost * quantity
        margin_amount = base_cost * material.supplier_margin
        total_cost = base_cost + margin_amount
        
        return {
            "material_id": material_id,
            "name": material.name,
            "quantity": quantity,
            "unit": material.unit,
            "unit_cost": material.base_cost,
            "base_cost": round(base_cost, 2),
            "margin": round(margin_amount, 2),
            "total_cost": round(total_cost, 2),
            "availability_score": material.availability_score,
            "quality_grade": material.quality_grade
        }
    
    def get_materials_by_category(self, category: str, region: str = "marseille") -> List[Material]:
        """Get all materials in a specific category with regional pricing"""
        
        materials = []
        for material_id, material in self.materials.items():
            if material.category == category:
                regional_material = self.get_material(material_id, region)
                if regional_material:
                    materials.append(regional_material)
        
        return materials
    
    def update_material_price(self, material_id: str, new_price: float, 
                            supplier_id: Optional[str] = None) -> bool:
        """Update material price (for supplier API integration)"""
        
        if material_id in self.materials:
            self.materials[material_id].base_cost = new_price
            self.materials[material_id].last_updated = datetime.now().isoformat()
            if supplier_id:
                self.materials[material_id].supplier_id = supplier_id
            return True
        return False
    
    def add_material(self, material_id: str, material: Material):
        """Add new material to database"""
        self.materials[material_id] = material
    
    def list_all_materials(self) -> List[str]:
        """Get list of all available material IDs"""
        return list(self.materials.keys())
    
    def get_regional_multiplier(self, region: str) -> float:
        """Get regional pricing multiplier for a city"""
        return self.regional_multipliers.get(region.lower(), 1.0)
    
    def export_to_json(self, filename: str = "data/materials.json"):
        """Export materials database to JSON file"""
        
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        export_data = {
            "materials": {mid: asdict(mat) for mid, mat in self.materials.items()},
            "regional_multipliers": self.regional_multipliers,
            "export_timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"Materials database exported to {filename}")
    
    def load_from_file(self, filename: str) -> bool:
        """Load materials database from JSON file"""
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load materials
            self.materials = {}
            for mid, mat_data in data.get("materials", {}).items():
                self.materials[mid] = Material(**mat_data)
            
            # Load regional multipliers
            self.regional_multipliers = data.get("regional_multipliers", {})
            
            print(f"Materials database loaded from {filename}")
            return True
            
        except Exception as e:
            print(f"Error loading material database: {e}")
            return False

def main():
    """Demo the material database"""
    
    print("Material Database")
    print("=" * 40)
    
    # Initialize database
    db = MaterialDatabase()
    
    # Test basic material lookup
    print("\nBasic Material Lookup:")
    material = db.get_material("ceramic_floor_basic", "marseille")
    if material:
        print(f"  {material.name}: €{material.base_cost:.2f}/{material.unit}")
        print(f"  Category: {material.category}, Grade: {material.quality_grade}")
    
    # Test regional pricing
    print(f"\nRegional Pricing Comparison:")
    cities = ["marseille", "paris", "lyon", "nice"]
    material_id = "ceramic_floor_basic"
    
    for city in cities:
        material = db.get_material(material_id, city)
        multiplier = db.get_regional_multiplier(city)
        print(f"  {city.title()}: €{material.base_cost:.2f}/{material.unit} ({multiplier}x)")
    
    # Test cost calculation with margin
    print(f"\nCost Calculation Example:")
    cost_info = db.get_cost_with_margin("shower_mixer_basic", 1, "paris")
    if not cost_info.get("error"):
        print(f"  Item: {cost_info['name']}")
        print(f"  Quantity: {cost_info['quantity']} {cost_info['unit']}")
        print(f"  Unit cost: €{cost_info['unit_cost']:.2f}")
        print(f"  Base cost: €{cost_info['base_cost']:.2f}")
        print(f"  Margin: €{cost_info['margin']:.2f}")
        print(f"  Total: €{cost_info['total_cost']:.2f}")
    
    # Test category listing
    print(f"\nAvailable Categories:")
    categories = set(mat.category for mat in db.materials.values())
    for category in sorted(categories):
        materials = db.get_materials_by_category(category)
        print(f"  {category.title()}: {len(materials)} items")
    
    # Export database
    print(f"\nExport Database:")
    db.export_to_json()
    
    print(f"\nAvailable Materials ({len(db.materials)} total):")
    for material_id in sorted(db.list_all_materials()):
        mat = db.materials[material_id]
        print(f"  {material_id}: {mat.name} (€{mat.base_cost:.2f}/{mat.unit})")

if __name__ == "__main__":
    main()