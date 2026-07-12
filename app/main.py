import argparse
import json
from datetime import datetime
from pathlib import Path

from app.graph import build_graph
from app.loaders import load_document
from app.state import PipelineState

OUTPUT_DIR = Path("output")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tailor a resume and draft a cover letter for a job description."
    )
    parser.add_argument("resume_path", type=Path, help="Path to resume (.txt or .pdf)")
    parser.add_argument("jd_path", type=Path, help="Path to job description (.txt or .pdf)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    raw_resume = load_document(args.resume_path)
    raw_job_description = load_document(args.jd_path)

    initial_state = PipelineState(
        raw_resume=raw_resume,
        raw_job_description=raw_job_description,
    )

    graph = build_graph()
    result = graph.invoke(initial_state)
    final_state = PipelineState.model_validate(result)

    run_dir = OUTPUT_DIR / f"run_{datetime.now():%Y%m%d_%H%M%S}"
    run_dir.mkdir(parents=True, exist_ok=True)

    result_path = run_dir / "result.json"
    result_path.write_text(final_state.model_dump_json(indent=2), encoding="utf-8")

    print(f"Done. Full result written to {result_path}")


if __name__ == "__main__":
    main()
