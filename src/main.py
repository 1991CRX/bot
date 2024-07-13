import logging
import os
import pathlib
import sys

import praw
import praw.models

SUB_NAME = os.environ["SUB_NAME"]
MIN_IMAGE_WIDTH_PX = 3100
NUM_POSTS_TO_PROCESS = 10
REMOVAL_MESSAGE_SUBJECT = "LOW QUALITY IMAGE"

src_path = pathlib.Path(__file__).parent
REMOVAL_COMMENT = (src_path / "removal_comment.md").read_text()
REMOVAL_MESSAGE = (src_path / "removal_message.md").read_text()


def setup_logger() -> None:
    logging.basicConfig(
        format="[%(asctime)s] %(message)s",
        datefmt="%m-%d %I:%M",
        level=logging.INFO,
        handlers=[
            logging.FileHandler("logs.log", mode="a"),
            logging.StreamHandler(),
        ],
    )


def create_reddit_instance() -> praw.Reddit:
    try:
        reddit = praw.Reddit(
            username=os.environ["USERNAME"],
            password=os.environ["PASSWORD"],
            client_id=os.environ["CLIENT_ID"],
            client_secret=os.environ["CLIENT_SECRET"],
            user_agent=os.environ["USER_AGENT"],
            ratelimit_seconds=600,
        )
    except Exception as e:
        logging.error("Failed to authenticate: %s", e)
        sys.exit()

    return reddit


def extract_width(selftext: str) -> int:
    try:
        extracted_string = selftext.split("width=")[1].split("&")[0]
        width = int(extracted_string)
        return int(width)
    except IndexError:
        return -1


def convert_to_dpi(image_width: int) -> int:
    return round(image_width / 8.5)


def reject(submission: praw.models.Submission, image_width: int) -> None:
    submission.mod.remove(spam=False)
    submission.mod.flair(
        text="Post Removed: Low Quality Image",
        css_class="removed",
        flair_template_id="7e1d0b6c-b178-11ee-866f-b61c7ef1fdc8",
    )
    submission.mod.lock()
    removal_comment_with_author = REMOVAL_COMMENT.format(
        author=submission.author, sub=SUB_NAME
    )
    submission.mod.send_removal_message(
        type="public_as_subreddit", message=removal_comment_with_author
    )
    submission.mod.send_removal_message(
        type="private",
        title=REMOVAL_MESSAGE_SUBJECT,
        message=REMOVAL_MESSAGE,
    )
    logging.info("REJECTED, %s, %d, %s", submission.id, image_width, submission.author)


def approve(submission: praw.models.Submission, image_width: int) -> None:
    submission.mod.approve()
    logging.info("APPROVED, %s, %d, %s", submission.id, image_width, submission.author)


def process(submission: praw.models.Submission) -> None:
    if submission.approved:
        return

    if submission.link_flair_text in {"Question", "Success Story!", "Meta"}:
        return

    image_width = extract_width(submission.selftext)

    if image_width == -1:
        logging.error(
            "UNABLE TO EXTRACT WIDTH FROM BODY TEXT, %s, %s",
            submission.id,
            submission.author,
        )

    elif image_width < MIN_IMAGE_WIDTH_PX:
        reject(submission, image_width)

    else:
        approve(submission, image_width)


if __name__ == "__main__":
    setup_logger()
    reddit = create_reddit_instance()
    subreddit: praw.models.Subreddit = reddit.subreddit(SUB_NAME)

    for submission in subreddit.new(limit=NUM_POSTS_TO_PROCESS):
        process(submission)
