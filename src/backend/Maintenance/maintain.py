import os
import io
import tokenize
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

def strip_comments_and_blank_lines(path):
    comment_count = 0
    blank_removed_count = 0

    with open(path, "rb") as f:
        src_bytes = f.read()

    tokens = []
    readline = io.BytesIO(src_bytes).readline
    for tok in tokenize.tokenize(readline):
        if tok.type == tokenize.COMMENT:
            comment_count += 1
            logging.info(f"Removed comment at {path}:{tok.start[0]}")
            continue
        tokens.append(tok)

    cleaned = tokenize.untokenize(tokens).decode("utf-8")

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
            logging.info(f"Removed blank line at cleaned line {idx} in {path}")

    final = "\n".join(result_lines) + "\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(final)

    logging.info(f"Total comments removed in {path}: {comment_count}")
    logging.info(f"Total blank lines removed in {path}: {blank_removed_count}")


def process_path(path):
    if os.path.isfile(path) and path.endswith(".py"):
        strip_comments_and_blank_lines(path)
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    strip_comments_and_blank_lines(file_path)
    else:
        logging.error(f"`{path}` is not a valid file or directory")


if __name__ == "__main__":
    # Hardcode the target file or folder here
    path = r"../app"
    if not os.path.exists(path):
        logging.error(f"Path not found: `{path}`")
        exit(1)
    process_path(path)