"""
Synth.Human — Character Creator
Build persistent characters for UGC video generation.
JSON output is passed directly to Nano Banana Pro as the prompt.
"""

import streamlit as st
import fal_client
import json
import requests
import os

# ============================================================
# PAGE CONFIG & CUSTOM CSS
# ============================================================

st.set_page_config(
    page_title="Character Creator — Synth.Human",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp {
        background: linear-gradient(180deg, #0a0a0a 0%, #111111 50%, #0d0d0d 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    #MainMenu, footer, header {visibility: hidden;}
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
    .brand-mark { font-size: 1.1rem; font-weight: 600; color: #fff; display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem; }
    .brand-mark span { color: #8b5cf6; }
    .page-title { font-size: 2rem; font-weight: 700; color: #fff; margin-bottom: 0.25rem; }
    .page-subtitle { font-size: 1rem; color: #666; margin-bottom: 2rem; }
    .section-header { font-size: 0.75rem; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 1.5rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.06); }
    .summary-bar { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 16px; margin: 1.5rem 0; color: #888; font-size: 0.9rem; }
    .summary-bar strong { color: #fff; }
    .stButton > button { background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%) !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 0.75rem 2rem !important; font-weight: 600 !important; }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea { background: rgba(255, 255, 255, 0.05) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 8px !important; color: #fff !important; }
    .stTextInput > label, .stTextArea > label, .stSelectbox > label { color: #888 !important; }
    .stSelectbox > div > div { background: rgba(255, 255, 255, 0.05) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 8px !important; }
    .stRadio > label { color: #888 !important; }
    .stSlider > div > div > div > div { background: #8b5cf6 !important; }
    .stSlider > label { color: #888 !important; }
    .streamlit-expanderHeader { background: rgba(255, 255, 255, 0.03) !important; border-radius: 8px !important; color: #888 !important; }
    .divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent); margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA
# ============================================================

SUBCULTURES = {
    "aesthetic_lifestyle": {
        "label": "Aesthetic / Lifestyle",
        "options": ["Clean Girl", "Quiet Luxury", "Old Money", "New Money", "Coastal Grandmother", "Cottagecore", "Dark Academia", "Light Academia", "Royalcore", "Balletcore", "Coquette", "Tomato Girl", "Vanilla Girl", "Strawberry Girl", "Latte Makeup", "Cold Girl", "It Girl", "That Girl"]
    },
    "street_urban": {
        "label": "Street / Urban",
        "options": ["Streetwear", "Hypebeast", "Gorpcore", "Blokecore", "Blokette", "Techwear", "Urbancore", "Athleisure", "Normcore", "Dadcore"]
    },
    "alternative_subversive": {
        "label": "Alternative / Subversive",
        "options": ["Indie Sleaze", "Downtown NYC", "Art Ho", "Grunge Revival", "Punk", "Goth", "E-Girl / E-Boy", "Soft Grunge", "Skater", "Bimbocore"]
    },
    "retro_nostalgic": {
        "label": "Retro / Nostalgic",
        "options": ["Y2K Revival", "90s Minimalism", "80s Glam", "70s Boho", "60s Mod", "Vintage Americana", "Rockabilly", "Disco", "McBling"]
    },
    "cultural_regional": {
        "label": "Cultural / Regional",
        "options": ["SoCal Wellness", "Miami Vice", "Brooklyn Creative", "Parisian Chic", "Scandi Minimalist", "British Prep", "Italian Sprezzatura", "Coastal California"]
    },
    "asian_subcultures": {
        "label": "Asian Subcultures",
        "options": ["Japanese Streetwear", "K-Fashion", "Harajuku", "Gyaru", "Visual Kei", "Mori Girl", "Ulzzang", "City Boy (JP)", "Hongdae Style", "Taiwanese Street"]
    },
    "professional_polished": {
        "label": "Professional / Polished",
        "options": ["Corporate Baddie", "Boss Babe", "Finance Bro", "Model Off Duty", "Creative Director", "Gallerina", "PR Girl", "Tech Minimalist"]
    },
    "niche_emerging": {
        "label": "Niche / Emerging",
        "options": ["Barbiecore", "Mermaidcore", "Fairycore", "Goblincore", "Grandpacore", "Cyber Y2K", "Twee Revival", "Indie Folk", "Jazz Club", "Festival", "Rave", "Skate Punk", "Surf", "Cottagecore Witch", "Dark Feminine"]
    }
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

RESOLUTION_OPTIONS = {
    "1K (1024px)": {"width": 1024, "height": 1820},
    "2K (1440px)": {"width": 1440, "height": 2560},
    "4K (2160px)": {"width": 2160, "height": 3840}
}

# Session state
if 'selected_subcultures' not in st.session_state:
    st.session_state.selected_subcultures = []
if 'custom_subcultures' not in st.session_state:
    st.session_state.custom_subcultures = []
if 'generated_character' not in st.session_state:
    st.session_state.generated_character = None
if 'character_image_url' not in st.session_state:
    st.session_state.character_image_url = None

# ============================================================
# CHARACTER GENERATION PROMPT (FULL SPECIFICITY)
# ============================================================

def get_character_prompt(config):
    subcultures_str = ", ".join(config['subcultures'])
    primary_subculture = config['subcultures'][0]
    secondary_subcultures = config['subcultures'][1:] if len(config['subcultures']) > 1 else []
    
    blend_instruction = ""
    if secondary_subcultures:
        blend_instruction = f"SUBCULTURE BLENDING: Primary={primary_subculture} (70%), Secondary={', '.join(secondary_subcultures)} (30%). Blend cohesively like a real person in overlapping communities."

    tier_rules = {
        "Budget": "BUDGET: Lived-in environment (IKEA, charger cords, uneven light). Hair=air-dried. Skin=minor imperfections OK. Outfit=grabbed not chosen. Acquisition=Target/Amazon/thrift.",
        "Mid": "MID: Tidy but personal (some decor, good light). Hair=styled easy. Skin=clear but real pores. Outfit=put-together effortless. Acquisition=Zara/COS/Everlane/vintage.",
        "Premium": "PREMIUM: Curated design-conscious (statement furniture, quality materials). Hair=intentional effortless. Skin=healthy glow with texture. Outfit=perfect fit, quality fabrics. Acquisition=HAY/design stores/galleries.",
        "Luxury": "LUXURY: Architectural space (high ceilings, art). Hair=salon perfect but natural. Skin=immaculate with texture. Outfit=quiet luxury, no logos. Acquisition=auctions/dealers/commissioned."
    }

    subcultures_json = json.dumps(config['subcultures'])

    return f'''You are the Character Architect for Synth.Human. Generate a DETAILED JSON that will be passed DIRECTLY to Nano Banana Pro as the prompt. THE JSON IS THE PROMPT.

INPUT: Subcultures={subcultures_str} | Tier={config['tier']} | Age={config['age']} | Gender={config['gender']} | Ethnicity={config['ethnicity']} | Location={config['location']}

{blend_instruction}

{tier_rules[config['tier']]}

═══ SPECIFICITY MANDATE (CRITICAL) ═══
Every object must be SPECIFIC and REAL. If you can't Google it and buy it, it's too vague.

BANNED: "a painting", "artwork", "coffee table books", "a plant", "nice chair", "modern furniture", "a lamp", "sneaker boxes", "a rug", "coffee", "jewelry", "a bag", "nice clothes"

FOR EACH OBJECT DETERMINE:
1. What SPECIFIC item would this persona at this income level actually own?
2. How did they acquire it? (Budget=thrift/Amazon, Mid=DTC/vintage, Premium=design stores, Luxury=auctions/galleries)
3. What's the provenance story?
4. Does it pass the Instagram comment test for this community?

OUTPUT: Brand + product name (mass-produced), OR artist + title (art), OR material + style + origin (vintage)

═══ EXPRESSION & ENERGY ═══
- DEFAULT: Relaxed, present, "okay here's the fit" energy
- MICRO-EXPRESSIONS: Slight smirk, one eyebrow raised, mid-word mouth, "about to say something" - NO posed smiles, NO thousand-yard stare
- EYES: Engaged with lens, catchlight visible, natural blink-ready

═══ PHYSICALITY & SKIN ═══
- HEALTHY BUT REAL: Visible pores always. Budget/Mid=minor imperfections OK. Premium/Luxury=clearer but NEVER airbrushed
- POSTURE: Natural asymmetry (weight on one leg, shoulder dropped). NEVER stiff catalog, NEVER slumped
- HAIR: Budget=air-dried. Mid=styled easy. Premium=intentional effortless. Luxury=salon perfect but natural
- HANDS: EMPTY. No phone, no drink, no props. Visible and relaxed.

═══ BANNED VISUAL CUES (NEVER GENERATE) ═══
DEPRESSION MARKERS: crying/teary eyes, puffy eyes, smeared makeup, under-eye darkness, gray skin, slumped posture, thousand-yard stare, dark vignette, desaturation, moody low-key lighting
STOCK MARKERS: catalog lighting, stiff symmetrical posing, performative smiles, furniture-ad environments, airbrushed skin
TIER MISMATCH: luxury person in budget environment, budget clutter in premium space
UI ARTIFACTS: phone UI, camera interface, timestamps, battery icons, watermarks

═══ CAMERA SPECS ═══
iPhone 15 Pro, 24mm wide, handheld/tripod energy, medium shot waist-up, 9:16 vertical, STANDING front-facing, direct eye contact, natural light only

═══ OUTPUT JSON (STRICT - NO MARKDOWN) ═══

{{
  "meta": {{
    "character_name": "fitting first name",
    "archetype_summary": "one evocative line e.g. 'Pilates before the gallery opening'",
    "subcultures": {subcultures_json},
    "tier": "{config['tier']}",
    "location": "{config['location']}"
  }},
  "identity_parameters": {{
    "preserve_face": true,
    "preserve_body_type": true,
    "age": {config['age']},
    "gender": "{config['gender']}",
    "physicality_details": {{
      "ethnicity_heritage": "{config['ethnicity']}",
      "skin_texture": "SPECIFIC undertone + texture + marks e.g. 'warm olive, visible pores, natural T-zone sheen, faint nose freckles'",
      "facial_features": "SPECIFIC eye shape + brow + lips + bone structure",
      "hair_specification": "SPECIFIC color + texture code + style + length + condition e.g. 'dark brown 2A waves, center part, air-dry texture, collarbone length'",
      "body_type": "SPECIFIC build + proportions"
    }}
  }},
  "persona_vibe": {{
    "style_archetype": "blended subculture identity 3-5 words",
    "expression": "SPECIFIC micro-expression e.g. 'slight smirk, left eyebrow micro-raised, eyes engaged'",
    "energy": "SPECIFIC e.g. 'relaxed confidence, just-said-something-clever, present not performing'",
    "posture": "SPECIFIC e.g. 'weight on right leg, left hip out, shoulders asymmetrical, right hand at hip'"
  }},
  "the_shot": {{
    "camera_specs": "iPhone 15 Pro, 24mm wide, handheld, eye-level, NO UI",
    "framing": "medium shot, waist-up, slightly off-center, 9:16 vertical",
    "distance": "arm's length OR tripod at 4-5 feet",
    "lighting": "SPECIFIC to location/time e.g. 'late morning LA light, soft west window, warm tone'",
    "aesthetic_artifacts": "SPECIFIC e.g. 'slight lens warmth, shallow DOF on background, micro handheld energy'"
  }},
  "environment_clutter": {{
    "setting": "SPECIFIC room + building + era + neighborhood e.g. '1970s West Hollywood 1BR, hardwood floors, casement windows'",
    "architecture_details": "SPECIFIC e.g. 'white plaster walls, wood window frames painted cream, 8ft ceilings'",
    "key_objects": [
      {{"item": "SPECIFIC NAMED OBJECT with brand e.g. 'HAY Mags Soft sofa in dusty rose Linara'", "placement": "where in frame", "acquisition_story": "how they got it"}},
      {{"item": "SECOND SPECIFIC OBJECT", "placement": "location", "acquisition_story": "provenance"}},
      {{"item": "THIRD SPECIFIC OBJECT", "placement": "location", "acquisition_story": "provenance"}}
    ],
    "oops_item": {{
      "item": "ONE casual imperfect detail e.g. 'half-drunk Erewhon smoothie'",
      "placement": "where",
      "why_its_there": "mundane reason"
    }},
    "lighting_source": "SPECIFIC e.g. 'west window with sheer linen, HAY PC pendant in corner'",
    "atmosphere": "one phrase e.g. 'lived-in but curated, late morning calm'"
  }},
  "base_outfit_neutral": {{
    "top": "SPECIFIC brand + style + color + fit e.g. 'Skims Fits Everybody tank in Sienna, loose fit'",
    "bottom": "SPECIFIC e.g. 'Levi's Ribcage Wide Leg in Tango Light, high-rise cropped'",
    "footwear": "SPECIFIC or 'barefoot, natural toenails'",
    "accessories": "SPECIFIC or 'none' e.g. 'Mejuri Bold Hoops gold vermeil, Apple Watch starlight band'",
    "outfit_logic": "why this makes sense e.g. 'Sunday morning, hasn't left yet, comfortable but selfie-ready'"
  }},
  "negative_constraints": ["no phone in hands", "no drink in hands", "no props in hands", "no camera UI", "no timestamps", "no airbrushed skin", "no catalog lighting", "no stiff posing", "no performative smile", "no depression markers", "no extra people", "hands empty and visible"]
}}'''

# ============================================================
# LLM & IMAGE GENERATION
# ============================================================

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
        gen_model = genai.GenerativeModel(model)
        response = gen_model.generate_content(prompt)
        return response.text

def generate_character_image(json_prompt, fal_key, resolution):
    """Generate character image - JSON is passed directly as prompt."""
    os.environ["FAL_KEY"] = fal_key
    res = RESOLUTION_OPTIONS[resolution]
    prompt_string = json.dumps(json_prompt, indent=2) if isinstance(json_prompt, dict) else json_prompt
    
    result = fal_client.subscribe(
        "fal-ai/nano-banana-pro",
        arguments={
            "prompt": prompt_string,
            "negative_prompt": "blurry, low quality, distorted, deformed, ugly, bad anatomy, bad hands, missing fingers, watermark, text, logo, UI elements, phone screen, camera interface, timestamp, battery icon, airbrushed skin, catalog lighting, stiff pose, fake smile, depression, sad, crying, gray skin, dark vignette",
            "image_size": {"width": res["width"], "height": res["height"]},
            "num_images": 1
        }
    )
    return result["images"][0]["url"]

# ============================================================
# MAIN APP
# ============================================================

def main():
    st.markdown('<div class="brand-mark"><span>✦</span> Synth.Human</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Character Creator</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Build a persistent character for your UGC videos.</div>', unsafe_allow_html=True)
    
    # API Configuration
    with st.expander("🔑 API Configuration", expanded=not st.session_state.get('api_configured', False)):
        col1, col2 = st.columns(2)
        with col1:
            fal_key = st.text_input("fal.ai API Key", type="password", placeholder="Enter your fal.ai key...")
            st.caption("[Get your key →](https://fal.ai/dashboard/keys)")
        with col2:
            llm_provider = st.selectbox("LLM Provider", ["OpenAI", "Anthropic (Claude)", "Google (Gemini)"])
        
        col3, col4 = st.columns(2)
        with col3:
            llm_key = st.text_input("LLM API Key", type="password", placeholder="Enter your LLM API key...")
        with col4:
            model_options = {
                "OpenAI": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4.1", "gpt-4.5-preview"],
                "Anthropic (Claude)": ["claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-3-5-sonnet-20241022"],
                "Google (Gemini)": ["gemini-2.0-flash", "gemini-2.0-pro", "gemini-1.5-pro"]
            }
            llm_model = st.selectbox("Model", model_options[llm_provider])
        
        resolution = st.selectbox("Image Resolution", list(RESOLUTION_OPTIONS.keys()), index=0)
        st.caption("Higher resolution = better quality but slower and more expensive")
        
        if fal_key and llm_key:
            st.session_state.api_configured = True
            st.session_state.fal_key = fal_key
            st.session_state.llm_key = llm_key
            st.session_state.llm_provider = {"OpenAI": "openai", "Anthropic (Claude)": "anthropic", "Google (Gemini)": "google"}[llm_provider]
            st.session_state.llm_model = llm_model
            st.session_state.resolution = resolution
            st.success("✓ API keys configured")
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Subcultures
    st.markdown('<p class="section-header">Subcultures — Select up to 3</p>', unsafe_allow_html=True)
    
    col_search, col_add = st.columns([3, 1])
    with col_search:
        custom_input = st.text_input("Search or add custom", placeholder="Type to search or add custom...", label_visibility="collapsed")
    with col_add:
        if st.button("+ Add Custom", use_container_width=True):
            if custom_input and custom_input not in st.session_state.selected_subcultures and len(st.session_state.selected_subcultures) < 3:
                st.session_state.selected_subcultures.append(custom_input)
                st.session_state.custom_subcultures.append(custom_input)
                st.rerun()
    
    if st.session_state.selected_subcultures:
        st.markdown("**Selected:**")
        cols = st.columns(len(st.session_state.selected_subcultures) + 1)
        for i, sub in enumerate(st.session_state.selected_subcultures):
            with cols[i]:
                if st.button(f"✕ {sub}", key=f"remove_{sub}"):
                    st.session_state.selected_subcultures.remove(sub)
                    if sub in st.session_state.custom_subcultures:
                        st.session_state.custom_subcultures.remove(sub)
                    st.rerun()
        remaining = 3 - len(st.session_state.selected_subcultures)
        if remaining > 0:
            with cols[len(st.session_state.selected_subcultures)]:
                st.caption(f"{remaining} remaining")
    
    for cat_key, cat_data in SUBCULTURES.items():
        filtered = [o for o in cat_data["options"] if not custom_input or custom_input.lower() in o.lower()]
        if not filtered:
            continue
        with st.expander(cat_data["label"]):
            cols = st.columns(5)
            for i, option in enumerate(filtered):
                with cols[i % 5]:
                    is_sel = option in st.session_state.selected_subcultures
                    if st.button(f"{'✓ ' if is_sel else ''}{option}", key=f"sub_{cat_key}_{option}", use_container_width=True):
                        if is_sel:
                            st.session_state.selected_subcultures.remove(option)
                        elif len(st.session_state.selected_subcultures) < 3:
                            st.session_state.selected_subcultures.append(option)
                        st.rerun()
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Demographics
    st.markdown('<p class="section-header">Demographics</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        tier = st.radio("Tier", ["Budget", "Mid", "Premium", "Luxury"], index=2)
    with col2:
        gender = st.radio("Gender", ["Female", "Male", "Non-binary"])
    with col3:
        age = st.slider("Age", 18, 38, 24)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Ethnicity
    st.markdown('<p class="section-header">Ethnicity</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        ethnicity_region = st.selectbox("Region", list(ETHNICITIES.keys()))
    with col2:
        ethnicity_specific = st.selectbox("Specific", ETHNICITIES[ethnicity_region])
    
    use_custom_eth = st.checkbox("Use custom ethnicity instead")
    if use_custom_eth:
        custom_eth = st.text_input("Custom ethnicity", placeholder='e.g., "Half Nigerian, half Korean"')
        ethnicity = custom_eth if custom_eth else ethnicity_specific
    else:
        ethnicity = ethnicity_specific
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Location
    st.markdown('<p class="section-header">Location</p>', unsafe_allow_html=True)
    st.markdown("**Popular:**")
    city_cols = st.columns(8)
    for i, city in enumerate(POPULAR_CITIES[:16]):
        with city_cols[i % 8]:
            if st.button(city, key=f"city_{city}", use_container_width=True):
                st.session_state.selected_city = city
                st.rerun()
    
    use_custom_loc = st.checkbox("Use custom location")
    if use_custom_loc:
        location = st.text_input("Custom location", placeholder='e.g., "Austin, Texas"')
        if not location:
            location = st.session_state.get('selected_city', 'Los Angeles')
    else:
        location = st.session_state.get('selected_city', 'Los Angeles')
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Summary
    subcultures_display = " + ".join(st.session_state.selected_subcultures) if st.session_state.selected_subcultures else "None selected"
    st.markdown(f'<div class="summary-bar"><strong>{subcultures_display}</strong> • {tier} • {age} • {gender} • {ethnicity} • {location}</div>', unsafe_allow_html=True)
    
    # Generate
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_clicked = st.button("✦ Generate Character", use_container_width=True, type="primary")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎲 Randomize All", use_container_width=True):
            import random
            all_subs = [opt for cat in SUBCULTURES.values() for opt in cat["options"]]
            st.session_state.selected_subcultures = random.sample(all_subs, random.randint(1, 3))
            st.session_state.selected_city = random.choice(POPULAR_CITIES)
            st.rerun()
    
    if generate_clicked:
        if not st.session_state.selected_subcultures:
            st.error("Please select at least one subculture.")
        elif not st.session_state.get('api_configured'):
            st.error("Please configure your API keys first.")
        else:
            config = {"subcultures": st.session_state.selected_subcultures, "tier": tier, "age": age, "gender": gender, "ethnicity": ethnicity, "location": location}
            
            with st.spinner("Generating character JSON..."):
                try:
                    prompt = get_character_prompt(config)
                    response = call_llm(prompt, st.session_state.llm_provider, st.session_state.llm_key, st.session_state.llm_model)
                    json_str = response.strip()
                    if "```json" in json_str:
                        json_str = json_str.split("```json")[1].split("```")[0]
                    elif "```" in json_str:
                        json_str = json_str.split("```")[1].split("```")[0]
                    character_data = json.loads(json_str.strip())
                    st.session_state.generated_character = character_data
                except Exception as e:
                    st.error(f"Error generating JSON: {str(e)}")
                    st.stop()
            
            with st.spinner("Generating image (JSON → Nano Banana Pro)..."):
                try:
                    image_url = generate_character_image(character_data, st.session_state.fal_key, st.session_state.resolution)
                    st.session_state.character_image_url = image_url
                except Exception as e:
                    st.error(f"Error generating image: {str(e)}")
                    st.stop()
            st.rerun()
    
    # Display results
    if st.session_state.generated_character and st.session_state.character_image_url:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<p class="section-header">Generated Character</p>', unsafe_allow_html=True)
        
        char = st.session_state.generated_character
        meta = char.get('meta', {})
        identity = char.get('identity_parameters', {})
        phys = identity.get('physicality_details', {})
        vibe = char.get('persona_vibe', {})
        env = char.get('environment_clutter', {})
        outfit = char.get('base_outfit_neutral', {})
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(st.session_state.character_image_url, use_container_width=True)
        with col2:
            st.markdown(f"### {meta.get('character_name', 'Character')}")
            st.markdown(f"*\"{meta.get('archetype_summary', '')}\"*")
            
            with st.expander("Identity", expanded=True):
                st.markdown(f"**Ethnicity:** {phys.get('ethnicity_heritage', 'N/A')}")
                st.markdown(f"**Skin:** {phys.get('skin_texture', 'N/A')}")
                st.markdown(f"**Hair:** {phys.get('hair_specification', 'N/A')}")
                st.markdown(f"**Features:** {phys.get('facial_features', 'N/A')}")
            
            with st.expander("Vibe"):
                st.markdown(f"**Expression:** {vibe.get('expression', 'N/A')}")
                st.markdown(f"**Energy:** {vibe.get('energy', 'N/A')}")
                st.markdown(f"**Posture:** {vibe.get('posture', 'N/A')}")
            
            with st.expander("Environment"):
                st.markdown(f"**Setting:** {env.get('setting', 'N/A')}")
                if env.get('key_objects'):
                    for obj in env['key_objects']:
                        st.markdown(f"- {obj.get('item', 'N/A')}")
            
            with st.expander("Outfit"):
                st.markdown(f"**Top:** {outfit.get('top', 'N/A')}")
                st.markdown(f"**Bottom:** {outfit.get('bottom', 'N/A')}")
                st.markdown(f"**Footwear:** {outfit.get('footwear', 'N/A')}")
            
            with st.expander("Full JSON"):
                st.json(char)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button("📥 Export JSON", json.dumps(char, indent=2).encode(), file_name=f"character_{meta.get('character_name', 'char').lower().replace(' ', '_')}.json", mime="application/json", use_container_width=True)
        with col2:
            img_resp = requests.get(st.session_state.character_image_url)
            st.download_button("🖼️ Download Image", img_resp.content, file_name=f"character_{meta.get('character_name', 'char').lower().replace(' ', '_')}.png", mime="image/png", use_container_width=True)
        with col3:
            if st.button("🎬 Use in UGC Generator", use_container_width=True):
                st.session_state.ugc_character = char
                st.session_state.ugc_character_image = st.session_state.character_image_url
                st.info("Character saved! Go to UGC Generator.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("↻ Regenerate", use_container_width=True):
                st.session_state.generated_character = None
                st.session_state.character_image_url = None
                st.rerun()

if __name__ == "__main__":
    main()
