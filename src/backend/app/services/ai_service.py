import json
import base64
import time
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
from app import text_model, logger
from app.config import config
import google.generativeai as genai
from google.generativeai.types import GenerationConfig, Part
import io


def _call_gemini_with_retry(prompt, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = text_model.generate_content(prompt)
            if response.text:
                cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
                json.loads(cleaned_response)
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
    logger.info(f"AI: Generating embedding for text: '{text[:30]}...'")
    result = genai.embed_content(model=config.GEMINI_MODEL_EMBEDDING, content=text)
    return result['embedding']


def rephrase_topic_with_emoji(topic):
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
    - For complex, academic, or broad topics, use 5-8 levels.

    Do not include any text outside of the JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['levels']


def generate_help_curriculum(topic):
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

    **IMPORTANT:** The number of levels should be appropriate for the topic's complexity, typically between 3 and 5 levels.

    Do not include any text outside of the JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['levels']


def generate_learn_level_content(topic, level_title, is_final_level=False):
    logger.info(f"AI: Generating 'learn' content for level: '{level_title}' (is_final: {is_final_level})")

    final_level_guideline = (
        "4. **IMPORTANT FINAL LEVEL RULE:** Since this is the final lesson, you **MUST** include at least one quiz to test the user's overall understanding. This is not optional."
        if is_final_level
        else ""
    )

    prompt = f"""
    You are an expert educator and content designer creating a lesson for a mobile learning app. The main course is "{topic}", and this specific lesson is "{level_title}".
    Your task is to create an insightful, visually engaging, and well-structured learning experience using markdown.

    The output MUST be a single, valid JSON object with one key: "items". "items" must be an array of objects. Each object must have a "type" ('slide' or 'quiz') and a "content" field.

    **Content Guidelines:**
    1.  **Rich & Structured Markdown:** Your content is the UI. Make it beautiful and easy to read.
        - Use `###` for subheadings to break up content.
        - Use `**bold text**` for emphasis and key terms.
        - Use `*italic text*` for nuance or definitions.
        - Use bulleted lists (`* Item 1`) for non-sequential points.
        - Use numbered lists (`1. Step 1`) for sequential steps.
        - Use blockquotes (`> A notable quote or important takeaway.`) to highlight critical information.
    2.  **Insightful & Mobile-First:** Keep paragraphs short (2-4 sentences). Go beyond basic facts and provide context, analogies, or interesting perspectives.
    3.  **Logical Flow:** A good level should have multiple slides. Explain a concept over a minimum of 3 slides before checking for understanding. A typical level should have 5-8 items in total.
    {final_level_guideline}

    **'slide' item format:**
    - "content" should be a string with detailed, informative, and richly formatted markdown in clear, intelligent English.

    **'quiz' item format:**
    - "content" should be a JSON object with four keys: "question" (string), "options" (array of 4 strings), "correctAnswerIndex" (integer 0-3), and "explanation" (string).
    - The question must test for genuine understanding, not just simple recall. The incorrect options (distractors) should be plausible. The explanation must clarify *why* the correct answer is right and provide additional valuable context.

    Generate the complete, mobile-friendly lesson for "{level_title}". Do not include any text outside of the main JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['items']


def generate_help_level_content(topic, step_title, is_final_level=False):
    logger.info(f"AI: Generating 'help' content for step: '{step_title}' (is_final: {is_final_level})")

    final_level_guideline = (
        "4. **IMPORTANT FINAL STEP RULE:** Since this is the final step, you **MUST** include at least one quiz to confirm the user has understood the process. This is not optional."
        if is_final_level
        else ""
    )

    prompt = f"""
    You are an expert guide creating a helpful, interactive lesson for a mobile app. The user's main goal is "{topic}", and this specific step is "{step_title}".
    Your task is to create a clear, effective, and visually structured learning experience using markdown.

    The output MUST be a single, valid JSON object with one key: "items". "items" must be an array of objects. Each object must have a "type" ('slide' or 'quiz') and a "content" field.

    **Content Guidelines:**
    1.  **Rich & Structured Markdown:** Your content is the UI. Make it beautiful and easy to follow.
        - Use `###` for subheadings to break up content.
        - Use `**bold text**` for emphasis and key actions.
        - Use numbered lists (`1. Step 1`) for sequential actions.
        - Use bulleted lists (`* A point to remember`) for tips or notes.
        - Use blockquotes (`> Important safety warning or key insight.`) to highlight critical information.
    2.  **Clear & Focused:** Keep paragraphs short (2-3 sentences). Avoid jargon. Focus on the action for the current step.
    3.  **Check for Understanding:** Include a quiz if it makes sense to test a key piece of knowledge or a critical safety step.
    {final_level_guideline}

    **'slide' item format:**
    - "content" should be a string with a clear, concise, and easy-to-follow explanation for this single step, using rich markdown.

    **'quiz' item format:**
    - "content" should be a JSON object with four keys: "question" (string), "options" (array of 4 strings), "correctAnswerIndex" (integer 0-3), and "explanation" (string).
    - The question should test a critical aspect of the step. The explanation should clarify why the answer is correct.

    Generate the complete, mobile-friendly lesson for "{step_title}". Do not include any text outside of the main JSON object.
    """
    cleaned_response = _call_gemini_with_retry(prompt)
    return json.loads(cleaned_response)['items']


def generate_random_topic():
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
    logger.info(f"IMAGE_GEN_SERVICE: Attempting to generate certificate image.")
    logger.info(f"IMAGE_GEN_SERVICE: Path Title: '{path_title}', User: '{user_name}', Output: '{output_file_path}'")
    logger.info(f"IMAGE_GEN_SERVICE: Using Gemini Vision Model: '{config.GEMINI_MODEL_VISION}'")

    base_image = None
    ai_generated_successfully = False

    try:
        image_model = genai.GenerativeModel(config.GEMINI_MODEL_VISION)
        prompt_for_image_generation = (
            "You are a master artist who creates symbolic, abstract emblems for digital certificates. Your task is to generate a 128x128 pixel art icon that is a deep, metaphorical representation of a learning topic.\n\n"
            f"**TOPIC:** '{path_title}'\n\n"
            "**ARTISTIC INSTRUCTIONS:**\n"
            "1.  **Deconstruct the Topic:** First, identify the core concepts and emotions of the topic. For 'Understand crypto investment psychology', the concepts are 'mind', 'emotion', 'finance', 'digital', 'growth', 'risk'.\n"
            "2.  **Create a Symbol:** Design a central, abstract symbol that merges these concepts. For the crypto example, this could be a glowing brain icon intertwined with a rising chart line, or a heart shape made of circuits.\n"
            "3.  **Style:** Modern pixel art. It must be clean, elegant, and iconic. Use bold outlines, a harmonious and vibrant color palette, and subtle glowing highlights to make it feel like a premium digital badge.\n"
            "4.  **Composition:** The symbol must be centered and balanced.\n"
            "5.  **STRICT NEGATIVE CONSTRAINTS:**\n"
            "    - **ABSOLUTELY NO text, letters, or numbers.**\n"
            "    - **DO NOT generate literal, real-world objects** like cars, houses, or people unless the topic is specifically about them. Focus on symbolism.\n"
            "    - The result must be the image data only. If you also generate text, that's fine, but the primary output I need is the image."
        )
        logger.info(f"IMAGE_GEN_SERVICE: Sending prompt to Gemini model: {prompt_for_image_generation}")
        response = image_model.generate_content(prompt_for_image_generation)
        logger.info(f"IMAGE_GEN_SERVICE: Received response from Gemini model.")

        base_image_bytes = None
        if response.parts:
            logger.info(f"IMAGE_GEN_SERVICE: Processing {len(response.parts)} parts in response.")
            for i, part in enumerate(response.parts):
                if part.inline_data:
                    logger.info(
                        f"IMAGE_GEN_SERVICE: Found inline_data in part {i}. Mime-type: {part.inline_data.mime_type}")
                    if "image" in part.inline_data.mime_type:
                        base_image_bytes = part.inline_data.data
                        logger.info(f"IMAGE_GEN_SERVICE: Extracted image bytes from part {i}.")
                        break
                elif part.text:
                    logger.info(f"IMAGE_GEN_SERVICE: Found text part {i}: '{part.text[:100]}...'")
                else:
                    logger.info(f"IMAGE_GEN_SERVICE: Part {i} has no inline_data or text.")
        else:
            logger.warning(f"IMAGE_GEN_SERVICE: No direct parts in response. Checking candidates.")
            if response.candidates and response.candidates[0].content.parts:
                logger.info(
                    f"IMAGE_GEN_SERVICE: Processing {len(response.candidates[0].content.parts)} parts in candidate 0.")
                for i, part in enumerate(response.candidates[0].content.parts):
                    if part.inline_data:
                        logger.info(
                            f"IMAGE_GEN_SERVICE: Found inline_data in candidate part {i}. Mime-type: {part.inline_data.mime_type}")
                        if "image" in part.inline_data.mime_type:
                            base_image_bytes = part.inline_data.data
                            logger.info(f"IMAGE_GEN_SERVICE: Extracted image bytes from candidate part {i}.")
                            break
                    elif part.text:
                        logger.info(f"IMAGE_GEN_SERVICE: Found text in candidate part {i}: '{part.text[:100]}...'")
                    else:
                        logger.info(f"IMAGE_GEN_SERVICE: Candidate part {i} has no inline_data or text.")
            else:
                logger.warning(f"IMAGE_GEN_SERVICE: No candidates or parts in Gemini response: {response}")

        if not base_image_bytes:
            logger.error(
                f"IMAGE_GEN_SERVICE: AI model '{config.GEMINI_MODEL_VISION}' did not return usable image data bytes. Full response: {response}")
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                logger.error(
                    f"IMAGE_GEN_SERVICE: Prompt feedback block reason: {response.prompt_feedback.block_reason_message}")
            raise ValueError(f"AI model '{config.GEMINI_MODEL_VISION}' did not return usable image data bytes.")

        logger.info(
            f"IMAGE_GEN_SERVICE: AI base image bytes received successfully using '{config.GEMINI_MODEL_VISION}'.")
        base_image = Image.open(io.BytesIO(base_image_bytes))
        logger.info(f"IMAGE_GEN_SERVICE: PIL Image object created from AI bytes. Size: {base_image.size}")
        ai_generated_successfully = True

    except Exception as e:
        logger.error(
            f"IMAGE_GEN_SERVICE: EXCEPTION during Gemini image generation step using '{config.GEMINI_MODEL_VISION}': {e}",
            exc_info=True)

    if not ai_generated_successfully or base_image is None:
        logger.warning(
            f"IMAGE_GEN_SERVICE: AI image generation failed or base_image is None. Proceeding to create fallback image.")
        base_image = Image.new('RGB', (128, 128), color=(10, 10, 20))
        draw = ImageDraw.Draw(base_image)
        try:
            font_fallback = ImageFont.truetype("arial.ttf", 12)
            logger.info("IMAGE_GEN_SERVICE: Loaded arial.ttf for fallback text.")
        except IOError:
            font_fallback = ImageFont.load_default()
            logger.warning("IMAGE_GEN_SERVICE: arial.ttf not found, using default font for fallback text.")
        draw.text((10, 10), "AI Gen\nFailed", fill=(255, 0, 0), font=font_fallback)
        logger.info(f"IMAGE_GEN_SERVICE: Fallback 128x128 placeholder image created in memory.")

    try:
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        logger.info(f"IMAGE_GEN_SERVICE: Ensured directory exists: {os.path.dirname(output_file_path)}")
    except Exception as dir_e:
        logger.error(f"IMAGE_GEN_SERVICE: Could not create directory {os.path.dirname(output_file_path)}: {dir_e}",
                     exc_info=True)
        return None

    try:
        logger.info(
            f"IMAGE_GEN_SERVICE: Starting framing process for image. Current base_image size: {base_image.size if base_image else 'None'}")
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

        logger.info(f"IMAGE_GEN_SERVICE: Resizing base image to ({inner_area_size}, {inner_area_size}) for framing.")
        resized_base_image = base_image.resize((inner_area_size, inner_area_size), Image.Resampling.NEAREST)
        final_image.paste(resized_base_image, (inner_offset, inner_offset))
        logger.info(f"IMAGE_GEN_SERVICE: Base image pasted into frame.")

        try:
            font_issuer = ImageFont.truetype("arial.ttf", 18)
        except IOError:
            logger.warning("IMAGE_GEN_SERVICE: Arial font for issuer text not found. Falling back to default.")
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
        logger.info(f"IMAGE_GEN_SERVICE: Text added to framed image.")

        final_image.save(output_file_path)
        logger.info(
            f"IMAGE_GEN_SERVICE: Successfully framed and saved final certificate to '{output_file_path}'. Image size: {final_image.size}")
        return output_file_path
    except Exception as e:
        logger.error(f"IMAGE_GEN_SERVICE: EXCEPTION during Pillow framing step: {e}", exc_info=True)
        logger.warning(
            f"IMAGE_GEN_SERVICE: Framing failed. Attempting to save the 128x128 base image (AI or fallback) to '{output_file_path}' if it exists.")
        if base_image:
            try:
                base_image.save(output_file_path)
                logger.info(
                    f"IMAGE_GEN_SERVICE: Successfully saved 128x128 base image to '{output_file_path}' after framing failure.")
                return output_file_path
            except Exception as save_base_e:
                logger.error(
                    f"IMAGE_GEN_SERVICE: Failed to save 128x128 base image after framing failure: {save_base_e}",
                    exc_info=True)
                return None
        else:
            logger.error(
                f"IMAGE_GEN_SERVICE: Framing failed and base_image was None. No image saved to '{output_file_path}'.")
            return None