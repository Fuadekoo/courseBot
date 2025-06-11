import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from models import Channel, SubjectPackage, CoursePackage, Course, Chapter

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL").replace("mysql://", "mysql+mysqlconnector://")
BASE_URL = os.getenv("AUTH_URL")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def fetch_channels(session, chat_id):
    return session.query(Channel).filter(
        Channel.chat_id == str(chat_id),
        Channel.status.in_(["Active", "Notyet"])
    ).all()

def update_youtube_subjects(session, channels):
    for channel in channels:
        subject = channel.subject
        if subject:
            subject_package = session.query(SubjectPackage).filter_by(subject=subject).first()
            channel.youtubeSubject = subject_package.packageId if subject_package else None
        else:
            channel.youtubeSubject = None
    session.commit()

def fetch_channels_with_package(session, chat_id):
    return session.query(Channel).options(
        joinedload(Channel.activePackage)
        .joinedload(CoursePackage.courses)
        .joinedload(Course.chapters)
    ).filter(
        Channel.chat_id == str(chat_id),
        Channel.status.in_(["Active", "Notyet"])
    ).all()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = "en"
    stud = "student"
    session = SessionLocal()

    # 1. Fetch channels
    channels = fetch_channels(session, chat_id)

    # 2. Update youtubeSubject for all channels
    update_youtube_subjects(session, channels)

    # 3. Fetch channels again with relationships
    channels = fetch_channels_with_package(session, chat_id)

    sent = False
    for channel in channels:
        studId = channel.wdt_ID
        active_package = channel.activePackage
        if active_package and active_package.isPublished and active_package.courses:
            course = next((c for c in active_package.courses if c.order == 1), None)
            if course and course.chapters:
                chapter = next((ch for ch in course.chapters if ch.position == 1), None)
                if chapter:
                    url = f"{BASE_URL}/{lang}/{stud}/{studId}/{course.id}/{chapter.id}"
                    name = channel.name or "ዳሩል-ኩብራ"
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"📚 የ{name}ን የትምህርት ገጽ ይክፈቱ", url=url)]
                    ])
                    await update.message.reply_text(
                        "✅  እንኳን ወደ ዳሩል-ኩብራ የቁርአን ማእከል በደህና መጡ! ኮርሱን ለመከታተል ከታች ያለውን ማስፈንጠሪያ ይጫኑ፡፡",
                        reply_markup=keyboard
                    )
                    sent = True
    session.close()
    if not sent:
        await update.message.reply_text("🚫 የኮርሱን ፕላትፎርም ለማግኘት አልተፈቀደለዎትም!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("c", start))
    print("✅ BOT STARTED")
    app.run_polling()

if __name__ == "__main__":
    main()