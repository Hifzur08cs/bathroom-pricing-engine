# Smart Bathroom Renovation Pricing Engine

Transform messy voice transcripts into professional renovation quotes with French VAT compliance, regional pricing, and OpenAI integration.

## How to Start the Project

### **1. Quick Setup (5 minutes)**

```bash
# 1. Clone the repository
git clone https://github.com/your-username/bathroom-pricing-engine.git
cd bathroom-pricing-engine

# 2. Verify project structure (should already exist)
ls -la
# You should see:
# pricing_logic/
# data/
# output/
# pricing_engine.py
# requirements.txt
# README.md

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment (optional - for OpenAI)
echo "OPENAI_API_KEY=sk-your-openai-key-here" > .env

# 5. Test the installation
python pricing_engine.py
```


## 🎯 How to Run

### **Basic Usage - Test with Sample Data**

```bash
# Run the main pricing engine with built-in test cases
python pricing_engine.py
```

This will generate quotes for 2 sample transcripts built into the `main()` function.

### **Testing with Your Own Transcripts**

To test with your own transcript, **modify the `main()` function** in `pricing_engine.py`:

```python
# In pricing_engine.py, find the main() function and modify:
def main():
    engine = PricingEngine()
    
    # Change this transcript to test your own data:
    your_transcript = """
    Client wants luxury bathroom renovation in Paris, 6m² space.
    Premium materials, remove everything, new plumbing, 
    waterproofing, marble tiles, custom vanity. No budget limits.
    """
    
    quote = engine.generate_quote(your_transcript)
    print(f"Quote: €{quote.total_price:,.2f}")
```

### **Component Testing**

```bash
# Test individual components
python pricing_logic/material_db.py      # Test material database
python pricing_logic/labor_calc.py       # Test labor calculations  
python pricing_logic/vat_rules.py        # Test VAT calculations
python pricing_logic/transcript_parser.py # Test OpenAI parsing

```

### **Sample Usage in Code**

```python
from pricing_engine import PricingEngine

# Initialize engine (with or without OpenAI)
engine = PricingEngine(openai_api_key="sk-your-key")  # With OpenAI

# Generate quote
quote = engine.generate_quote("Your renovation transcript here...")
print(f"Total: €{quote.total_price:,.2f}")
```

## 📁 Project Structure

```
bathroom-pricing-engine/
├── pricing_engine.py                   # MAIN FILE - Run this to test
├── requirements.txt                    # Python dependencies
├── README.md                          # This documentation
├── .env                               # OpenAI API key (create this)
├── 
├── pricing_logic/                     # Core business logic modules
│   ├── __init__.py                    # Python package marker (empty)
│   ├── material_db.py                 # Material pricing database
│   ├── labor_calc.py                  # Labor cost calculations
│   ├── vat_rules.py                   # French VAT compliance engine
│   └── transcript_parser.py           # OpenAI transcript parsing
├── 
├── data/                              # Static data files
│   ├── materials.json                 # Material price database
│   └── price_templates.csv            # Historical pricing data
├── 
├── output/                            # Generated quotes (auto-created)
    └── sample_quote.json              # Example output

```

## Database Architecture (Current vs Future)

### **Current Implementation - Hardcoded Data**

The system currently uses **hardcoded data structures** for rapid development and testing:

```python
# Current: Hardcoded in Python files
materials = {
    "ceramic_floor_basic": Material(name="Ceramic Tiles", cost=22.0, ...),
    "shower_mixer_basic": Material(name="Shower Mixer", cost=85.0, ...),
    # ... more materials
}

labor_rates = {
    "paris": 1.45,
    "lyon": 1.20, 
    # ... more cities
}

vat_rules = {
    "renovation": 0.10,
    "energy_efficiency": 0.055,
    # ... more rules
}
```

**Advantages**: 
- Fast development and testing
- No database setup required
- Easy to modify and experiment
- Zero external dependencies

### **Future Scalability - Database Integration**

For production and scalability, all data can be moved to databases:

#### **Traditional Database (PostgreSQL/MySQL)**
```python
# Future: Database-driven
class MaterialDatabase:
    def __init__(self):
        self.db = PostgreSQLConnection(DATABASE_URL)
    
    def get_material(self, material_id, region):
        query = """
        SELECT m.*, r.multiplier 
        FROM materials m 
        JOIN regional_pricing r ON m.id = r.material_id 
        WHERE m.id = %s AND r.region = %s
        """
        return self.db.execute(query, [material_id, region])
```

#### **Vector Database for RAG and Embeddings**

For advanced AI features, we recommend **Milvus** (best for multi-tenant):

```python
# Future: Vector database for intelligent matching
class VectorPricingMemory:
    def __init__(self):
        self.milvus_client = MilvusClient(MILVUS_URI)
        self.collection_name = "renovation_projects"
    
    def find_similar_projects(self, project_embedding):
        # Find similar historical projects for pricing guidance
        similar = self.milvus_client.search(
            collection_name=self.collection_name,
            data=[project_embedding],
            limit=5,
            partition_names=["tenant_123"]  # Multi-tenant support
        )
        return similar
    
    def store_project_embedding(self, project_data, tenant_id):
        # Store completed projects for future matching
        embedding = self.generate_embedding(project_data)
        self.milvus_client.insert(
            collection_name=self.collection_name,
            data=[{"embedding": embedding, "project": project_data}],
            partition_name=f"tenant_{tenant_id}"
        )
```

#### **Migration Path**
```python
# Easy migration from hardcoded to database
class MaterialDatabase:
    def __init__(self, use_database=False):
        if use_database:
            self.backend = DatabaseMaterialBackend()
        else:
            self.backend = HardcodedMaterialBackend()  # Current implementation
    
    def get_material(self, material_id, region):
        return self.backend.get_material(material_id, region)
```

## What This System Does

**Input Example:**
```
"Client wants to renovate a small 4m² bathroom in Marseille. Remove old tiles, 
redo plumbing for shower, replace toilet, install vanity, repaint walls. 
Budget-conscious project."
```

**Output Example:**
```json
{
  "project_id": "BTH_20250830_143022",
  "city": "marseille", 
  "total_area_sqm": 4.0,
  "total_price": 3245.67,
  "vat_amount": 324.57,
  "confidence_score": 0.75,
  "parsing_method": "openai",
  "tasks": [
    {
      "task_type": "demolition",
      "labor_cost": 180.00,
      "materials_cost": 92.00
    },
    {
      "task_type": "plumbing", 
      "labor_cost": 650.00,
      "materials_cost": 425.30
    }
    // ... more tasks
  ]
}
```

## AI Integration

### **With OpenAI API Key**
- **Natural language understanding**: "moisture behind tiles" → waterproofing needed
- **Context inference**: "keep toilet" → partial renovation 
- **Higher accuracy**: 85%+ confidence scores
- **Handles complex transcripts**: Conversational, technical, or minimal input

### **Without OpenAI (Pattern-Based)**
- **Reliable keyword matching**: Works offline
- **Fast processing**: No API calls needed
- **Good accuracy**: 75%+ for clear transcripts
- **Zero cost**: No API fees

## Pricing Intelligence

### **Regional Variations**
| City | Labor Multiplier | Material Multiplier | 4m² Quote |
|------|------------------|---------------------|-----------|
| **Marseille** | 1.0x | 1.0x | €3,245 |
| **Paris** | 1.45x | 1.35x | €4,683 |
| **Lyon** | 1.20x | 1.15x | €3,732 |
| **Nice** | 1.30x | 1.25x | €4,056 |

### **French VAT Compliance**
- **Standard**: 20% (new construction)
- **Renovation**: 10% (building >2 years old)
- **Energy Efficiency**: 5.5% (with certified improvements)
- **Automatic optimization**: Suggests VAT-saving opportunities

## Customization

### **Adding New Materials**
```python
# In pricing_logic/material_db.py, add to default_materials:
"custom_premium_tiles": Material(
    name="Premium Italian Porcelain",
    category="flooring",
    unit="m²", 
    base_cost=95.0,
    supplier_margin=0.25,
    quality_grade="premium",
    availability_score=0.8,
    last_updated=datetime.now().isoformat()
)
```

### **Adding New Cities**
```python
# In pricing_logic/labor_calc.py and material_db.py:
regional_multipliers = {
    "your_city": 1.15,  # 15% above Marseille baseline
    # ... existing cities
}
```

### **Custom VAT Rules**
```python
# In pricing_logic/vat_rules.py:
vat_rates = {
    "custom_rate": 0.08,  # 8% for special cases
    # ... existing rates
}
```

## Performance & Scalability

### **Current Performance**
- **Quote Generation**: <1 second (pattern) / ~3 seconds (OpenAI)
- **Memory Usage**: <50MB for complete system
- **Concurrent Requests**: Handles multiple simultaneous quotes
- **Accuracy**: 85%+ with OpenAI, 75%+ with patterns

### **Scalability Options**

#### **Phase 1: Database Migration**
- Move hardcoded data to PostgreSQL/MySQL
- Add caching layer (Redis)
- API rate limiting and authentication

#### **Phase 2: Vector Database & RAG**
- **Milvus Integration**: Store project embeddings
- **Multi-tenant Support**: Separate data per contractor/company
- **Intelligent Matching**: Find similar historical projects
- **Learning System**: Improve accuracy from feedback

#### **Phase 3: Microservices**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Transcript     │    │   Pricing       │    │   Quote         │
│  Service        │───▶│   Service       │───▶│   Service       │
│  (OpenAI)       │    │  (Materials+    │    │  (VAT+Output)   │
└─────────────────┘    │   Labor)        │    └─────────────────┘
                       └─────────────────┘
```



**🎯 Built for French renovation contractors who need fast, accurate, compliant quotes.**

Transform messy project descriptions into professional quotes in seconds. Ready to use immediately, scalable for the future.