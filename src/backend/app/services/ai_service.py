import json
import base64
import time
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
from app import text_model, logger
from app.config import config
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
    result = genai.embed_content(model=config.GEMINI_MODEL_EMBEDDING, content=text)
    return result['embedding']


def rephrase_topic_with_emoji(topic):
    """Asks the AI to rephrase a topic into a catchy, simple title."""
    logger.info(f"AI: Rephrasing topic into simple title: '{topic}'")
    prompt = f"""
    You are a curriculum expert who creates clear and simple course titles. A user has provided the topic "{topic}".
    Your task is to transform this into a simple, straightforward, and encouraging title.

    **RULES:**
    1.  Prepend a single, relevant emoji to the very beginning of the new title.
    2.  The title MUST be a single, simple sentence.
    3.  The title MUST NOT contain any colons (:). Keep it clean and direct.

    **Examples of good, simple titles:**
    - User Topic: "How to bake sourdough bread" -> "🍞 Bake Perfect Sourdough Bread at Home."
    - User Topic: "The History of Rome" -> "🏛️ Explore the Rise and Fall of the Roman Empire."
    - User Topic: "How to fix a leaky faucet" -> "💧 Learn to Fix Your Leaky Faucet in Minutes."
    - User Topic: "Introduction to Quantum Mechanics" -> "⚛️ Understand the Basics of Quantum Mechanics."

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
    prompt = f"""
    You are an expert educator creating a lesson for a mobile learning app. The main course is "{topic}", and this specific lesson is "{level_title}".
    Your task is to create an interleaved learning experience optimized for a small screen.

    The output MUST be a single, valid JSON object with one key: "items". "items" must be an array of objects. Each object must have a "type" ('slide' or 'quiz') and a "content" field.

    **Content Guidelines:**
    1.  **STRICTLY Mobile First:** Keep paragraphs short (2-3 sentences). Use markdown `### Subheadings`, `**bold**`, and bullet points (`* item`) to break up text and make it easy to read on a phone.
    2.  **Multiple Slides:** A good level should have multiple slides. Explain a concept over a minimum of 3 slides before checking for understanding. A typical level should have 5-8 items in total.
    3.  **Flexible Quizzes:** Quizzes are great but not mandatory for every single concept. Include a quiz only when it makes sense to test a key piece of knowledge. If a concept is simple, a few clear slides are enough along with a basic quiz.

    **'slide' item format:**
    - "content" should be a string with detailed, informative markdown in simple English.

    **'quiz' item format:**
    - "content" should be a JSON object with four keys: "question" (string), "options" (array of 4 strings), "correctAnswerIndex" (integer 0-3), and "explanation" (string).
    - The "explanation" should provide deeper context or a fun fact, only one of .

    Generate the complete, mobile-friendly lesson for "{level_title}". Do not include any text outside of the main JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['items']


def generate_help_level_content(topic, step_title):
    """Generates rich, interleaved content for a single 'help' step."""
    logger.info(f"AI: Generating 'help' content for step: '{step_title}'")
    prompt = f"""
    You are an expert guide creating a helpful, interactive lesson for a mobile app. The user's main goal is "{topic}", and this specific step is "{step_title}".
    Your task is to create an interleaved learning experience to help the user master this step.

    The output MUST be a single, valid JSON object with one key: "items". "items" must be an array of objects. Each object must have a "type" ('slide' or 'quiz') and a "content" field.

    **Content Guidelines:**
    1.  **STRICTLY Mobile First:** Keep paragraphs short (2-3 sentences). Use markdown `### Subheadings`, `**bold**`, and bullet points (`* item`) to make it easy to read on a phone.
    2.  **Interleaved Content:** A good step-by-step guide should have multiple slides to explain the process clearly. A typical step should have 3-5 items in total.
    3.  **Check for Understanding:** Quizzes are a great way to ensure the user has understood a critical part of the step. Include a quiz if it makes sense to test a key piece of knowledge.

    **'slide' item format:**
    - "content" should be a string with a clear, concise, and easy-to-follow explanation for this single step. Use simple English.

    **'quiz' item format:**
    - "content" should be a JSON object with four keys: "question" (string), "options" (array of 4 strings), "correctAnswerIndex" (integer 0-3), and "explanation" (string).
    - The "explanation" should clarify why the answer is correct.

    Generate the complete, mobile-friendly lesson for "{step_title}". Do not include any text outside of the main JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['items']


def generate_random_topic():
    """Asks the AI to generate a single, random, interesting topic for a learning path."""
    logger.info("AI: Generating a random topic...")
    prompt = """
    You are a creative idea generator for a learning app. Your task is to invent a single, fun, and practical topic for a short course or a helpful guide.
    The goal is to be engaging and useful for everyday people, not a university lecture.

    **RULES:**
    1.  The topic should be a specific skill, a "how-to" question, or a fascinating concept explained simply.
    2.  Avoid overly academic, philosophical, or abstract topics like "The Epistemology of Knowledge" or "Post-structuralist critiques of...".
    3.  The topic should sound like something a real person would search for.

    **Examples of good, practical topics:**
    - "How to Make a Perfect Cup of Coffee"
    - "A Beginner's Guide to Investing in Stocks"
    - "How to Meal Prep for a Busy Week"
    - "What are the Northern Lights and How Can I See Them?"
    - "How to Change a Bicycle's Inner Tube"
    - "Simple Tricks to Improve Your Sleep Quality"
    - "How to Build a Simple Website with HTML and CSS"

    The output MUST be a single, valid JSON object with one key: "topic".
    Do not include any text outside of the JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['topic']


def generate_pixel_cert(title, path_id):
    """
    Generates a retro pixel-art certificate using Pillow, saves it locally,
    and returns the path to the file.
    """
    logger.info(f"IMAGE: Generating pixel certificate for path {path_id}: '{title}'")
    try:
        # --- Setup and Configuration ---
        scale = 10  # Each "pixel" will be 10x10 real pixels
        W, H = 64, 64  # Pixel dimensions
        IMG_W, IMG_H = W * scale, H * scale

        # --- Colors ---
        C_BLACK = (20, 20, 30)
        C_WHITE = (240, 240, 240)
        C_GOLD = (255, 215, 0)
        C_BLUE = (60, 80, 150)
        C_GREY = (100, 100, 120)

        # --- Create Image ---
        img = Image.new('RGB', (IMG_W, IMG_H), color=C_BLUE)
        d = ImageDraw.Draw(img)

        # --- Fonts (using a default monospace font for pixel effect) ---
        try:
            # Use a simple, clean font. If not available, Pillow's default will be used.
            font_main = ImageFont.truetype("cour.ttf", 11 * scale)
            font_title = ImageFont.truetype("cour.ttf", 6 * scale)
            font_small = ImageFont.truetype("cour.ttf", 4 * scale)
        except IOError:
            logger.warning("IMAGE: Courier font not found. Falling back to default.")
            font_main = ImageFont.load_default()
            font_title = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # --- Draw Certificate Elements ---
        # Border
        d.rectangle([(2 * scale, 2 * scale), (IMG_W - 2 * scale, IMG_H - 2 * scale)], fill=C_BLACK)
        d.rectangle([(3 * scale, 3 * scale), (IMG_W - 3 * scale, IMG_H - 3 * scale)], outline=C_GOLD, width=scale)

        # Header
        d.text((IMG_W / 2, 10 * scale), "CERTIFICATE", font=font_main, fill=C_GOLD, anchor="ms")
        d.text((IMG_W / 2, 16 * scale), "OF COMPLETION", font=font_small, fill=C_WHITE, anchor="ms")

        # Path Title
        wrapper = textwrap.TextWrapper(width=18) # Character width for pixel font
        wrapped_title = wrapper.wrap(text=title.upper())
        y_text = 24 * scale
        for line in wrapped_title:
            d.text((IMG_W / 2, y_text), line, font=font_title, fill=C_WHITE, anchor="mm")
            y_text += 7 * scale

        # Footer
        d.text((IMG_W / 2, H * scale - 10 * scale), "NOODL VERIFIED", font=font_small, fill=C_GOLD, anchor="ms")

        # --- Save the Image ---
        cert_dir = os.path.abspath("certificates")
        os.makedirs(cert_dir, exist_ok=True)
        file_path = os.path.join(cert_dir, f"path_{path_id}.png")

        img.save(file_path)
        logger.info(f"IMAGE: Successfully generated and saved pixel certificate to {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"IMAGE: Failed to generate pixel certificate for path {path_id}: {e}", exc_info=True)
        return None