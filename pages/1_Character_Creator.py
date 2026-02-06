"""
Synth.Human — Character Creator v2
Two-LLM pipeline: Persona Inference → Character Builder → Nano Banana Pro
"""

import streamlit as st
import fal_client
import json
import requests
import os

st.set_page_config(page_title="Character Creator — Synth.Human", page_icon="✦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
.stApp { background: linear-gradient(180deg, #0a0a0a 0%, #111111 50%, #0d0d0d 100%); font-family: 'Inter', sans-serif; }
#MainMenu, footer, header {visibility: hidden;}
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
.brand-mark { font-size: 1.1rem; font-weight: 600; color: #fff; display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem; }
.brand-mark span { color: #8b5cf6; }
.page-title { font-size: 2rem; font-weight: 700; color: #fff; margin-bottom: 0.25rem; }
.page-subtitle { font-size: 1rem; color: #666; margin-bottom: 2rem; }
.section-header { font-size: 0.75rem; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 1.5rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.06); }
.summary-bar { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 16px; margin: 1.5rem 0; color: #888; }
.summary-bar strong { color: #fff; }
.stButton > button { background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%) !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 0.75rem 2rem !important; font-weight: 600 !important; }
.stTextInput > div > div > input { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 8px !important; color: #fff !important; }
.stSelectbox > div > div { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 8px !important; }
.stRadio > label, .stSlider > label, .stSelectbox > label, .stTextInput > label { color: #888 !important; }
.stSlider > div > div > div > div { background: #8b5cf6 !important; }
.streamlit-expanderHeader { background: rgba(255,255,255,0.03) !important; border-radius: 8px !important; color: #888 !important; }
.divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent); margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# Data
SUBCULTURES = {
    "aesthetic_lifestyle": {"label": "Aesthetic / Lifestyle", "options": ["Clean Girl", "Quiet Luxury", "Old Money", "New Money", "Coastal Grandmother", "Cottagecore", "Dark Academia", "Light Academia", "Royalcore", "Balletcore", "Coquette", "Tomato Girl", "Vanilla Girl", "Strawberry Girl", "Latte Makeup", "Cold Girl", "It Girl", "That Girl"]},
    "street_urban": {"label": "Street / Urban", "options": ["Streetwear", "Hypebeast", "Gorpcore", "Blokecore", "Blokette", "Techwear", "Urbancore", "Athleisure", "Normcore", "Dadcore"]},
    "alternative_subversive": {"label": "Alternative / Subversive", "options": ["Indie Sleaze", "Downtown NYC", "Art Ho", "Grunge Revival", "Punk", "Goth", "E-Girl / E-Boy", "Soft Grunge", "Skater", "Bimbocore"]},
    "retro_nostalgic": {"label": "Retro / Nostalgic", "options": ["Y2K Revival", "90s Minimalism", "80s Glam", "70s Boho", "60s Mod", "Vintage Americana", "Rockabilly", "Disco", "McBling"]},
    "cultural_regional": {"label": "Cultural / Regional", "options": ["SoCal Wellness", "Miami Vice", "Brooklyn Creative", "Parisian Chic", "Scandi Minimalist", "British Prep", "Italian Sprezzatura", "Coastal California"]},
    "asian_subcultures": {"label": "Asian Subcultures", "options": ["Japanese Streetwear", "K-Fashion", "Harajuku", "Gyaru", "Visual Kei", "Mori Girl", "Ulzzang", "City Boy (JP)", "Hongdae Style", "Taiwanese Street"]},
    "professional_polished": {"label": "Professional / Polished", "options": ["Corporate Baddie", "Boss Babe", "Finance Bro", "Model Off Duty", "Creative Director", "Gallerina", "PR Girl", "Tech Minimalist"]},
    "niche_emerging": {"label": "Niche / Emerging", "options": ["Barbiecore", "Mermaidcore", "Fairycore", "Goblincore", "Grandpacore", "Cyber Y2K", "Twee Revival", "Indie Folk", "Jazz Club", "Festival", "Rave", "Skate Punk", "Surf", "Cottagecore Witch", "Dark Feminine"]}
}

ETHNICITIES = {
    "East Asian": ["Chinese (Han)", "Japanese", "Korean", "Taiwanese", "Vietnamese", "Filipino/a", "Thai"],
    "South Asian": ["Indian (North)", "Indian (South)", "Pakistani", "Bangladeshi", "Sri Lankan", "Nepali"],
    "Southeast Asian": ["Indonesian", "Malaysian", "Singaporean", "Cambodian", "Burmese"],
    "Middle Eastern / North African": ["Arab (Levantine)", "Arab (Gulf)", "Persian/Iranian", "Turkish", "Egyptian", "Moroccan", "Israeli"],
    "Black / African Descent": ["African American", "Caribbean", "West African", "East African", "South African", "Afro-Latino/a"],
    "Latino / Hispanic": ["Mexican", "Puerto Rican", "Dominican", "Colombian", "Brazilian", "Argentinian", "Cuban", "Central American"],
    "White / European": ["Northern European", "Southern European", "Eastern European", "Irish", "French", "Slavic"],
    "Mixed / Multiracial": ["Black + White", "Asian + White", "Latino + White", "Black + Asian", "Black + Latino", "Other Mix"],
    "Pacific Islander": ["Hawaiian", "Samoan", "Tongan", "Maori", "Fijian"],
    "Indigenous": ["Native American", "First Nations", "Indigenous Australian", "Indigenous Latin American"]
}

POPULAR_CITIES = ["Los Angeles", "New York City", "London", "Tokyo", "Miami", "Berlin", "Paris", "Seoul", "Chicago", "Toronto", "Dubai", "Sydney", "Milan", "Atlanta", "São Paulo", "Lagos", "Mumbai", "Shanghai", "Amsterdam", "Copenhagen", "Melbourne", "Austin", "San Francisco", "Barcelona", "Stockholm", "Singapore"]

ASPECT_RATIOS = {"9:16 (Vertical/UGC)": "9:16", "16:9 (Landscape)": "16:9", "1:1 (Square)": "1:1", "4:5 (Instagram)": "4:5"}

# Session state
for key in ['selected_subcultures', 'custom_subcultures', 'generated_character', 'character_image_url', 'persona_json']:
    if key not in st.session_state:
        st.session_state[key] = [] if 'subcultures' in key else None

# =============================================================================
# LLM 1: PERSONA INFERENCE ENGINE
# =============================================================================

def get_persona_inference_prompt(config):
    subcultures_str = ", ".join(config['subcultures'])
    return f'''You are a high-fidelity subculture-mapping and persona-inference engine. Your goal is to take user selections and reverse-engineer the "Social Media Truth" of who this person is.

INPUT SELECTIONS:
- Subcultures: {subcultures_str}
- Tier: {config['tier']}
- Age: {config['age']}
- Gender: {config['gender']}
- Ethnicity: {config['ethnicity']}
- Location: {config['location']}

YOUR TASK:
Analyze the subculture combination and demographic inputs. Infer a persona that is not just a demographic, but a "vibe" that would go viral on TikTok or Instagram.

THE "VIBE" ARCHITECTURE:
Aesthetic Gravity: How do these subcultures blend? What's the specific internet micro-aesthetic?
Social Capital: Is this person a "gatekeeper," a "trend-setter," or a "curator"?
Identity Nuance: Based on the subcultures and location, what specific style markers define them?

SUBCULTURE BLENDING RULES:
- If multiple subcultures selected, the FIRST is primary (70%), others add texture (30%)
- Find the authentic overlap — what does a real person who exists in these communities look like?
- Avoid costume mashups — find the coherent identity

OUTPUT FORMAT (STRICT JSON, NO MARKDOWN):
{{
  "brand_analysis": {{
    "brand_tier": "{config['tier'].lower()}",
    "aesthetic_core": "the blended micro-aesthetic name",
    "cultural_associations": ["list", "of", "cultural", "markers"],
    "market_positioning": "one sentence on why this persona is culturally relevant now"
  }},
  "buyer_persona": {{
    "age": {config['age']},
    "gender_presentation": "{config['gender'].lower()}",
    "physical_identity_signals": {{
      "ethnicity": "{config['ethnicity']}",
      "style_archetype": "specific archetype e.g. 'Bushwick Art School Dropout' or 'SoCal Wellness Creative'",
      "hair_vibe": "specific hair description aligned to subculture + tier",
      "skin_undertone": "specific undertone based on ethnicity"
    }},
    "personality": "one-sentence psychological profile",
    "social_capital": "gatekeeper | trend-setter | curator"
  }},
  "viral_context": {{
    "platform": "TikTok | Instagram",
    "scene_location": "specific residential interior aligned to vibe, tier, and geography",
    "lighting_profile": "specific lighting description for this location",
    "camera_feel": "UGC camera energy description"
  }}
}}'''

# =============================================================================
# LLM 2: CHARACTER BUILDER (Full JSON for Nano Banana Pro)
# =============================================================================

def get_character_builder_prompt(persona_json, config):
    persona_str = json.dumps(persona_json, indent=2)
    
    tier_rules = {
        "Budget": "BUDGET: Actually lived-in (IKEA, mismatched decor, wear). High clutter (charger cords, laundry visible). Oops items: chain coffee, Amazon package. Lighting: whatever's available. Hair: air-dried. Outfit: grabbed not chosen.",
        "Mid": "MID: Tidy but personal (Target/West Elm level). Medium clutter (book open, thriving plant). Oops: tote on door. Good natural light. Hair: styled but easy. Put-together effortless.",
        "Premium": "PREMIUM: Curated design-conscious (statement chair, intentional art). Low-curated clutter. Oops: artful disorder (sunglasses on table). Beautiful natural light. Hair: intentional effortless. Everything fits perfectly.",
        "Luxury": "LUXURY: Architectural (high ceilings, statement furniture). Minimal-intentional clutter. Oops: Hermès on floor, jacket on $15k chair. Perfect natural light. Hair: salon-perfect but natural. Immaculate presentation."
    }
    
    age_rules = ""
    age = config['age']
    if age <= 23:
        age_rules = "AGE 18-23: 'First real space' energy. Transitional quality. Evidence of social life (extra shoes, borrowed jacket). Roommate probability high. Things are new-ish."
    elif age <= 29:
        age_rules = "AGE 24-29: Establishing phase. More intentional but evolving. Likely alone or with partner. Starting to replace early-20s furniture. Objects have short histories."
    else:
        age_rules = "AGE 30-38: Settled. Everything chosen. Years of editing. Objects have stories. Vintage pieces, travel acquisitions. No transitional furniture."

    return f'''You are the Character Architect for Nano Banana Pro. Generate a DETAILED JSON that will be passed DIRECTLY to the image model as the prompt.

PERSONA FROM NODE 1:
{persona_str}

USER SELECTIONS:
- Tier: {config['tier']}
- Age: {config['age']}
- Gender: {config['gender']}
- Ethnicity: {config['ethnicity']}
- Location: {config['location']}
- Subcultures: {", ".join(config['subcultures'])}

{tier_rules[config['tier']]}

{age_rules}

═══ CAMERA ANGLE & FRAMING (CRITICAL) ═══

This is the "phone propped on desk" angle. Camera is BELOW subject, looking UP.

CAMERA POSITION:
- Phone on surface (desk, nightstand, shelf) at waist-to-chest height
- Lens angled UPWARD toward subject's face
- Slight low-angle perspective—NOT selfie, NOT eye-level
- Subject appears looking DOWN at camera, face fully visible

WHAT THIS LOOKS LIKE:
- Subject's chin slightly visible from below (natural, not unflattering)
- Ceiling/upper walls may be visible in background
- Background shows room BEHIND and ABOVE subject

SUBJECT POSITION:
- SEATED OR PERCHED: edge of bed, chair arm, leaning against furniture, couch
- Upper body upright but relaxed, slight lean forward
- Waist-up or chest-up framing
- Face is focus but torso and hands visible

DO NOT: eye-level camera, overhead angle, selfie with arm, standing poses

═══ POSE & HANDS (CRITICAL) ═══

Relaxed "just pressed record" state. NOT holding anything.

HAND OPTIONS (choose one):
- Both hands resting on lap/thighs
- One on lap, other touching surface they sit on
- Hands lightly clasped in lap
- One on knee, other relaxed

BANNED: Holding anything, hands hidden, gesturing at nothing, hands near face, arms crossed

EXPRESSION: "About to say something" — mouth slightly parted, engaged with camera, slight smirk, eyebrows slightly raised, eyes looking into lens with catchlight

═══ SPECIFICITY MANDATE ═══

Every object must be SPECIFIC and REAL. If you can't Google it and buy it, it's too vague.

BANNED: "a painting", "coffee table books", "a plant", "nice chair", "a lamp", "a rug", "coffee"

FOR EACH OBJECT:
1. What SPECIFIC item would this persona at this tier actually own?
2. How acquired? (Budget=thrift/Amazon, Mid=DTC/vintage, Premium=design stores, Luxury=auctions)
3. Provenance story?
4. Instagram comment test — would their community recognize this?

═══ GEOGRAPHIC COHERENCE ═══

Location: {config['location']}
- What building types common for this tier here?
- What era of construction? What details?
- What's realistic square footage?
- What latitude/weather affects light?
- What local stores/brands would they shop?
- "Visiting friend" test — would a local spot anything wrong?

═══ BANNED VISUAL CUES ═══

NEVER: crying/teary eyes, under-eye darkness, gray skin, slumped posture, thousand-yard stare, dark vignette, catalog lighting, stiff symmetrical pose, performative smile, airbrushed skin, furniture-ad environment, tier mismatch, UI overlays

═══ OUTPUT JSON (STRICT — NO MARKDOWN, NO META, NO NEGATIVE_CONSTRAINTS) ═══

{{
  "inherited_context": {{
    "brand_tier": "{config['tier'].lower()}",
    "age": {config['age']},
    "geographic_context": "{config['location']}"
  }},
  "identity_parameters": {{
    "preserve_face": true,
    "preserve_body_type": true,
    "physicality_details": {{
      "ethnicity_heritage": "{config['ethnicity']}",
      "skin_texture": "SPECIFIC: undertone + texture + marks",
      "facial_features": "SPECIFIC: eye shape, brows, lips, bone structure, distinctive marks",
      "hair_specification": "SPECIFIC: color + texture code + style + length + condition"
    }}
  }},
  "persona_vibe": {{
    "style_archetype": "from persona inference",
    "expression": "SPECIFIC micro-expression with 'about to speak' energy",
    "energy": "SPECIFIC energy aligned to tier"
  }},
  "the_shot": {{
    "camera_position": "phone propped on [specific surface] at [height], angled upward toward subject",
    "camera_specs": "iPhone 15 Pro, 24mm wide, NO UI elements",
    "framing": "chest-up or waist-up, subject looking down at camera, face fully visible",
    "subject_position": "seated on [specific furniture], upper body upright with slight forward lean",
    "lighting": "SPECIFIC to location and tier",
    "aesthetic_artifacts": "subtle iPhone artifacts for lighting conditions"
  }},
  "pose_details": {{
    "seated_on": "SPECIFIC furniture piece",
    "torso_orientation": "facing camera with natural asymmetry",
    "head_position": "chin slightly down, eyes engaged with lens below",
    "left_hand": "SPECIFIC relaxed position",
    "right_hand": "SPECIFIC relaxed position",
    "hands_holding": "NOTHING - hands must be empty"
  }},
  "environment": {{
    "setting": {{
      "room_type": "SPECIFIC room with architectural details for geography",
      "square_footage_feel": "realistic for tier and location",
      "architectural_details": "SPECIFIC to geography and building type",
      "what_is_visible_behind_subject": "SPECIFIC background above/behind seated subject from low angle"
    }},
    "specific_objects": [
      {{"category": "furniture_subject_sits_on", "specific_item": "EXACT brand/item", "placement": "where in frame"}},
      {{"category": "background_furniture", "specific_item": "EXACT item", "placement": "where", "provenance": "how acquired"}},
      {{"category": "wall_decor", "specific_item": "EXACT artwork/poster with artist", "placement": "upper frame", "provenance": "how acquired"}},
      {{"category": "surface_object", "specific_item": "EXACT item with brand", "placement": "where", "provenance": "how acquired"}},
      {{"category": "oops_item", "specific_item": "tier-appropriate casual item", "placement": "where", "provenance": "why it's there"}}
    ],
    "atmosphere": "lighting, mood, lived-in quality"
  }},
  "base_outfit": {{
    "top": "SPECIFIC brand + style + color + condition",
    "bottom": "SPECIFIC brand + style + condition (may only show waistband)",
    "visible_accessories": "SPECIFIC items or 'none'",
    "note": "why this outfit makes sense for this moment"
  }}
}}'''

# =============================================================================
# LLM & IMAGE GENERATION
# =============================================================================

def call_llm(prompt, provider, api_key, model):
    if provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], max_tokens=4000)
        return response.choices[0].message.content
    elif provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(model=model, max_tokens=4000, messages=[{"role": "user", "content": prompt}])
        return response.content[0].text
    elif provider == "google":
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model_obj = genai.GenerativeModel(model)
        response = model_obj.generate_content(prompt)
        return response.text

def parse_json_response(response):
    json_str = response.strip()
    if "```json" in json_str:
        json_str = json_str.split("```json")[1].split("```")[0]
    elif "```" in json_str:
        json_str = json_str.split("```")[1].split("```")[0]
    return json.loads(json_str.strip())

def generate_character_image(character_json, fal_key, aspect_ratio):
    os.environ["FAL_KEY"] = fal_key
    prompt_string = json.dumps(character_json, indent=2)
    result = fal_client.subscribe(
        "fal-ai/nano-banana-pro",
        arguments={
            "prompt": prompt_string,
            "negative_prompt": "blurry, low quality, distorted, deformed, ugly, bad anatomy, bad hands, missing fingers, watermark, text, logo, UI elements, phone screen, camera interface, timestamp, battery icon, airbrushed skin, catalog lighting, stiff pose, fake smile, depression, sad, crying, gray skin, dark vignette, standing pose, eye-level camera, selfie arm, holding phone, holding object",
            "aspect_ratio": aspect_ratio,
            "num_images": 1
        }
    )
    return result["images"][0]["url"]

# =============================================================================
# MAIN APP
# =============================================================================

def main():
    st.markdown('<div class="brand-mark"><span>✦</span> Synth.Human</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Character Creator</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Build a persistent character for your UGC videos.</div>', unsafe_allow_html=True)
    
    # API Config
    with st.expander("🔑 API Configuration", expanded=not st.session_state.get('api_configured')):
        c1, c2 = st.columns(2)
        with c1:
            fal_key = st.text_input("fal.ai API Key", type="password", placeholder="Enter fal.ai key...")
        with c2:
            llm_provider = st.selectbox("LLM Provider", ["OpenAI", "Anthropic (Claude)", "Google (Gemini)"])
        c3, c4 = st.columns(2)
        with c3:
            llm_key = st.text_input("LLM API Key", type="password", placeholder="Enter LLM key...")
        with c4:
            models = {"OpenAI": ["gpt-4o", "gpt-4o-mini", "gpt-4.1"], "Anthropic (Claude)": ["claude-sonnet-4-20250514", "claude-opus-4-20250514"], "Google (Gemini)": ["gemini-2.0-flash", "gemini-2.0-pro"]}
            llm_model = st.selectbox("Model", models[llm_provider])
        aspect_ratio = st.selectbox("Aspect Ratio", list(ASPECT_RATIOS.keys()), index=0)
        if fal_key and llm_key:
            st.session_state.api_configured = True
            st.session_state.fal_key = fal_key
            st.session_state.llm_key = llm_key
            st.session_state.llm_provider = {"OpenAI": "openai", "Anthropic (Claude)": "anthropic", "Google (Gemini)": "google"}[llm_provider]
            st.session_state.llm_model = llm_model
            st.session_state.aspect_ratio = ASPECT_RATIOS[aspect_ratio]
            st.success("✓ Configured")
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Subcultures
    st.markdown('<p class="section-header">Subcultures — Select up to 3</p>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        custom_input = st.text_input("Search or add custom", placeholder="Type to search...", label_visibility="collapsed")
    with c2:
        if st.button("+ Add Custom") and custom_input and custom_input not in st.session_state.selected_subcultures and len(st.session_state.selected_subcultures) < 3:
            st.session_state.selected_subcultures.append(custom_input)
            st.rerun()
    
    if st.session_state.selected_subcultures:
        cols = st.columns(len(st.session_state.selected_subcultures) + 1)
        for i, sub in enumerate(st.session_state.selected_subcultures):
            with cols[i]:
                if st.button(f"✕ {sub}", key=f"rm_{sub}"):
                    st.session_state.selected_subcultures.remove(sub)
                    st.rerun()
        with cols[-1]:
            st.caption(f"{3 - len(st.session_state.selected_subcultures)} left")
    
    for cat_key, cat_data in SUBCULTURES.items():
        filtered = [o for o in cat_data["options"] if not custom_input or custom_input.lower() in o.lower()]
        if not filtered:
            continue
        with st.expander(cat_data["label"]):
            cols = st.columns(5)
            for i, opt in enumerate(filtered):
                with cols[i % 5]:
                    sel = opt in st.session_state.selected_subcultures
                    if st.button(f"{'✓ ' if sel else ''}{opt}", key=f"s_{cat_key}_{opt}", use_container_width=True):
                        if sel:
                            st.session_state.selected_subcultures.remove(opt)
                        elif len(st.session_state.selected_subcultures) < 3:
                            st.session_state.selected_subcultures.append(opt)
                        st.rerun()
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Demographics
    st.markdown('<p class="section-header">Demographics</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        tier = st.radio("Tier", ["Budget", "Mid", "Premium", "Luxury"], index=2)
    with c2:
        gender = st.radio("Gender", ["Female", "Male", "Non-binary"])
    with c3:
        age = st.slider("Age", 18, 38, 24)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Ethnicity
    st.markdown('<p class="section-header">Ethnicity</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        eth_region = st.selectbox("Region", list(ETHNICITIES.keys()))
    with c2:
        eth_specific = st.selectbox("Specific", ETHNICITIES[eth_region])
    use_custom_eth = st.checkbox("Custom ethnicity")
    ethnicity = st.text_input("Custom", placeholder='e.g. "Half Korean, half Black"') if use_custom_eth else eth_specific
    if use_custom_eth and not ethnicity:
        ethnicity = eth_specific
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Location
    st.markdown('<p class="section-header">Location</p>', unsafe_allow_html=True)
    cols = st.columns(8)
    for i, city in enumerate(POPULAR_CITIES[:16]):
        with cols[i % 8]:
            if st.button(city, key=f"c_{city}", use_container_width=True):
                st.session_state.selected_city = city
                st.rerun()
    use_custom_loc = st.checkbox("Custom location")
    location = st.text_input("Custom loc", placeholder='e.g. "Austin, TX"') if use_custom_loc else st.session_state.get('selected_city', 'Los Angeles')
    if use_custom_loc and not location:
        location = st.session_state.get('selected_city', 'Los Angeles')
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Summary
    subs = " + ".join(st.session_state.selected_subcultures) or "None"
    st.markdown(f'<div class="summary-bar"><strong>{subs}</strong> • {tier} • {age} • {gender} • {ethnicity} • {location}</div>', unsafe_allow_html=True)
    
    # Generate
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        gen = st.button("✦ Generate Character", use_container_width=True, type="primary")
    
    if gen:
        if not st.session_state.selected_subcultures:
            st.error("Select at least one subculture")
        elif not st.session_state.get('api_configured'):
            st.error("Configure API keys first")
        else:
            config = {"subcultures": st.session_state.selected_subcultures, "tier": tier, "age": age, "gender": gender, "ethnicity": ethnicity, "location": location}
            
            # LLM 1: Persona Inference
            with st.spinner("Step 1/3: Inferring persona..."):
                try:
                    p1 = get_persona_inference_prompt(config)
                    r1 = call_llm(p1, st.session_state.llm_provider, st.session_state.llm_key, st.session_state.llm_model)
                    persona = parse_json_response(r1)
                    st.session_state.persona_json = persona
                except Exception as e:
                    st.error(f"Persona inference failed: {e}")
                    st.stop()
            
            # LLM 2: Character Builder
            with st.spinner("Step 2/3: Building character JSON..."):
                try:
                    p2 = get_character_builder_prompt(persona, config)
                    r2 = call_llm(p2, st.session_state.llm_provider, st.session_state.llm_key, st.session_state.llm_model)
                    character = parse_json_response(r2)
                    st.session_state.generated_character = character
                except Exception as e:
                    st.error(f"Character build failed: {e}")
                    st.stop()
            
            # Image Generation
            with st.spinner("Step 3/3: Generating image..."):
                try:
                    url = generate_character_image(character, st.session_state.fal_key, st.session_state.aspect_ratio)
                    st.session_state.character_image_url = url
                except Exception as e:
                    st.error(f"Image generation failed: {e}")
                    st.stop()
            st.rerun()
    
    # Display Results
    if st.session_state.generated_character and st.session_state.character_image_url:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        char = st.session_state.generated_character
        c1, c2 = st.columns([1, 1])
        with c1:
            st.image(st.session_state.character_image_url, use_container_width=True)
        with c2:
            ctx = char.get('inherited_context', {})
            st.markdown(f"### {ctx.get('geographic_context', 'Character')}")
            vibe = char.get('persona_vibe', {})
            st.markdown(f"*{vibe.get('style_archetype', '')}*")
            
            with st.expander("Identity", expanded=True):
                phys = char.get('identity_parameters', {}).get('physicality_details', {})
                for k, v in phys.items():
                    st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")
            
            with st.expander("Pose & Shot"):
                pose = char.get('pose_details', {})
                shot = char.get('the_shot', {})
                st.markdown(f"**Seated on:** {pose.get('seated_on', 'N/A')}")
                st.markdown(f"**Camera:** {shot.get('camera_position', 'N/A')}")
                st.markdown(f"**Lighting:** {shot.get('lighting', 'N/A')}")
            
            with st.expander("Environment"):
                env = char.get('environment', {})
                setting = env.get('setting', {})
                st.markdown(f"**Room:** {setting.get('room_type', 'N/A')}")
                st.markdown(f"**Behind subject:** {setting.get('what_is_visible_behind_subject', 'N/A')}")
                for obj in env.get('specific_objects', []):
                    st.markdown(f"- **{obj.get('category', '')}:** {obj.get('specific_item', '')}")
            
            with st.expander("Outfit"):
                outfit = char.get('base_outfit', {})
                for k, v in outfit.items():
                    st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")
            
            with st.expander("Full JSON"):
                st.json(char)
            
            if st.session_state.persona_json:
                with st.expander("Persona Inference (LLM 1)"):
                    st.json(st.session_state.persona_json)
        
        # Actions
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("📥 JSON", json.dumps(char, indent=2).encode(), "character.json", "application/json", use_container_width=True)
        with c2:
            img = requests.get(st.session_state.character_image_url).content
            st.download_button("🖼️ Image", img, "character.png", "image/png", use_container_width=True)
        with c3:
            if st.button("🎬 Use in UGC", use_container_width=True):
                st.session_state.ugc_character = char
                st.session_state.ugc_character_image = st.session_state.character_image_url
                st.info("Saved! Go to main app.")
        
        if st.button("↻ Regenerate"):
            st.session_state.generated_character = None
            st.session_state.character_image_url = None
            st.session_state.persona_json = None
            st.rerun()

if __name__ == "__main__":
    main()
