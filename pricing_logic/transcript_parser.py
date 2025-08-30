import json
import os
import re
from typing import Dict, Optional

class SmartTranscriptParser:
    """
    OpenAI-powered transcript parser
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = None
        
        # Initialize OpenAI
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
            print("OpenAI client initialized successfully")
        except ImportError:
            raise ImportError("ERROR: OpenAI package not installed. Run: pip install openai")
        except Exception as e:
            raise Exception(f"ERROR: OpenAI initialization failed: {e}")
    
    def parse_transcript(self, transcript: str) -> Dict:
        """
        Parse transcript using OpenAI GPT
        Returns structured data for the pricing engine
        """
        
        system_prompt = """
        You are an expert renovation quote parser. Extract structured data from voice transcripts about bathroom renovations.
        
        Return a JSON object with these exact fields:
        {
          "area_sqm": number (extract area in square meters, default 4.0 if not mentioned),
          "city": string (French city name, lowercase, default "marseille"),
          "tasks": [
            {
              "type": string (one of: "demolition", "plumbing", "electrical", "tiling", "painting", "installation"),
              "description": string,
              "urgency": string (one of: "low", "medium", "high"),
              "complexity_factors": [string] (e.g., ["small_tiles", "waterproofing", "tight_access"])
            }
          ],
          "budget_conscious": boolean,
          "urgency_level": string (one of: "low", "medium", "high", "rush"),
          "special_requirements": [string] (any special needs mentioned)
        }
        
        Common French cities: marseille, paris, lyon, toulouse, nice, nantes, bordeaux, strasbourg, lille, montpellier
        
        Task types and keywords:
        - "demolition": remove, tear out, demo, strip, clear
        - "plumbing": pipes, shower, toilet, water, plumbing, mixer, basin
        - "electrical": wiring, lights, ventilation, electrical, fan, power
        - "tiling": tiles, flooring, walls, ceramic, stone, mosaic
        - "painting": paint, color, walls, ceiling, repaint
        - "installation": install, replace, vanity, fixtures, mirror, cabinet
        
        Complexity factors:
        - "small_tiles": small, mini, mosaic tiles
        - "waterproofing": waterproof, membrane, seal, moisture
        - "tight_access": tight, narrow, difficult access
        - "curved_surfaces": curved, round, corner cuts
        - "premium_materials": luxury, premium, high-end
        - "custom_work": custom, bespoke, made-to-measure
        
        Return ONLY the JSON object, no other text.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this renovation transcript: {transcript}"}
                ],
                #temperature=0.1,
                #max_tokens=4000
            )
            
            # Get and clean the response
            content = response.choices[0].message.content.strip()
            
            # Remove any markdown formatting
            if content.startswith("```"):
                content = re.sub(r"```(?:json)?\n?", "", content)
                content = content.replace("```", "").strip()
            
            # Parse JSON
            parsed_json = json.loads(content)
            
            # Add confidence score and parsing method
            parsed_json["confidence_score"] = self._calculate_confidence(parsed_json, transcript)
            parsed_json["parsing_method"] = "openai"
            
            return parsed_json
            
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse OpenAI response: {e}")
            print(f"Response was: {content[:200]}...")
            raise e
        except Exception as e:
            print(f"ERROR: OpenAI API call failed: {e}")
            raise e
    
    def _calculate_confidence(self, parsed_data: Dict, transcript: str) -> float:
        """Calculate confidence based on parsing completeness"""
        
        confidence = 0.75  # Base confidence for AI parsing
        
        # Boost for explicit measurements
        if any(indicator in transcript.lower() for indicator in ["m²", "meter", "square"]):
            confidence += 0.1
        
        # Boost for city mention
        french_cities = ["paris", "lyon", "marseille", "toulouse", "nice", "nantes", "bordeaux"]
        if any(city in transcript.lower() for city in french_cities):
            confidence += 0.1
        
        # Boost for multiple tasks
        task_count = len(parsed_data.get("tasks", []))
        if task_count >= 3:
            confidence += 0.1
        elif task_count >= 2:
            confidence += 0.05
        
        # Boost for complexity factors
        total_complexity = sum(
            len(task.get("complexity_factors", [])) 
            for task in parsed_data.get("tasks", [])
        )
        if total_complexity > 0:
            confidence += min(0.05, total_complexity * 0.02)
        
        # Penalty for very short transcript
        word_count = len(transcript.split())
        if word_count < 10:
            confidence -= 0.2
        elif word_count < 20:
            confidence -= 0.1
        
        return max(0.3, min(1.0, confidence))

def main():
    
    
    print("OpenAI Transcript Parser Demo")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: No OpenAI API key found!")
        print("Set OPENAI_API_KEY environment variable")
        return
    
    # Initialize parser
    try:
        parser = SmartTranscriptParser(api_key)
    except Exception as e:
        print(f"ERROR: failed to initialize parser: {e}")
        return

if __name__ == "__main__":
    main()