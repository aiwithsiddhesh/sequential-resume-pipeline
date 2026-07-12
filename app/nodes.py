from langchain_groq import ChatGroq

from app.config import settings
from app.state import (
    CoverLetter,
    GapAnalysis,
    ParsedJobDescription,
    ParsedResume,
    PipelineState,
    TailoredResume,
    ValidationResult,
)

MODEL_NAME = "llama-3.3-70b-versatile"


def make_llm(temperature: float) -> ChatGroq:
    return ChatGroq(
        model=MODEL_NAME,
        temperature=temperature,
        api_key=settings.groq_api_key,
    )


def parse_node(state: PipelineState) -> dict:
    resume_llm = make_llm(0.1).with_structured_output(ParsedResume)
    parsed_resume = resume_llm.invoke(
        "Extract the candidate's skills and experience bullets from this "
        f"resume:\n\n{state.raw_resume}"
    )

    jd_llm = make_llm(0.1).with_structured_output(ParsedJobDescription)
    parsed_job_description = jd_llm.invoke(
        "Extract the required skills and requirements from this job "
        f"description:\n\n{state.raw_job_description}"
    )

    return {
        "parsed_resume": parsed_resume,
        "parsed_job_description": parsed_job_description,
    }


def gap_analysis_node(state: PipelineState) -> dict:
    assert state.parsed_resume is not None
    assert state.parsed_job_description is not None

    llm = make_llm(0.1).with_structured_output(GapAnalysis)
    gap_analysis = llm.invoke(
        "Compare the candidate's skills against the job's required skills "
        "and requirements. Identify matched skills, missing skills, and "
        "give a match score from 0 to 100.\n\n"
        f"Candidate skills:\n{state.parsed_resume.skills}\n\n"
        f"Required skills:\n{state.parsed_job_description.required_skills}\n\n"
        f"Requirements:\n{state.parsed_job_description.requirements}"
    )

    return {"gap_analysis": gap_analysis}


def tailor_node(state: PipelineState) -> dict:
    assert state.parsed_resume is not None
    assert state.gap_analysis is not None

    llm = make_llm(0.4).with_structured_output(TailoredResume)
    tailored_resume = llm.invoke(
        "Rewrite and reorder these resume experience bullets to emphasize "
        "the matched skills and, where truthful, address the missing "
        "skills. Do not invent experience the candidate doesn't have.\n\n"
        f"Original bullets:\n{state.parsed_resume.experience_bullets}\n\n"
        f"Matched skills:\n{state.gap_analysis.matched_skills}\n\n"
        f"Missing skills:\n{state.gap_analysis.missing_skills}"
    )

    return {"tailored_resume": tailored_resume}


def cover_letter_node(state: PipelineState) -> dict:
    assert state.tailored_resume is not None
    assert state.gap_analysis is not None

    llm = make_llm(0.6).with_structured_output(CoverLetter)
    cover_letter = llm.invoke(
        "Write a concise, professional cover letter for this job "
        "application. Lean on the tailored resume bullets and briefly "
        "address the candidate's missing skills in a positive way "
        "(e.g. eagerness to learn), without being defensive.\n\n"
        f"Job description:\n{state.raw_job_description}\n\n"
        f"Tailored resume bullets:\n{state.tailored_resume.tailored_bullets}\n\n"
        f"Missing skills:\n{state.gap_analysis.missing_skills}"
    )

    return {"cover_letter": cover_letter}


def validate_node(state: PipelineState) -> dict:
    assert state.parsed_job_description is not None
    assert state.tailored_resume is not None
    assert state.cover_letter is not None

    llm = make_llm(0.1).with_structured_output(ValidationResult)
    validation = llm.invoke(
        "Check whether the tailored resume and cover letter adequately "
        "cover the job description's required skills and requirements. "
        "List which key terms are covered and which are still missing, "
        "give a validation score from 0 to 100, and set passed to true "
        "only if the coverage is strong.\n\n"
        f"Required skills:\n{state.parsed_job_description.required_skills}\n\n"
        f"Requirements:\n{state.parsed_job_description.requirements}\n\n"
        f"Tailored resume bullets:\n{state.tailored_resume.tailored_bullets}\n\n"
        f"Cover letter:\n{state.cover_letter.text}"
    )

    return {"validation": validation}
