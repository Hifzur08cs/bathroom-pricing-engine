# pricing_logic/labor_calc.py
"""
Labor Calculator with skill-based rates and regional pricing
"""

from datetime import datetime
from typing import Dict, Optional
from enum import Enum

class SkillLevel(Enum):
    HELPER = "helper"           # €22/hour
    BASIC = "basic"             # €30/hour  
    SKILLED = "skilled"         # €42/hour
    SPECIALIST = "specialist"   # €65/hour

class LaborCalculator:
    """
    Calculate labor costs with skill levels and regional variations
    """
    
    def __init__(self):
        # Base hourly rates by skill level (Marseille baseline)
        self.base_rates = {
            SkillLevel.HELPER: 22.0,
            SkillLevel.BASIC: 30.0,
            SkillLevel.SKILLED: 42.0,
            SkillLevel.SPECIALIST: 65.0,
        }
        
        # Regional multipliers for labor rates
        self.regional_multipliers = {
            "paris": 1.45,
            "lyon": 1.20,
            "marseille": 1.0,  # baseline
            "toulouse": 1.12,
            "nice": 1.30,
            "nantes": 1.05,
            "strasbourg": 1.18,
            "bordeaux": 1.15,
            "lille": 1.10,
            "montpellier": 1.03,
            "rennes": 1.06,
            "reims": 1.02
        }
        
        # Task definitions with time estimates and skill requirements
        self.task_definitions = {
            "demolition": {
                "skill_level": SkillLevel.BASIC,
                "hours_per_sqm": 1.5,
                "minimum_hours": 3.0,
                "complexity_factors": {
                    "thick_walls": 1.3,
                    "tight_access": 1.2,
                    "electrical_obstacles": 1.2
                }
            },
            "tiling": {
                "skill_level": SkillLevel.SKILLED,
                "hours_per_sqm": 2.8,
                "minimum_hours": 6.0,
                "complexity_factors": {
                    "small_tiles": 1.4,
                    "pattern_work": 1.6,
                    "curved_surfaces": 1.5,
                    "waterproofing": 1.3
                }
            },
            "plumbing": {
                "skill_level": SkillLevel.SPECIALIST,
                "hours_per_sqm": 2.5,
                "minimum_hours": 4.0,
                "complexity_factors": {
                    "new_connections": 1.5,
                    "old_building": 1.4,
                    "waterproofing": 1.2
                }
            },
            "electrical": {
                "skill_level": SkillLevel.SPECIALIST,
                "hours_per_sqm": 2.0,
                "minimum_hours": 3.0,
                "complexity_factors": {
                    "new_circuit": 1.5,
                    "bathroom_safety": 1.3,
                    "concealed_wiring": 1.4
                }
            },
            "installation": {
                "skill_level": SkillLevel.SKILLED,
                "hours_per_sqm": 1.8,
                "minimum_hours": 2.0,
                "complexity_factors": {
                    "heavy_items": 1.3,
                    "custom_fitting": 1.4,
                    "wall_mounting": 1.1
                }
            },
            "painting": {
                "skill_level": SkillLevel.BASIC,
                "hours_per_sqm": 1.0,
                "minimum_hours": 4.0,
                "complexity_factors": {
                    "multiple_coats": 1.4,
                    "detail_work": 1.3,
                    "moisture_resistant": 1.1
                }
            }
        }
        
        # Seasonal adjustments
        self.seasonal_multipliers = {
            1: 0.95, 2: 0.95,  # Winter (low season)
            3: 1.0, 4: 1.15,   # Spring (high season starts)
            5: 1.25, 6: 1.25,  # Peak season
            7: 1.35, 8: 1.35,  # Holiday season
            9: 1.15, 10: 1.15, # Fall high season
            11: 0.95, 12: 0.95 # Winter
        }
    
    def calculate_task_labor(self, task_type: str, area_or_units: float, 
                           region: str, complexity_factors: Optional[list] = None,
                           target_date: Optional[datetime] = None, 
                           rush_job: bool = False) -> Dict:
        """
        Calculate labor cost for a specific task
        
        Args:
            task_type: Type of work (demolition, tiling, etc.)
            area_or_units: Area in m² or number of units
            region: City/region for pricing
            complexity_factors: List of complexity factors
            target_date: When work will be performed
            rush_job: Whether this is a rush job
        """
        
        if task_type not in self.task_definitions:
            return {"error": f"Unknown task type: {task_type}"}
        
        task_def = self.task_definitions[task_type]
        skill_level = task_def["skill_level"]
        
        # Calculate base hours
        base_hours = area_or_units * task_def["hours_per_sqm"]
        
        # Apply minimum hours
        billable_hours = max(base_hours, task_def["minimum_hours"])
        
        # Apply complexity factors
        complexity_multiplier = 1.0
        applied_factors = []
        
        if complexity_factors:
            for factor in complexity_factors:
                if factor in task_def["complexity_factors"]:
                    factor_multiplier = task_def["complexity_factors"][factor]
                    complexity_multiplier *= factor_multiplier
                    applied_factors.append({
                        "factor": factor,
                        "multiplier": factor_multiplier
                    })
        
        # Adjust hours for complexity
        final_hours = billable_hours * complexity_multiplier
        
        # Get base hourly rate
        base_hourly_rate = self.base_rates[skill_level]
        
        # Apply regional multiplier
        regional_multiplier = self.regional_multipliers.get(region.lower(), 1.0)
        regional_rate = base_hourly_rate * regional_multiplier
        
        # Apply seasonal adjustment
        seasonal_multiplier = 1.0
        if target_date:
            month = target_date.month
            seasonal_multiplier = self.seasonal_multipliers.get(month, 1.0)
        
        # Apply rush job premium
        rush_multiplier = 1.8 if rush_job else 1.0
        
        # Calculate final rate and cost
        final_hourly_rate = regional_rate * seasonal_multiplier * rush_multiplier
        base_labor_cost = final_hours * final_hourly_rate
        
        return {
            "task_type": task_type,
            "skill_required": skill_level.value,
            "base_hours": round(base_hours, 1),
            "billable_hours": round(billable_hours, 1),
            "final_hours": round(final_hours, 1),
            "base_hourly_rate": base_hourly_rate,
            "regional_multiplier": regional_multiplier,
            "complexity_multiplier": round(complexity_multiplier, 2),
            "seasonal_multiplier": round(seasonal_multiplier, 2),
            "rush_multiplier": rush_multiplier,
            "final_hourly_rate": round(final_hourly_rate, 2),
            "base_labor_cost": round(base_labor_cost, 2),
            "applied_complexity_factors": applied_factors,
            "area_or_units": area_or_units
        }
    
    def get_hourly_rate(self, skill_level: SkillLevel, region: str) -> float:
        """Get hourly rate for skill level and region"""
        base_rate = self.base_rates[skill_level]
        regional_multiplier = self.regional_multipliers.get(region.lower(), 1.0)
        return base_rate * regional_multiplier
    
    def estimate_project_duration(self, tasks: list) -> Dict:
        """Estimate total project duration from task list"""
        total_hours = sum(task.get("final_hours", 0) for task in tasks)
        
        # Assume 8-hour work days
        work_days = total_hours / 8.0
        
        # Add setup/coordination time (10% of work time)
        total_days = work_days * 1.1
        
        return {
            "total_labor_hours": round(total_hours, 1),
            "work_days": round(work_days, 1),
            "estimated_duration_days": round(total_days, 1)
        }

def main():
    """Demo the labor calculator"""
    
    print("👷 Labor Calculator Demo")
    print("=" * 40)
    
    calc = LaborCalculator()
    
    # Test different tasks
    test_cases = [
        {
            "name": "Basic Demolition",
            "task_type": "demolition",
            "area": 4.0,
            "region": "marseille",
            "complexity": []
        },
        {
            "name": "Complex Tiling (Paris)",
            "task_type": "tiling", 
            "area": 4.0,
            "region": "paris",
            "complexity": ["small_tiles", "waterproofing"]
        },
        {
            "name": "Specialist Plumbing",
            "task_type": "plumbing",
            "area": 4.0,
            "region": "lyon",
            "complexity": ["new_connections"]
        }
    ]
    
    for test in test_cases:
        print(f"\n🔧 {test['name']}")
        print("-" * 30)
        
        result = calc.calculate_task_labor(
            task_type=test["task_type"],
            area_or_units=test["area"],
            region=test["region"],
            complexity_factors=test["complexity"]
        )
        
        if "error" not in result:
            print(f"Skill Level: {result['skill_required']}")
            print(f"Base Rate: €{result['base_hourly_rate']:.2f}/hour")
            print(f"Final Rate: €{result['final_hourly_rate']:.2f}/hour")
            print(f"Hours: {result['final_hours']} hours")
            print(f"Total Cost: €{result['base_labor_cost']:.2f}")
            print(f"Regional Multiplier: {result['regional_multiplier']}x")
            if result['complexity_multiplier'] > 1.0:
                print(f"Complexity Multiplier: {result['complexity_multiplier']}x")
        else:
            print(f"Error: {result['error']}")
    
    # Test regional comparison
    print(f"\n🌍 Regional Rate Comparison (Skilled Tiling)")
    print("-" * 50)
    
    cities = ["marseille", "paris", "lyon", "nice"]
    for city in cities:
        rate = calc.get_hourly_rate(SkillLevel.SKILLED, city)
        multiplier = calc.regional_multipliers.get(city, 1.0)
        print(f"{city.title()}: €{rate:.2f}/hour ({multiplier}x)")

if __name__ == "__main__":
    main()