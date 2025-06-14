import os
import io
import tokenize
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

def strip_comments_and_blank_lines(path):
    comment_count = 0
    blank_removed_count = 0

    # Read original file as bytes
    with open(path, "rb") as f:
        src_bytes = f.read()

    # Remove all COMMENT tokens
    tokens = []
    readline = io.BytesIO(src_bytes).readline
    for tok in tokenize.tokenize(readline):
        if tok.type == tokenize.COMMENT:
            comment_count += 1
            logging.info(f"Removed comment at {path}:{tok.start[0]}")
            continue
        tokens.append(tok)

    # Reconstruct source code
    cleaned = tokenize.untokenize(tokens).decode("utf-8")

    # Collapse multiple blank lines
    result_lines = []
    blank_count = 0
    for idx, line in enumerate(cleaned.splitlines(), start=1):
        if not line.strip():
            blank_count += 1
        else:
            blank_count = 0

        if blank_count <= 1:
            result_lines.append(line)
        else:
            blank_removed_count += 1
            logging.info(f"Removed blank line at cleaned line {idx}")

    final = "\n".join(result_lines) + "\n"

    # Overwrite the original file
    with open(path, "w", encoding="utf-8") as f:
        f.write(final)

    logging.info(f"Total comments removed: {comment_count}")
    logging.info(f"Total blank lines removed: {blank_removed_count}")


if __name__ == "__main__":
    # Hardcode the target file here
    path = r"../app/services/supabase_service.py"
    if not os.path.isfile(path):
        logging.error(f"File not found: {path}")
        exit(1)
    strip_comments_and_blank_lines(path)