import json
import base64
import time
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
from app import text_model, logger
from app.config import config
import google.generativeai as genai
from google.genai import types
import io


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

    **RULES:**
    1.  The output MUST be a single, valid JSON object with one key: "levels".
    2.  "levels" must be an array of strings.
    3.  Each string in the array is a concise title for a learning level.
    4.  Each title MUST start with a single, relevant emoji.
    5.  Each title MUST NOT start with a number (e.g., "1.", "2."). The numbering is handled automatically by the frontend.

    **IMPORTANT:** The number of levels should be appropriate for the topic's complexity.
    - For simple, everyday topics (e.g., 'how to brush your teeth'), use 3-4 levels.
    - For complex, academic, or broad topics (e.g., 'The History of the Renaissance'), use 7-10 levels.

    Do not include any text outside of the JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['levels']


def generate_help_curriculum(topic):
    """Generates a step-by-step guide for a 'help' intent."""
    logger.info(f"AI: Generating 'help' curriculum for topic: '{topic}'")
    prompt = f"""You are a helpful and clear technical writer. A user needs help with: "{topic}".
    Your task is to break down the solution into a series of simple, actionable steps. These steps will become the titles of a short guide.

    **RULES:**
    1.  The output MUST be a single, valid JSON object with one key: "levels".
    2.  "levels" must be an array of strings.
    3.  Each string is a step in the process, written in simple, encouraging language.
    4.  Each title MUST start with a single, relevant emoji.
    5.  Each title MUST NOT start with a number (e.g., "1.", "2.").

    **Example for 'How to change a flat tire':**
    - "🚗 Park Safely and Gather Tools"
    - "🔧 Loosen the Lug Nuts"
    - "⬆️ Jack Up the Car"
    - "🔄 Replace the Tire"
    - "⬇️ Lower the Car and Tighten"

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
    You are a viral content creator who is an expert at brainstorming edgy, hilarious, and genuinely useful ideas for a Gen Z audience.
    Your task is to invent a single, mind-blowing topic for a short course or a helpful guide. The tone should be modern, a little bit savage, and hyper-relevant to real-world situations.

    **RULES:**
    1.  **BE BOLD & UNEXPECTED**: Think outside the box. What's a skill or piece of knowledge that's surprisingly useful?
    2.  **GEN Z VIBE**: Use modern language. Topics can be funny, a bit sarcastic, or address modern life-hacks.
    3.  **PRACTICAL & ACTIONABLE**: The topic must be a specific skill, a "how-to" guide for a modern problem, or a fascinating concept explained simply.
    4.  **AVOID BORING STUFF**: No "History of Rome" or "How to knit a scarf". Think more "How to slide into DMs without being cringe" or "The Art of the Graceful Exit from an Awkward Conversation".

    **Examples of the VIBE we're looking for:**
    - "How to Win Any Argument Using Cold, Hard Logic (and a Little Bit of Sass)"
    - "The Art of the Side Hustle: Turn Your Weird Hobby into Actual Money"
    - "Adulting 101: How to Read a Rental Agreement Without Crying"
    - "Mastering the Art of the Polite 'No' to Protect Your Energy"
    - "How to Spot Red Flags on a First Date: A Field Guide"
    - "The Ultimate Guide to Thrifting and Finding Hidden Gems"
    - "How to Build a Killer Personal Website in One Weekend"
    - "Financial Glow-Up: Budgeting for People Who Hate Spreadsheets"

    The output MUST be a single, valid JSON object with one key: "topic".
    Do not include any text outside of the JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['topic']


def generate_certificate_image(path_title, user_name, output_file_path):
    """
    Generates a base image using the Gemini API based on the path title,
    then frames it and adds the user's name and issuer name.
    """
    logger.info(f"IMAGE: Starting AI NFT image generation for topic: {path_title}")

    # 1. Generate the base image using Gemini
    base_image = None
    try:
        image_model = genai.GenerativeModel("gemini-2.0-flash-preview-image-generation")

        prompt = (
            f"Create a vibrant, high-contrast 128x128 pixel digital art NFT image representing the topic: '{path_title}'. "
            "The image should be richly colored with a harmonious palette, featuring bold outlines and intricate pixel details "
            "that fully use the canvas. The style should be modern pixel art with a slight 3D effect, glowing highlights, "
            "and smooth shading to make the image pop. The composition must be balanced and visually appealing, suitable for a "
            "collectible NFT series with consistent artistic style and color harmony across variations."
        )

        response = image_model.generate_content(
            contents=prompt,
            generation_config={"response_mime_type": "image/png"}
        )

        base_image_bytes = None
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    base_image_bytes = part.inline_data.data
                    break

        if not base_image_bytes:
            logger.error(f"AI model did not return image data. Full response: {response}")
            raise ValueError("AI model did not return image data.")

        logger.info("IMAGE: AI base image generated successfully.")
        base_image = Image.open(io.BytesIO(base_image_bytes))

    except Exception as e:
        logger.error(f"IMAGE: Failed during Gemini image generation step: {e}", exc_info=True)
        # Create a more graceful fallback image
        base_image = Image.new('RGB', (256, 256), color=(15, 20, 40))
        draw = ImageDraw.Draw(base_image)
        try:
            font_title = ImageFont.truetype("arial.ttf", 20)
            font_body = ImageFont.truetype("arial.ttf", 14)
        except IOError:
            font_title = ImageFont.load_default()
            font_body = ImageFont.load_default()

        wrapper = textwrap.TextWrapper(width=25)
        wrapped_title = '\n'.join(wrapper.wrap(text=path_title))

        draw.text((128, 50), "KODO Certificate", font=font_title, fill=(255, 215, 0), anchor="ms")
        draw.text((128, 128), wrapped_title, font=font_body, fill=(240, 240, 240), anchor="mm")
        draw.text((128, 200), "Generation Failed", font=font_body, fill=(255, 80, 80), anchor="ms")
        logger.warning("IMAGE: Created a fallback placeholder image.")

    # 2. Frame the image and add text using Pillow
    try:
        W, H = 512, 512
        FRAME_THICKNESS = 25
        BG_COLOR = (20, 20, 30)
        FRAME_COLOR = (255, 215, 0)
        TEXT_COLOR = (240, 240, 240)
        ISSUER_COLOR = (255, 215, 0)

        final_image = Image.new('RGB', (W, H), color=BG_COLOR)
        draw = ImageDraw.Draw(final_image)

        draw.rectangle(
            [(FRAME_THICKNESS, FRAME_THICKNESS), (W - FRAME_THICKNESS, H - FRAME_THICKNESS)],
            outline=FRAME_COLOR,
            width=5
        )

        inner_area_size = W - 2 * (FRAME_THICKNESS + 5)
        inner_offset = FRAME_THICKNESS + 5

        base_image = base_image.resize((inner_area_size, inner_area_size), Image.Resampling.NEAREST)
        final_image.paste(base_image, (inner_offset, inner_offset))

        try:
            font_issuer = ImageFont.truetype("arial.ttf", 18)
        except IOError:
            logger.warning("IMAGE: Arial font not found. Falling back to default.")
            font_issuer = ImageFont.load_default()

        issued_to_text = f"Issued to: {user_name}"
        issuer_text = "Issuer: KODO"

        draw.text(
            (FRAME_THICKNESS + 10, H - FRAME_THICKNESS + 5),
            issued_to_text,
            font=font_issuer,
            fill=TEXT_COLOR,
            anchor="ls"
        )
        draw.text(
            (W - FRAME_THICKNESS - 10, H - FRAME_THICKNESS + 5),
            issuer_text,
            font=font_issuer,
            fill=ISSUER_COLOR,
            anchor="rs"
        )

        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        final_image.save(output_file_path)
        logger.info(f"IMAGE: Successfully framed and saved certificate to {output_file_path}")
        return output_file_path

    except Exception as e:
        logger.error(f"IMAGE: Failed during Pillow framing step: {e}", exc_info=True)
        return None