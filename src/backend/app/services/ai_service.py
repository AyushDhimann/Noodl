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
    You are a curriculum expert who creates clear, engaging, and insightful course titles. A user has provided the topic "{topic}".
    Your task is to transform this into a simple, straightforward, and encouraging title that accurately reflects its value.

    **RULES:**
    1.  Prepend a single, relevant emoji to the very beginning of the new title.
    2.  The title MUST be a single, simple sentence.
    3.  The title MUST NOT contain any colons (:). Keep it clean and direct.
    4.  The tone should be encouraging and inspiring, highlighting what the user will be able to do or understand.

    The output MUST be a single, valid JSON object with one key: "new_title".
    Do not include any text outside of the JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['new_title']


def generate_path_description(topic_title):
    """Generates an engaging, frontend-ready description for the learning path."""
    logger.info(f"AI: Generating description for topic: '{topic_title}'")
    prompt = f"""
    You are a curriculum writer for a learning app. Your goal is to write compelling descriptions for a course titled "{topic_title}".
    You must use clear, intelligent English, suitable for a global audience. Your descriptions should highlight the value and key takeaways of the course.

    Your task is to generate two distinct descriptions:
    1. A "short_description": A very brief, one-sentence summary. It must be a maximum of 20 words.
    2. A "long_description": A more detailed paragraph. It should give an overview of what the user will learn and why it's useful. It must be a maximum of 80 words.

    The output MUST be a single, valid JSON object with two keys: "short_description" and "long_description".
    Do not include any text outside of the JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)


def generate_learn_curriculum(topic, country=None):
    """Asks AI to generate a dynamic curriculum for a 'learn' intent."""
    logger.info(f"AI: Generating 'learn' curriculum for topic: '{topic}' with country context: {country}")
    country_context = f"The user is from {country}, so you can use local examples or spellings if relevant, but it's not a requirement." if country else ""
    prompt = f"""You are an expert curriculum designer. For the course titled "{topic}", create a detailed, logical syllabus. The goal is to take a user from beginner to competent, respecting their intelligence. {country_context}

    **RULES:**
    1.  The output MUST be a single, valid JSON object with one key: "levels".
    2.  "levels" must be an array of strings.
    3.  Each string in the array is a concise title for a learning level.
    4.  Each title must represent a distinct and meaningful concept or step in the learning journey. Avoid breaking down concepts into trivially small pieces.
    5.  Each title MUST start with a single, relevant emoji.
    6.  Each title MUST NOT start with a number (e.g., "1.", "2.").

    **IMPORTANT:** The number of levels should be appropriate for the topic's complexity.
    - For simple, everyday topics, use 3-4 levels.
    - For complex, academic, or broad topics, use 7-10 levels.

    Do not include any text outside of the JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['levels']


def generate_help_curriculum(topic):
    """Generates a step-by-step guide for a 'help' intent."""
    logger.info(f"AI: Generating 'help' curriculum for topic: '{topic}'")
    prompt = f"""You are a helpful and clear technical writer. A user needs help with: "{topic}".
    Your task is to break down the solution into a series of simple, logical, and actionable steps. These steps will become the titles of a short guide.

    **RULES:**
    1.  The output MUST be a single, valid JSON object with one key: "levels".
    2.  "levels" must be an array of strings.
    3.  Each string is a step in the process, written in clear, encouraging language.
    4.  Each title must represent a distinct and meaningful step. Do not include obvious or redundant steps.
    5.  Each title MUST start with a single, relevant emoji.
    6.  Each title MUST NOT start with a number (e.g., "1.", "2.").

    Do not include any text outside of the JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['levels']


def generate_learn_level_content(topic, level_title, is_final_level=False):
    """Generates rich, interleaved content for a single 'learn' level."""
    logger.info(f"AI: Generating 'learn' content for level: '{level_title}' (is_final: {is_final_level})")

    final_level_guideline = (
        "4. **IMPORTANT FINAL LEVEL RULE:** Since this is the final lesson, you **MUST** include at least one quiz to test the user's overall understanding. This is not optional."
        if is_final_level
        else ""
    )

    prompt = f"""
    You are an expert educator creating a lesson for a mobile learning app. The main course is "{topic}", and this specific lesson is "{level_title}".
    Your task is to create an insightful, interleaved learning experience.

    The output MUST be a single, valid JSON object with one key: "items". "items" must be an array of objects. Each object must have a "type" ('slide' or 'quiz') and a "content" field.

    **Content Guidelines:**
    1.  **Mobile First & Insightful:** Keep paragraphs short (2-3 sentences). Your explanation should be intelligent and go beyond the basics. Provide context, interesting facts, or a novel perspective. Avoid simply stating the obvious. Use markdown `### Subheadings`, `**bold**`, and bullet points (`* item`).
    2.  **Logical Flow:** A good level should have multiple slides. Explain a concept over a minimum of 3 slides before checking for understanding. A typical level should have 5-8 items in total.
    3.  **Meaningful Quizzes:** Include a quiz only when it makes sense to test a key piece of knowledge.
    {final_level_guideline}

    **'slide' item format:**
    - "content" should be a string with detailed, informative markdown in clear, intelligent English.

    **'quiz' item format:**
    - "content" should be a JSON object with four keys: "question" (string), "options" (array of 4 strings), "correctAnswerIndex" (integer 0-3), and "explanation" (string).
    - The question must test for genuine understanding, not just simple recall. The incorrect options (distractors) should be plausible. The explanation must clarify *why* the correct answer is right and provide additional valuable context.

    Generate the complete, mobile-friendly lesson for "{level_title}". Do not include any text outside of the main JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['items']


def generate_help_level_content(topic, step_title, is_final_level=False):
    """Generates rich, interleaved content for a single 'help' step."""
    logger.info(f"AI: Generating 'help' content for step: '{step_title}' (is_final: {is_final_level})")

    final_level_guideline = (
        "4. **IMPORTANT FINAL STEP RULE:** Since this is the final step, you **MUST** include at least one quiz to confirm the user has understood the process. This is not optional."
        if is_final_level
        else ""
    )

    prompt = f"""
    You are an expert guide creating a helpful, interactive lesson for a mobile app. The user's main goal is "{topic}", and this specific step is "{step_title}".
    Your task is to create an clear and effective interleaved learning experience.

    The output MUST be a single, valid JSON object with one key: "items". "items" must be an array of objects. Each object must have a "type" ('slide' or 'quiz') and a "content" field.

    **Content Guidelines:**
    1.  **Mobile First & Clear:** Keep paragraphs short (2-3 sentences). Use markdown `### Subheadings`, `**bold**`, and bullet points (`* item`) to make instructions easy to follow. Avoid jargon where possible.
    2.  **Focused Content:** A good step-by-step guide should have multiple slides to explain the process clearly. A typical step should have 3-5 items in total.
    3.  **Check for Understanding:** Include a quiz if it makes sense to test a key piece of knowledge or a critical safety step.
    {final_level_guideline}

    **'slide' item format:**
    - "content" should be a string with a clear, concise, and easy-to-follow explanation for this single step.

    **'quiz' item format:**
    - "content" should be a JSON object with four keys: "question" (string), "options" (array of 4 strings), "correctAnswerIndex" (integer 0-3), and "explanation" (string).
    - The question should test a critical aspect of the step. The explanation should clarify why the answer is correct.

    Generate the complete, mobile-friendly lesson for "{step_title}". Do not include any text outside of the main JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['items']


def generate_random_topic():
    """Asks the AI to generate a single, random, interesting topic for a learning path."""
    logger.info("AI: Generating a random topic...")
    prompt = """
    You are a creative and insightful assistant tasked with generating compelling topics for educational content.
    Your goal is to brainstorm a single topic for a short course or a helpful guide that provides genuine, real-world value to a curious adult.

    **RULES:**
    1.  **FOCUS ON VALUE:** The topic must be practical, intellectually stimulating, or teach a useful skill. It should answer a question the user might genuinely have or introduce a fascinating concept they haven't considered.
    2.  **AVOID TRIVIALITY:** Do not suggest topics that are common knowledge (e.g., "How to tie your shoes") or overly simplistic. Aim for a level of depth that respects the user's intelligence.
    3.  **BE CREATIVE & DIVERSE:** Think across a wide range of categories: personal finance, professional skills, DIY projects, scientific concepts, historical deep-dives, creative hobbies, or practical life-hacks.
    4.  **BE SPECIFIC:** Instead of a broad topic like "History," suggest something more focused and intriguing like "The History and Science of Fermentation."

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
            f"Create a vibrant, high-contrast 128x128 pixel digital art NFT image representing the TOPIC: '{path_title}'. "
            "The image should be richly colored with a harmonious palette, featuring bold outlines and intricate pixel details "
            "that fully use the canvas. The style should be modern pixel art with a slight 3D effect, glowing highlights, "
            "and smooth shading to make the image pop. The composition must be balanced and visually appealing, suitable for a "
            "collectible NFT series with consistent artistic style and color harmony across variations."
        )

        # CORRECTED: Pass the generation_config as a dictionary.
        response = image_model.generate_content(
            contents=prompt,
            generation_config={"response_modalities": ["IMAGE", "TEXT"]}
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
        base_image = Image.new('RGB', (128, 128), color=(10, 10, 20))
        draw = ImageDraw.Draw(base_image)
        try:
            font_fallback = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            font_fallback = ImageFont.load_default()
        draw.text((10, 10), "AI Gen\nFailed", fill=(255, 0, 0), font=font_fallback)
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