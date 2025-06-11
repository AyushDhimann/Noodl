import json
import base64
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from app import text_model, logger
import google.generativeai as genai


def _call_gemini_with_retry(prompt, retries=3, delay=5):
    """A wrapper to call the Gemini API with retry logic."""
    for attempt in range(retries):
        try:
            response = text_model.generate_content(prompt)
            if response.text:
                cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
                json.loads(cleaned_response)  # Validate JSON before returning
                return cleaned_response
            else:
                raise ValueError("AI returned an empty response.")
        except Exception as e:
            logger.warning(f"AI: API call attempt {attempt + 1}/{retries} failed: {e}")
            if attempt + 1 == retries:
                logger.error("AI: All retry attempts failed.")
                raise
            time.sleep(delay)
    raise Exception("AI: Generation failed after all retries.")


def classify_topic_intent(topic):
    """Classifies the user's topic as either 'learn' or 'help'."""
    logger.info(f"AI: Classifying intent for topic: '{topic}'")
    prompt = f"""
    You are an intelligent assistant that categorizes user requests into one of two types: 'learn' or 'help'.
    Your analysis must be accurate to ensure the user gets the right kind of content.

    - 'learn': Choose this if the user wants to acquire a broad skill or comprehensive knowledge on a subject. These are typically complex topics that require a structured course.
      Examples: "History of Japan", "How to code a websocket in Python", "Learn to play the guitar", "Introduction to Quantum Mechanics".

    - 'help': Choose this if the user has a specific, practical, real-world problem and needs a direct, step-by-step solution or a 'how-to' guide. These are often immediate needs.
      Examples: "How do I put the zip back in the zipper of my bag?", "My phone won't turn on", "How to fix a leaky faucet", "How to tie a tie".

    Analyze the following topic: "{topic}"

    The output MUST be a single, valid JSON object with one key: "intent". The value must be either "learn" or "help".
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['intent']


def get_embedding(text):
    """Generates a vector embedding for a given text."""
    logger.info(f"AI: Generating embedding for text: '{text[:30]}...'")
    result = genai.embed_content(model="models/embedding-001", content=text)
    return result['embedding']


def rephrase_topic_with_emoji(topic):
    """Asks the AI to rephrase a topic into a course title and add a relevant emoji."""
    logger.info(f"AI: Rephrasing topic: '{topic}'")
    prompt = f"""
    You are a creative curriculum designer. A user has provided the topic "{topic}".
    Your task is to rephrase this topic into a more engaging and professional course title using simple English.
    Then, you MUST prepend a single, relevant emoji to the beginning of the new title.
    The output MUST be a single, valid JSON object with one key: "new_title".
    Do not include any text outside of the JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['new_title']


def generate_path_description(topic_title):
    """Generates an engaging, frontend-ready description for the learning path."""
    logger.info(f"AI: Generating description for topic: '{topic_title}'")
    prompt = f"""
    You are a curriculum writer for a learning app. Your goal is to write descriptions for a course titled "{topic_title}".
    You must use simple English, suitable for a global audience.

    Your task is to generate two distinct descriptions:
    1. A "short_description": A very brief, one-sentence summary. It must be a maximum of 20 words.
    2. A "long_description": A more detailed paragraph. It should give an overview of what the user will learn across the different levels of the course. It must be a maximum of 80 words.

    The output MUST be a single, valid JSON object with two keys: "short_description" and "long_description".
    Do not include any text outside of the JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)


def generate_learn_curriculum(topic, country=None):
    """Asks AI to generate a dynamic curriculum for a 'learn' intent."""
    logger.info(f"AI: Generating 'learn' curriculum for topic: '{topic}' with country context: {country}")
    country_context = f"The user is from {country}, so you can use local examples or spellings if relevant, but it's not a requirement." if country else ""
    prompt = f"""You are an expert curriculum designer for a learning app. For the course titled "{topic}", create a detailed syllabus using simple English. The goal is to take a user from beginner to competent. {country_context}

    The output MUST be a single, valid JSON object with one key: "levels". "levels" should be an array of strings, where each string is a concise title for a learning level. The titles should represent a logical progression.

    IMPORTANT: The number of levels should be appropriate for the topic's complexity.
    - For simple, everyday topics (e.g., 'how to brush your teeth'), use 3-4 levels.
    - For complex, academic, or broad topics (e.g., 'The History of the Renaissance'), use 7-10 levels.

    Do not include any text outside of the JSON object. Also make sure the title of each level starts with a single, appropriate emoji."""
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['levels']


def generate_help_curriculum(topic):
    """Generates a step-by-step guide for a 'help' intent."""
    logger.info(f"AI: Generating 'help' curriculum for topic: '{topic}'")
    prompt = f"""You are a helpful and clear technical writer. A user needs help with: "{topic}".
    Your task is to break down the solution into a series of simple, actionable steps. These steps will become the titles of a short guide.
    Use simple, encouraging language. The titles should be very clear, like a checklist.
    For example, for a topic like 'How to change a flat tire', the steps might be: ["1. Park Safely and Gather Tools", "2. Loosen the Lug Nuts", "3. Jack Up the Car", "4. Replace the Tire", "5. Lower the Car and Tighten"].

    The output MUST be a single, valid JSON object with one key: "levels". "levels" should be an array of strings, where each string is a step in the process.
    Do not include any text outside of the JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['levels']


def generate_learn_level_content(topic, level_title):
    """Generates rich, interleaved content for a single 'learn' level."""
    logger.info(f"AI: Generating 'learn' content for level: '{level_title}'")
    # FIX: Updated prompt for mobile-friendliness and flexible quiz inclusion.
    prompt = f"""
    You are an expert educator creating a lesson for a mobile learning app. The main course is "{topic}", and this specific lesson is "{level_title}".
    Your task is to create an interleaved learning experience optimized for a small screen.

    The output MUST be a single, valid JSON object with one key: "items". "items" must be an array of objects. Each object must have a "type" ('slide' or 'quiz') and a "content" field.

    **Content Guidelines:**
    1.  **Mobile First:** Keep paragraphs short (2-3 sentences). Use markdown `### Subheadings`, `**bold**`, and bullet points (`* item`) to break up text and make it easy to read on a phone.
    2.  **Multiple Slides:** A good level should have multiple slides. Explain a concept over 2-3 slides before checking for understanding. A typical level should have 5-8 items in total.
    3.  **Flexible Quizzes:** Quizzes are great but not mandatory for every single concept. Include a quiz only when it makes sense to test a key piece of knowledge. If a concept is simple, a few clear slides are enough.

    **'slide' item format:**
    - "content" should be a string with detailed, informative markdown in simple English.

    **'quiz' item format:**
    - "content" should be a JSON object with four keys: "question" (string), "options" (array of 4 strings), "correctAnswerIndex" (integer 0-3), and "explanation" (string).
    - The "explanation" should provide deeper context or a fun fact.

    Generate the complete, mobile-friendly lesson for "{level_title}". Do not include any text outside of the main JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['items']


def generate_help_level_content(topic, step_title):
    """Generates a direct, helpful slide for a single 'help' step."""
    logger.info(f"AI: Generating 'help' content for step: '{step_title}'")
    prompt = f"""
    You are an expert guide creating one part of a 'how-to' manual for a mobile app. The user's main goal is "{topic}", and this specific step is "{step_title}".
    Your task is to write a clear, concise, and easy-to-follow explanation for this single step. Your tone must be supportive and non-patronizing.

    - Use simple English and short paragraphs for mobile readability.
    - Use markdown for formatting: `### Subheadings`, `**bold**` for emphasis on crucial actions, and numbered lists for any sub-steps.
    - Assume the user is smart but unfamiliar with this specific task. Avoid jargon where possible, or explain it simply if necessary.
    - The goal is to help the user successfully complete this one step.

    The output MUST be a single, valid JSON object with one key: "items".
    "items" must be an array containing a SINGLE object with "type": "slide" and "content": "your markdown explanation". Do not generate quizzes.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['items']


# FIX: New function for the "I'm Feeling Lucky" feature
def generate_random_topic():
    """Asks the AI to generate a single, random, interesting topic for a learning path."""
    logger.info("AI: Generating a random topic...")
    prompt = """
    You are a creative idea generator. Your task is to invent a single, interesting, and non-trivial topic for a short learning course.
    The topic should be something a curious person would want to learn, like a specific historical event, a scientific concept, a practical skill, or a philosophical idea or you are even open to give same questions to ask for help related something.

    Examples of good topics:
    - "The Great Emu War of 1932"
    - "How to Make a Perfect Sourdough Starter"
    - "An Introduction to Stoic Philosophy"
    - "The Science of Black Holes"
    - "How to Fix a Leaky Faucet"
    - "How to Organize Your Digital Life"
    - "How to Tie a Bowline Knot"

    The output MUST be a single, valid JSON object with one key: "topic".
    Do not include any text outside of the JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['topic']


def generate_nft_svg(title):
    """Generates a unique SVG image as a string using Gemini."""
    logger.info(f"AI: Generating SVG image for title: '{title}'")
    prompt = f"""Create a simple, abstract, and colorful SVG image representing learning about "{title}". The SVG must be 512x512 pixels. Use a dark background like #1a1a1a. Generate 3-5 random, colorful, overlapping geometric shapes (circles, rectangles). Use vibrant colors like #FF6B6B, #4ECDC4, #45B7D1. Add the text "Noodl Certificate" and "{title}" on separate lines with a light color like #FFFFFF. The output must be ONLY the SVG code, starting with <svg> and ending with </svg>. Do not add any other text or markdown."""
    try:
        response = text_model.generate_content(prompt)
        svg_code = response.text.strip().replace("```svg", "").replace("```", "")
        if not svg_code.startswith('<svg'):
            raise ValueError("AI did not return valid SVG")
        logger.info("AI: Successfully generated SVG.")
        return svg_code
    except Exception as e:
        logger.error(f"AI: Failed to generate NFT SVG, creating fallback image: {e}")
        img = Image.new('RGB', (512, 512), color='#1a1a1a')
        d = ImageDraw.Draw(img)
        try:
            title_font = ImageFont.truetype("DejaVuSans.ttf", 32)
            subtitle_font = ImageFont.truetype("DejaVuSans.ttf", 24)
        except IOError:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        d.text((256, 220), "Noodl Certificate", font=title_font, fill="#FFFFFF", anchor="ms")
        d.text((256, 260), title, font=subtitle_font, fill="#DDDDDD", anchor="ms")
        d.rectangle([(20, 20), (512 - 20, 512 - 20)], outline="#4ECDC4", width=5)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        png_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f'<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg"><image href="data:image/png;base64,{png_b64}" height="512" width="512"/></svg>'