from sqlalchemy import (
    Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Table
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

# Association table for many-to-many relation between Channel and CoursePackage (PackageHistory)
package_history = Table(
    "packagehistory",
    Base.metadata,
    Column("channel_id", Integer, ForeignKey("wpos_wpdatatable_23.wdt_ID")),
    Column("package_id", String(36), ForeignKey("coursepackage.id"))
)

class CoursePackage(Base):
    __tablename__ = "coursepackage"
    id = Column(String(36), primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    isPublished = Column(Boolean, default=False)
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())
    courses = relationship("Course", back_populates="package")
    students = relationship(
        "Channel",
        secondary=package_history,
        back_populates="packages"
    )
    activeStudents = relationship(
        "Channel",
        back_populates="activePackage",
        foreign_keys="Channel.youtubeSubject"
    )
    subjectPackages = relationship("SubjectPackage", back_populates="package")

class SubjectPackage(Base):
    __tablename__ = "subjectpackage"
    id = Column(String(36), primary_key=True)
    subject = Column(String(255), unique=True)
    packageId = Column(String(36), ForeignKey("coursepackage.id"))
    package = relationship("CoursePackage", back_populates="subjectPackages")

class Course(Base):
    __tablename__ = "course"
    id = Column(String(36), primary_key=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    imageUrl = Column(Text)
    isPublished = Column(Boolean, default=False)
    order = Column(Integer)
    packageId = Column(String(36), ForeignKey("coursepackage.id"))
    package = relationship("CoursePackage", back_populates="courses")
    timeLimit = Column(Integer)
    timeUnit = Column(String(50))
    chapters = relationship("Chapter", back_populates="course")
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())

class Chapter(Base):
    __tablename__ = "chapter"
    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    videoUrl = Column(Text)
    position = Column(Integer)
    isPublished = Column(Boolean, default=False)
    courseId = Column(String(36), ForeignKey("course.id"))
    course = relationship("Course", back_populates="chapters")
    questions = relationship("Question", back_populates="chapter")
    studentProgress = relationship("StudentProgress", back_populates="chapter")
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())

class Question(Base):
    __tablename__ = "question"
    id = Column(String(36), primary_key=True)
    chapterId = Column(String(36), ForeignKey("chapter.id"))
    chapter = relationship("Chapter", back_populates="questions")
    question = Column(Text)
    questionOptions = relationship("QuestionOption", back_populates="question")
    questionAnswers = relationship("QuestionAnswer", back_populates="question")
    studentQuizzes = relationship("StudentQuiz", back_populates="question")

class QuestionOption(Base):
    __tablename__ = "questionoption"
    id = Column(String(36), primary_key=True)
    questionId = Column(String(36), ForeignKey("question.id"))
    question = relationship("Question", back_populates="questionOptions")
    option = Column(Text)
    questionAnswers = relationship("QuestionAnswer", back_populates="answer")
    studentQuizAnswers = relationship("StudentQuizAnswer", back_populates="selectedOption")

class QuestionAnswer(Base):
    __tablename__ = "questionanswer"
    id = Column(String(36), primary_key=True)
    questionId = Column(String(36), ForeignKey("question.id"))
    answerId = Column(String(36), ForeignKey("questionoption.id"))
    question = relationship("Question", back_populates="questionAnswers")
    answer = relationship("QuestionOption", back_populates="questionAnswers")

class StudentQuiz(Base):
    __tablename__ = "studentquiz"
    id = Column(String(36), primary_key=True)
    studentId = Column(Integer, ForeignKey("wpos_wpdatatable_23.wdt_ID"))
    questionId = Column(String(36), ForeignKey("question.id"))
    takenAt = Column(DateTime, server_default=func.now())
    studentQuizAnswers = relationship("StudentQuizAnswer", back_populates="studentQuiz")
    student = relationship("Channel", back_populates="studentQuizzes")
    question = relationship("Question", back_populates="studentQuizzes")

class StudentQuizAnswer(Base):
    __tablename__ = "studentquizanswer"
    id = Column(String(36), primary_key=True)
    studentQuizId = Column(String(36), ForeignKey("studentquiz.id"))
    selectedOptionId = Column(String(36), ForeignKey("questionoption.id"))
    studentQuiz = relationship("StudentQuiz", back_populates="studentQuizAnswers")
    selectedOption = relationship("QuestionOption", back_populates="studentQuizAnswers")

class StudentProgress(Base):
    __tablename__ = "studentprogress"
    id = Column(String(36), primary_key=True)
    studentId = Column(Integer, ForeignKey("wpos_wpdatatable_23.wdt_ID"))
    chapterId = Column(String(36), ForeignKey("chapter.id"))
    isStarted = Column(Boolean, default=True)
    isCompleted = Column(Boolean, default=False)
    completedAt = Column(DateTime)
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())
    student = relationship("Channel", back_populates="progress")
    chapter = relationship("Chapter", back_populates="studentProgress")

class Admin(Base):
    __tablename__ = "admin"
    id = Column(String(36), primary_key=True)
    name = Column(String(255))
    phoneno = Column(String(255), unique=True)
    passcode = Column(String(255))
    createdAt = Column(DateTime, server_default=func.now())

class Channel(Base):
    __tablename__ = "wpos_wpdatatable_23"
    wdt_ID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    passcode = Column(String(255), unique=True)
    phoneno = Column(String(255), unique=True)
    status = Column(String(255))
    subject = Column(String(255))
    youtubeSubject = Column(String(36), ForeignKey("coursepackage.id"))
    chat_id = Column(String(255), default="")
    packages = relationship(
        "CoursePackage",
        secondary=package_history,
        back_populates="students"
    )
    activePackage = relationship(
        "CoursePackage",
        foreign_keys=[youtubeSubject],
        back_populates="activeStudents"
    )
    progress = relationship("StudentProgress", back_populates="student")
    studentQuizzes = relationship("StudentQuiz", back_populates="student")