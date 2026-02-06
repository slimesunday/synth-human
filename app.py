"""
Synth.Human — AI-Powered UGC Video Generator
Turn any product into viral influencer content in minutes.
"""

import streamlit as st
import fal_client
import json
import base64
import requests
import time
from PIL import Image
from io import BytesIO

# ============================================================
# PAGE CONFIG & CUSTOM CSS
# ============================================================

st.set_page_config(
    page_title="Synth.Human — AI UGC Video Generator",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Runway-inspired dark mode CSS
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global dark theme */
    .stApp {
        background: linear-gradient(180deg, #0a0a0a 0%, #111111 50%, #0d0d0d 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }
    ::-webkit-scrollbar-thumb {
        background: #333;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    
    /* Main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Hero title */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    /* Hero subtitle */
    .hero-subtitle {
        font-size: 1.25rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Brand mark */
    .brand-mark {
        font-size: 1.1rem;
        font-weight: 600;
        color: #fff;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 2rem;
    }
    
    .brand-mark span {
        color: #8b5cf6;
    }
    
    /* Glass card */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }
    
    .glass-card-header {
        font-size: 0.875rem;
        font-weight: 500;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
    }
    
    /* Upload area */
    .upload-area {
        border: 2px dashed rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 3rem 2rem;
        text-align: center;
        background: rgba(139, 92, 246, 0.05);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .upload-area:hover {
        border-color: rgba(139, 92, 246, 0.6);
        background: rgba(139, 92, 246, 0.1);
    }
    
    .upload-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .upload-text {
        color: #888;
        font-size: 0.95rem;
    }
    
    .upload-text strong {
        color: #8b5cf6;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #fff !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
    }
    
    .stTextInput > label {
        color: #888 !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox > label {
        color: #888 !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 14px rgba(139, 92, 246, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.5) !important;
    }
    
    /* Secondary button */
    .secondary-btn > button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: none !important;
    }
    
    .secondary-btn > button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        box-shadow: none !important;
    }
    
    /* Progress steps */
    .progress-container {
        display: flex;
        justify-content: space-between;
        margin: 2rem 0;
        position: relative;
    }
    
    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        position: relative;
    }
    
    .step-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        color: #666;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .step-circle.active {
        background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
        border-color: #8b5cf6;
        color: white;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
    }
    
    .step-circle.completed {
        background: #22c55e;
        border-color: #22c55e;
        color: white;
    }
    
    .step-label {
        font-size: 0.75rem;
        color: #666;
        text-align: center;
    }
    
    .step-label.active {
        color: #8b5cf6;
    }
    
    /* Divider */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        margin: 2rem 0;
    }
    
    /* Status message */
    .status-message {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem;
        background: rgba(139, 92, 246, 0.1);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 8px;
        color: #a78bfa;
        font-size: 0.9rem;
    }
    
    /* Result card */
    .result-card {
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    
    /* Video container */
    .video-container {
        border-radius: 12px;
        overflow: hidden;
        background: #000;
        aspect-ratio: 9/16;
        max-width: 300px;
        margin: 0 auto;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #444;
        font-size: 0.8rem;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 8px !important;
        color: #888 !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        color: #888;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(139, 92, 246, 0.2) !important;
        color: #8b5cf6 !important;
        border-color: #8b5cf6 !important;
    }
    
    /* Image preview */
    .image-preview {
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        overflow: hidden;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #8b5cf6 !important;
    }
    
    /* Info/warning boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    
    /* File uploader */
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 2px dashed rgba(139, 92, 246, 0.3) !important;
        border-radius: 12px !important;
    }
    
    .stFileUploader > div > div:hover {
        border-color: rgba(139, 92, 246, 0.6) !important;
    }
    
    /* Section headers */
    .section-header {
        font-size: 0.75rem;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    /* Glow effect */
    .glow {
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from {
            box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
        }
        to {
            box-shadow: 0 0 30px rgba(139, 92, 246, 0.6);
        }
    }
    
    /* Hide file uploader label */
    .stFileUploader > label {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if 'step' not in st.session_state:
    st.session_state.step = 1
if 'product_image' not in st.session_state:
    st.session_state.product_image = None
if 'result' not in st.session_state:
    st.session_state.result = None
if 'api_configured' not in st.session_state:
    st.session_state.api_configured = False


# ============================================================
# PROMPTS
# ============================================================

def get_persona_inference_prompt(advertiser_controls):
    return f'''You are a high-fidelity brand intelligence and subculture-mapping engine. Your goal is to look at a product and reverse-engineer the "Social Media Truth" of who owns it and where they post it.

INPUT
A PRODUCT IMAGE (e.g., footwear, apparel, accessory, beauty, food, tech, home goods - any product).

ADVERTISER CONTROLS (if provided):
{advertiser_controls}

YOUR TASK
Analyze the product for material quality, design language, and cultural signifiers. Infer a persona that is not just a demographic, but a "vibe" that would go viral on TikTok or Instagram. If advertiser controls are provided, use them to shape or override your inference.

OUTPUT FORMAT (STRICT JSON)
Return ONLY a valid JSON object. No markdown code blocks. No intro text. Just the raw JSON.

{{
  "brand_analysis": {{
    "brand_name": "string or null",
    "brand_tier": "budget | mid | premium | luxury",
    "aesthetic_core": "the specific subculture name",
    "cultural_associations": ["list", "of", "micro-trends"],
    "market_positioning": "why this product is cool right now"
  }},
  "buyer_persona": {{
    "age": 25,
    "gender_presentation": "male | female | non-binary",
    "physical_identity_signals": {{
      "ethnicity": "specific ethnic background for visual representation",
      "style_archetype": "e.g., Berlin Techno-Minimalist or SoCal Wellness Influencer",
      "hair_vibe": "texture and style description",
      "skin_undertone": "e.g., warm honey, cool espresso, fair with freckles"
    }},
    "personality": "one-sentence psychological profile",
    "income_bracket": "low | mid | upper-middle | high"
  }},
  "viral_context": {{
    "platform": "TikTok | Instagram",
    "scene_location": "specific residential interior location",
    "lighting_profile": "e.g., golden hour hazy backlight",
    "camera_feel": "e.g., iPhone propped on desk, low angle looking up"
  }}
}}'''


def get_character_builder_prompt(persona_json_str):
    return f'''You are the Character Architect for UGC video generation. Your job is to turn abstract persona data into a concrete, photorealistic human being who is ready to film UGC content.

INPUT
PERSONA JSON from the inference engine:
{persona_json_str}

YOUR TASK
Generate a detailed image prompt for creating a photorealistic character sitting in their home, ready to film content. The character must have NO products or props in their hands.

CRITICAL REQUIREMENTS

CAMERA ANGLE (CRITICAL):
- Phone propped on a surface at waist-to-chest height
- Camera angled UPWARD toward the subject's face
- Subject is looking DOWN at the camera
- This is the classic "phone on desk" UGC angle

SUBJECT POSITION:
- SEATED: on bed edge, chair, couch, or perched on furniture
- Upper body upright with slight forward lean toward camera
- Chest-up or waist-up framing
- Face fully visible, engaged with camera

HANDS (CRITICAL):
- Hands MUST be empty and visible
- Relaxed position: on lap, resting on surface, or lightly clasped
- NO phones, drinks, products, or any objects in hands

EXPRESSION:
- "About to say something" energy
- Engaged, warm, slight smile or mouth slightly open
- Direct eye contact with camera lens

OUTPUT FORMAT
Return ONLY the image generation prompt as a single paragraph (100-150 words). No JSON. No explanation. No markdown.'''


def get_first_last_frame_prompt(product_name, persona_summary):
    return f'''You generate exactly TWO image prompts for UGC-style video generation.

INPUTS
1. CHARACTER REFERENCE: A person in their environment (already generated)
2. PRODUCT: {product_name}
3. PERSONA CONTEXT: {persona_summary}

THE VIBE
This is "let me tell you about this product" content. The subject is ALREADY holding the product in both frames.

- FIRST FRAME: Product in hand but held casually at chest level, "about to say something" energy
- LAST FRAME: Product brought close to camera, tilted to show detail, "look at this" moment

NO unboxing. NO reaching for product. Product is IN HAND from frame one.

OUTPUT FORMAT (STRICT)
Output EXACTLY two prompts. Each starts with * on a new line. No titles, labels, or explanations.

Each prompt must:
1. Open with: "Using the provided character reference for face, body, room, and lighting consistency."
2. Describe the specific pose, expression, product position
3. Be under 120 words'''


def get_veo_script_prompt(product_name, persona_summary, campaign_tone, script_override, tone_instructions):
    return f'''You are a UGC script writer for viral TikTok/Instagram content.

INPUTS
- Product: {product_name}
- Persona: {persona_summary}
- Campaign Tone: {campaign_tone}
- Custom Script (if provided): {script_override}

YOUR TASK
Generate a single Veo prompt describing the visual scene and spoken dialogue (4-5 sentences).

DIALOGUE STYLE
{tone_instructions}

DIALOGUE RULES
- 4-5 short, casual sentences
- Include filler words naturally ("like", "literally", "okay so")
- Mention the product naturally but NO specific claims
- No calls to action
- Match accent/speech to persona geography

OUTPUT FORMAT
Return ONLY the Veo prompt as a single paragraph. No JSON. No markdown.

Structure: "[Character description] is filming a UGC style TikTok in their [room], speaking naturally to camera. [Setting]. [Mannerisms]. They say: [dialogue]. [Final product moment]."'''


# ============================================================
# LLM WRAPPER
# ============================================================

def call_llm(prompt, image_base64=None, provider="openai", api_key=None, model=None):
    """Call the selected LLM provider."""
    
    if provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        messages = []
        if image_base64:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            })
        else:
            messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model or "gpt-4o",
            messages=messages,
            max_tokens=2000
        )
        return response.choices[0].message.content
    
    elif provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        content = []
        if image_base64:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_base64
                }
            })
        content.append({"type": "text", "text": prompt})
        
        response = client.messages.create(
            model=model or "claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": content}]
        )
        return response.content[0].text
    
    elif provider == "google":
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        gen_model = genai.GenerativeModel(model or 'gemini-2.0-flash')
        
        if image_base64:
            image_data = base64.b64decode(image_base64)
            image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
            response = gen_model.generate_content([prompt, image_parts[0]])
        else:
            response = gen_model.generate_content(prompt)
        
        return response.text


# ============================================================
# IMAGE/VIDEO GENERATION
# ============================================================

def generate_image(prompt, reference_urls=None, fal_key=None):
    """Generate image using Nano Banana Pro."""
    import os
    os.environ["FAL_KEY"] = fal_key
    
    if reference_urls:
        result = fal_client.subscribe(
            "fal-ai/nano-banana-pro/edit",
            arguments={
                "prompt": prompt,
                "image_urls": reference_urls,
                "aspect_ratio": "9:16",
                "num_images": 1
            }
        )
    else:
        result = fal_client.subscribe(
            "fal-ai/nano-banana-pro",
            arguments={
                "prompt": prompt,
                "aspect_ratio": "9:16",
                "num_images": 1
            }
        )
    
    return result["images"][0]["url"]


def generate_video(first_frame_url, last_frame_url, prompt, fal_key):
    """Generate video using Veo 3.1."""
    import os
    os.environ["FAL_KEY"] = fal_key
    
    result = fal_client.subscribe(
        "fal-ai/veo3.1/fast/first-last-frame-to-video",
        arguments={
            "first_frame_url": first_frame_url,
            "last_frame_url": last_frame_url,
            "prompt": prompt,
            "duration": "8s",
            "aspect_ratio": "9:16",
            "generate_audio": True
        }
    )
    
    return result["video"]["url"]


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline(product_image_bytes, config, fal_key, llm_provider, llm_key, llm_model, progress_callback=None):
    """Run the full UGC video generation pipeline."""
    
    results = {}
    
    # Encode product image
    product_image_b64 = base64.b64encode(product_image_bytes).decode('utf-8')
    
    # Upload product image to fal
    if progress_callback:
        progress_callback("Uploading product image...", 0.05)
    
    import os
    os.environ["FAL_KEY"] = fal_key
    product_image_url = fal_client.upload(product_image_bytes, content_type="image/jpeg")
    
    # ----- NODE 1: Persona Inference -----
    if progress_callback:
        progress_callback("Analyzing product & inferring persona...", 0.15)
    
    controls = []
    if config.get('target_age_range'):
        controls.append(f"- Target age range: {config['target_age_range']}")
    if config.get('target_gender'):
        controls.append(f"- Target gender: {config['target_gender']}")
    if config.get('target_geography'):
        controls.append(f"- Target geography: {config['target_geography']}")
    if config.get('target_ethnicity'):
        controls.append(f"- Target ethnicity: {config['target_ethnicity']}")
    if config.get('subculture'):
        controls.append(f"- Subculture/aesthetic: {config['subculture']}")
    if config.get('campaign_tone'):
        controls.append(f"- Campaign tone: {config['campaign_tone']}")
    
    controls_str = "\n".join(controls) if controls else "None provided - infer everything from the product."
    
    persona_prompt = get_persona_inference_prompt(controls_str)
    persona_response = call_llm(persona_prompt, image_base64=product_image_b64, 
                                 provider=llm_provider, api_key=llm_key, model=llm_model)
    
    # Parse JSON
    try:
        json_str = persona_response.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]
        persona_json = json.loads(json_str.strip())
    except:
        persona_json = {
            "brand_analysis": {"brand_tier": "mid", "aesthetic_core": "contemporary casual"},
            "buyer_persona": {
                "age": 25,
                "gender_presentation": "female",
                "physical_identity_signals": {
                    "ethnicity": "mixed",
                    "style_archetype": "Urban Creative",
                    "hair_vibe": "natural texture, shoulder length",
                    "skin_undertone": "warm"
                }
            },
            "viral_context": {
                "scene_location": "bedroom",
                "lighting_profile": "soft natural window light"
            }
        }
    
    results['persona'] = persona_json
    
    # ----- NODE 2: Character Builder -----
    if progress_callback:
        progress_callback("Building character profile...", 0.25)
    
    character_prompt = get_character_builder_prompt(json.dumps(persona_json, indent=2))
    character_image_prompt = call_llm(character_prompt, provider=llm_provider, api_key=llm_key, model=llm_model)
    character_image_prompt = character_image_prompt.strip().strip('"').strip("'")
    
    # ----- Generate Character Image -----
    if progress_callback:
        progress_callback("Generating character image...", 0.35)
    
    character_image_url = generate_image(character_image_prompt, fal_key=fal_key)
    results['character_image_url'] = character_image_url
    
    # ----- NODE 3: First/Last Frame Prompts -----
    if progress_callback:
        progress_callback("Creating frame compositions...", 0.45)
    
    persona_summary = f"{persona_json.get('buyer_persona', {}).get('physical_identity_signals', {}).get('style_archetype', 'Influencer')}, {persona_json.get('buyer_persona', {}).get('age', '25')} years old"
    
    frame_prompt = get_first_last_frame_prompt(config['product_name'], persona_summary)
    frame_response = call_llm(frame_prompt, provider=llm_provider, api_key=llm_key, model=llm_model)
    
    frame_parts = frame_response.split('*')
    frame_parts = [p.strip() for p in frame_parts if p.strip()]
    
    if len(frame_parts) >= 2:
        first_frame_prompt = frame_parts[0]
        last_frame_prompt = frame_parts[1]
    else:
        first_frame_prompt = f"Using the provided character reference. Subject seated, holding {config['product_name']} casually at chest level, engaged expression, about to speak."
        last_frame_prompt = f"Using the provided character reference. Subject holding {config['product_name']} toward camera, tilted to show detail, enthusiastic expression."
    
    # ----- Generate Frame Images -----
    if progress_callback:
        progress_callback("Generating first frame...", 0.55)
    
    first_frame_url = generate_image(first_frame_prompt, reference_urls=[character_image_url, product_image_url], fal_key=fal_key)
    results['first_frame_url'] = first_frame_url
    
    if progress_callback:
        progress_callback("Generating last frame...", 0.65)
    
    last_frame_url = generate_image(last_frame_prompt, reference_urls=[character_image_url, product_image_url], fal_key=fal_key)
    results['last_frame_url'] = last_frame_url
    
    # ----- NODE 4: Veo Script -----
    if progress_callback:
        progress_callback("Writing video script...", 0.75)
    
    tone = config.get('campaign_tone') or 'playful'
    tone_map = {
        'playful': 'Humorous, slightly ironic, self-aware. Example: "okay the secret is literally this thing..."',
        'aspirational': 'Confident, "this elevated my routine" energy.',
        'relatable': 'Warm, "I am just like you" discovery energy.',
        'edgy': 'Nonchalant, "idk why everyone sleeps on this" cool energy.',
        'wholesome': 'Genuine excitement, sharing with friends energy.'
    }
    tone_instructions = tone_map.get(tone.lower(), tone_map['playful'])
    
    script_override = config.get('script_override') or 'None - generate based on tone'
    
    veo_prompt = get_veo_script_prompt(config['product_name'], persona_summary, tone, script_override, tone_instructions)
    veo_script = call_llm(veo_prompt, provider=llm_provider, api_key=llm_key, model=llm_model)
    veo_script = veo_script.strip().strip('"')
    results['script'] = veo_script
    
    # ----- Generate Video -----
    if progress_callback:
        progress_callback("Generating video (this takes 1-3 min)...", 0.85)
    
    video_url = generate_video(first_frame_url, last_frame_url, veo_script, fal_key)
    results['video_url'] = video_url
    
    if progress_callback:
        progress_callback("Complete!", 1.0)
    
    return results


# ============================================================
# UI COMPONENTS
# ============================================================

def render_header():
    """Render the header/brand."""
    st.markdown("""
    <div class="brand-mark">
        <span>✦</span> Synth.Human
    </div>
    """, unsafe_allow_html=True)


def render_hero():
    """Render the hero section."""
    st.markdown("""
    <div class="hero-title">Turn Products Into Viral UGC</div>
    <div class="hero-subtitle">AI-powered influencer videos in minutes. No actors. No studio. Just upload.</div>
    """, unsafe_allow_html=True)


def render_progress_steps(current_step):
    """Render the progress steps."""
    steps = ["Configure", "Upload", "Generate", "Download"]
    
    cols = st.columns(4)
    for i, (col, step) in enumerate(zip(cols, steps), 1):
        with col:
            if i < current_step:
                status = "completed"
                icon = "✓"
            elif i == current_step:
                status = "active"
                icon = str(i)
            else:
                status = ""
                icon = str(i)
            
            st.markdown(f"""
            <div style="text-align: center;">
                <div class="step-circle {status}">{icon}</div>
                <div class="step-label {status}">{step}</div>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# MAIN APP
# ============================================================

def main():
    render_header()
    render_hero()
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Progress steps
    render_progress_steps(st.session_state.step)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Main content
    if st.session_state.step == 1:
        # ===== STEP 1: API CONFIGURATION =====
        st.markdown('<p class="section-header">🔑 API Configuration</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**fal.ai Key** (for image/video generation)")
            fal_key = st.text_input("fal.ai API Key", type="password", label_visibility="collapsed", 
                                     placeholder="Enter your fal.ai key...")
            st.caption("[Get your key →](https://fal.ai/dashboard/keys)")
        
        with col2:
            st.markdown("**LLM Provider**")
            llm_provider = st.selectbox("Provider", ["OpenAI", "Anthropic (Claude)", "Google (Gemini)"], 
                                        label_visibility="collapsed")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("**LLM API Key**")
            llm_key = st.text_input("LLM API Key", type="password", label_visibility="collapsed",
                                    placeholder="Enter your LLM API key...")
            
            provider_links = {
                "OpenAI": "[Get key →](https://platform.openai.com/api-keys)",
                "Anthropic (Claude)": "[Get key →](https://console.anthropic.com/)",
                "Google (Gemini)": "[Get key →](https://aistudio.google.com/app/apikey)"
            }
            st.caption(provider_links[llm_provider])
        
        with col4:
            st.markdown("**Model**")
            
            model_options = {
                "OpenAI": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4.1", "gpt-4.5-preview"],
                "Anthropic (Claude)": ["claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-3-5-sonnet-20241022"],
                "Google (Gemini)": ["gemini-2.0-flash", "gemini-2.0-pro", "gemini-1.5-pro"]
            }
            
            llm_model = st.selectbox("Model", model_options[llm_provider], label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Continue →", use_container_width=True):
            if fal_key and llm_key:
                st.session_state.fal_key = fal_key
                st.session_state.llm_key = llm_key
                st.session_state.llm_provider = {"OpenAI": "openai", "Anthropic (Claude)": "anthropic", "Google (Gemini)": "google"}[llm_provider]
                st.session_state.llm_model = llm_model
                st.session_state.api_configured = True
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Please enter both API keys to continue.")
    
    elif st.session_state.step == 2:
        # ===== STEP 2: UPLOAD & CONFIGURE =====
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<p class="section-header">📸 Product Image</p>', unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader("Upload", type=['png', 'jpg', 'jpeg', 'webp'], 
                                             label_visibility="collapsed")
            
            if uploaded_file:
                st.session_state.product_image = uploaded_file.read()
                img = Image.open(BytesIO(st.session_state.product_image))
                st.image(img, use_container_width=True)
        
        with col2:
            st.markdown('<p class="section-header">⚙️ Configuration</p>', unsafe_allow_html=True)
            
            product_name = st.text_input("Product Name", placeholder="e.g., Nike Dunk Low")
            
            campaign_tone = st.selectbox("Tone", ["Playful/Humorous", "Aspirational", "Relatable", "Edgy", "Wholesome"])
            
            with st.expander("Advanced Options"):
                target_age = st.text_input("Target Age Range", placeholder="e.g., 18-25")
                target_gender = st.selectbox("Target Gender", ["Any", "Male", "Female", "Non-binary"])
                target_geography = st.text_input("Target Geography", placeholder="e.g., Los Angeles")
                target_ethnicity = st.text_input("Target Ethnicity", placeholder="e.g., East Asian (or leave blank)")
                subculture = st.text_input("Subculture/Aesthetic", placeholder="e.g., clean girl, gorpcore")
                script_override = st.text_area("Custom Script (optional)", placeholder="Leave blank to auto-generate...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_back, col_next = st.columns([1, 3])
        with col_back:
            if st.button("← Back", use_container_width=True, key="back_btn"):
                st.session_state.step = 1
                st.rerun()
        
        with col_next:
            if st.button("🚀 Generate Video", use_container_width=True, type="primary"):
                if not st.session_state.product_image:
                    st.error("Please upload a product image.")
                elif not product_name:
                    st.error("Please enter a product name.")
                else:
                    # Store config
                    st.session_state.config = {
                        "product_name": product_name,
                        "campaign_tone": campaign_tone.split("/")[0].lower(),
                        "target_age_range": target_age if target_age else None,
                        "target_gender": None if target_gender == "Any" else target_gender.lower(),
                        "target_geography": target_geography if target_geography else None,
                        "target_ethnicity": target_ethnicity if target_ethnicity else None,
                        "subculture": subculture if subculture else None,
                        "script_override": script_override if script_override else None
                    }
                    st.session_state.step = 3
                    st.rerun()
    
    elif st.session_state.step == 3:
        # ===== STEP 3: GENERATING =====
        st.markdown('<p class="section-header">🎬 Generating Your Video</p>', unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        preview_cols = st.columns(4)
        preview_placeholders = {
            'persona': preview_cols[0].empty(),
            'character': preview_cols[1].empty(),
            'first_frame': preview_cols[2].empty(),
            'last_frame': preview_cols[3].empty()
        }
        
        def update_progress(message, progress):
            status_text.markdown(f"""
            <div class="status-message">
                <span>⏳</span> {message}
            </div>
            """, unsafe_allow_html=True)
            progress_bar.progress(progress)
        
        try:
            result = run_pipeline(
                st.session_state.product_image,
                st.session_state.config,
                st.session_state.fal_key,
                st.session_state.llm_provider,
                st.session_state.llm_key,
                st.session_state.llm_model,
                progress_callback=update_progress
            )
            
            st.session_state.result = result
            st.session_state.step = 4
            st.rerun()
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            if st.button("← Try Again"):
                st.session_state.step = 2
                st.rerun()
    
    elif st.session_state.step == 4:
        # ===== STEP 4: RESULTS =====
        result = st.session_state.result
        
        st.markdown("""
        <div class="result-card">
            <h2 style="color: #22c55e; margin-bottom: 0.5rem;">✓ Video Generated!</h2>
            <p style="color: #666;">Your UGC video is ready to download.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Video preview
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.video(result['video_url'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Download button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Download video
            video_response = requests.get(result['video_url'])
            video_bytes = video_response.content
            
            st.download_button(
                label="📥 Download Video",
                data=video_bytes,
                file_name=f"synth_human_{st.session_state.config['product_name'].replace(' ', '_')}.mp4",
                mime="video/mp4",
                use_container_width=True
            )
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Show generated assets
        with st.expander("View Generated Assets"):
            asset_cols = st.columns(3)
            
            with asset_cols[0]:
                st.caption("Character")
                st.image(result['character_image_url'], use_container_width=True)
            
            with asset_cols[1]:
                st.caption("First Frame")
                st.image(result['first_frame_url'], use_container_width=True)
            
            with asset_cols[2]:
                st.caption("Last Frame")
                st.image(result['last_frame_url'], use_container_width=True)
        
        with st.expander("View Script"):
            st.code(result['script'], language=None)
        
        with st.expander("View Persona"):
            st.json(result['persona'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("← Generate Another", use_container_width=True):
            st.session_state.step = 2
            st.session_state.result = None
            st.session_state.product_image = None
            st.rerun()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Synth.Human — AI-Powered UGC Generation</p>
        <p style="font-size: 0.7rem; margin-top: 0.5rem;">Powered by fal.ai • Nano Banana Pro • Veo 3.1</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
