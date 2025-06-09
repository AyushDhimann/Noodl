import json
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from app import text_model, logger
import google.generativeai as genai

def get_embedding(text):
    """Generates a vector embedding for a given text."""
    logger.info(f"AI: Generating embedding for text: '{text[:30]}...'")
    result = genai.embed_content(model="models/embedding-001", content=text)
    return result['embedding']

def generate_curriculum(topic):
    """Asks AI to generate a dynamic curriculum (list of level titles)."""
    logger.info(f"AI: Generating curriculum for topic: '{topic}'")
    prompt = f"""You are an expert curriculum designer for a learning app. For the topic "{topic}", create a syllabus. The output MUST be a single, valid JSON object with one key: "levels". "levels" should be an array of strings, where each string is a concise title for a learning level. The number of levels should be appropriate for the topic's complexity (3-10 levels). Do not include any text outside of the JSON object. Also make sure the title of the level starts with an emoji which is appropriate to the level please, a single emoji at the starting is a must."""
    response = text_model.generate_content(prompt)
    cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(cleaned_response)['levels']

def generate_interleaved_level_content(topic, level_title):
    """Generates slides and quiz for a single level."""
    logger.info(f"AI: Generating interleaved content for level: '{level_title}'")
    prompt = f"""
    You are an expert educator creating a lesson for a learning app. The main topic is "{topic}", and this specific lesson is titled "{level_title}".
    Your task is to create an interleaved learning experience with slides and quizzes.
    The output MUST be a single, valid JSON object with one key: "items".
    "items" must be an array of objects. Each object must have a "type" ('slide' or 'quiz') and a "content" field.

    1.  For a 'slide' item:
        - The "content" field should be a string containing rich markdown.
        - Use markdown for formatting: `### Subheadings`, `**bold**`, `* item 1`, `* item 2`.
        - The content should be detailed and informative, providing real value. A slide can be multiple paragraphs long.
        - Structure the lesson logically: start with an introduction, explain concepts with a few slides, then add a quiz to check understanding. Repeat this pattern 2-3 times, ending with a final quiz. A typical level should have 5-8 items in total.

    2.  For a 'quiz' item:
        - The "content" field should be a JSON object with four keys: "question" (string), "options" (array of 4 strings), "correctAnswerIndex" (integer 0-3), and "explanation" (string).
        - The "explanation" should be a "Do you know? 🤓" fun fact or a clear explanation of why the correct answer is right. It should also be formatted with markdown.

    Generate the complete, interleaved lesson for "{level_title}". Do not include any text outside of the main JSON object.
    """
    response = text_model.generate_content(prompt)
    cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
    return json.loads(cleaned_response)['items']

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
        img = Image.new('RGB', (512, 512), color = '#1a1a1a')
        d = ImageDraw.Draw(img)
        try:
            title_font = ImageFont.truetype("DejaVuSans.ttf", 32)
            subtitle_font = ImageFont.truetype("DejaVuSans.ttf", 24)
        except IOError:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        d.text((256, 220), "Noodl Certificate", font=title_font, fill="#FFFFFF", anchor="ms")
        d.text((256, 260), title, font=subtitle_font, fill="#DDDDDD", anchor="ms")
        d.rectangle([(20,20), (512-20,512-20)], outline="#4ECDC4", width=5)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        png_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f'<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg"><image href="data:image/png;base64,{png_b64}" height="512" width="512"/></svg>'