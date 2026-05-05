from collections import defaultdict
import os

import pandas as pd
import requests
import streamlit as st

from countries import COUNTRIES
from survey_schemas import (
    ChoicesPropositions,
    CompanySize,
    OptionPropositions,
    Question,
    Recommandation,
    SurveyResponse,
    SurveyResults,
    TextProposition,
    TopicResult,
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

GRADE_COLORS = {
    "A": "#038141",
    "B": "#85BB2F",
    "C": "#FECB02",
    "D": "#EE8100",
    "E": "#E63E11",
}

INTRO = """
To support SMEs in the fight against malnutrition, ATNI initiated a 3-year project in April 2019 (ending March 2022), to design a voluntary self-assessment tool for SMEs called the **Nutrition Business Monitor (NBM)** in partnership with the Global Alliance for Improved Nutrition (GAIN). The aim of the tool is to evaluate the performance of SMEs on their commitments and practices related to increasing the affordability and accessibility of nutritious foods and beverages in their respective markets. The tool also produces a document of country-specific recommendations and information for each company, which is based on gaps and areas in need of improvement identified during completion of the tool.

**How to use the file**

This assessment is intended to be used as a self-assessment tool. You can navigate freely from one category to the other.

When filling in the category, your running score appears in the sidebar. Once you submit, you'll see an overall grade, a topic-by-topic breakdown, and tailored recommendations.

**How to navigate the file?**

Click on the relevant tab to toggle the category you want to fill in.
"""

st.set_page_config(page_title="Nutrition Self-Assessment", page_icon="📋", layout="centered")
st.title("📋 Nutrition Self-Assessment")
st.caption("Powered by the ATNi Nutri API")


def percentage_to_grade(pct: float) -> str:
    if pct >= 80:
        return "A"
    if pct >= 60:
        return "B"
    if pct >= 40:
        return "C"
    if pct >= 20:
        return "D"
    return "E"


def render_grade_badge(grade: str) -> None:
    color = GRADE_COLORS.get(grade, "#888888")
    st.markdown(
        f"""
        <div style="
            background-color:{color};
            color:white;
            font-size:4rem;
            font-weight:bold;
            text-align:center;
            border-radius:12px;
            padding:0.4rem 1rem;
        ">{grade}</div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=600)
def fetch_survey() -> dict:
    resp = requests.get(f"{API_BASE_URL}/survey/questions", timeout=10)
    resp.raise_for_status()
    return resp.json()


try:
    survey = SurveyResponse.model_validate(fetch_survey())
    all_questions = survey.questions
    max_score = survey.max_score
    max_score_by_topic = survey.max_score_by_topic
except requests.exceptions.ConnectionError:
    st.error("Cannot reach the API. Make sure the server is running on " + API_BASE_URL)
    st.stop()
except requests.exceptions.HTTPError as exc:
    st.error(f"API error: {exc}")
    st.stop()

# Group questions by topic, preserving first-seen order
questions_by_topic: dict[str, list[Question]] = defaultdict(list)
for q in all_questions:
    questions_by_topic[q.topic].append(q)
topics = list(questions_by_topic)
questions_by_id: dict[str, Question] = {q.question_id: q for q in all_questions}


def build_report_markdown(results: SurveyResults) -> str:
    lines = [
        "# Nutrition Self-Assessment Report",
        "",
        f"**Company:** {results.company_name}  ",
        f"**Country:** {results.country}  ",
        f"**Size:** {results.company_size}  ",
        "",
        f"## Overall score: {results.overall_pct:.1f}% — Grade {results.grade}",
        "",
    ]
    for topic, payload in results.by_topic.items():
        lines.append(f"### {topic}")
        lines.append(f"Score: **{payload.score:.1f} / {payload.max_score:.1f}** ({payload.pct:.1f}%)")
        lines.append("")
        for r in payload.recos:
            q = questions_by_id[r.question_id]
            lines.append(f"- **{r.question_id}. {q.question}**")
            lines.append("")
            lines.append(f"  {r.recommandation}")
            lines.append("")
    return "\n".join(lines)


def render_results(results: SurveyResults) -> None:
    by_topic = results.by_topic

    st.success(f"Assessment complete — {results.n_recos} recommendations generated.")

    col_grade, col_score, col_meta = st.columns([1, 1, 2])
    with col_grade:
        render_grade_badge(results.grade)
    with col_score:
        st.metric("Overall score", f"{results.overall_pct:.1f}%")
        st.caption(f"{results.overall_score:.1f} / {max_score:.1f} pts")
    with col_meta:
        if by_topic:
            best_topic, best_payload = max(by_topic.items(), key=lambda kv: kv[1].pct)
            worst_topic, worst_payload = min(by_topic.items(), key=lambda kv: kv[1].pct)
            st.markdown(f"**Strongest:** {best_topic} ({best_payload.pct:.0f}%)")
            st.markdown(f"**Weakest:** {worst_topic} ({worst_payload.pct:.0f}%)")
            st.caption(f"{results.company_name} — {results.country}")

    st.divider()

    st.subheader("Score by topic")
    chart_df = pd.DataFrame(
        {"Score (%)": [v.pct for v in by_topic.values()]},
        index=list(by_topic.keys()),
    )
    st.bar_chart(chart_df, horizontal=True, x_label="% of max", height=max(120, 40 * len(by_topic)))

    st.divider()

    for topic, payload in by_topic.items():
        with st.container(border=True):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.subheader(topic)
            with col_b:
                st.metric("Score", f"{payload.score:.1f} / {payload.max_score:.1f}")
            st.progress(min(payload.pct / 100.0, 1.0), text=f"{payload.pct:.0f}%")

            if not payload.recos:
                st.caption("No recommendations for this topic — well done.")
                continue

            for r in payload.recos:
                question = questions_by_id[r.question_id]
                if len(r.recommandation) > 400:
                    with st.expander(f"{r.question_id}. {question.question}"):
                        st.markdown(r.recommandation)
                else:
                    st.markdown(f"**{r.question_id}. {question.question}**")
                    st.markdown(r.recommandation)

    st.divider()

    col_dl, col_reset = st.columns(2)
    with col_dl:
        report_md = build_report_markdown(results)
        safe_name = "".join(c if c.isalnum() else "_" for c in results.company_name)
        st.download_button(
            "📥 Download report",
            data=report_md.encode(),
            file_name=f"nutrition_assessment_{safe_name}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_reset:
        if st.button("🔄 Start a new assessment", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith(("answer_", "choice_", "none_", "text_")) or k == "survey_results":
                    del st.session_state[k]
            st.rerun()


# ── Phase: results ─────────────────────────────────────────────────────────────
if "survey_results" in st.session_state:
    with st.expander("Introduction"):
        st.markdown(INTRO)
    render_results(st.session_state["survey_results"])
    st.stop()


# ── Phase: form ────────────────────────────────────────────────────────────────
with st.expander("Introduction", expanded=True):
    st.markdown(INTRO)

st.subheader("About your company")
company_name = st.text_input("Company name", placeholder="Enter your company name", max_chars=50)
col_country, col_size = st.columns(2)
with col_country:
    country = st.selectbox("Country", options=COUNTRIES, index=None, placeholder="Select your country")
with col_size:
    company_size = st.selectbox(
        "Company size",
        options=[s.value for s in CompanySize],
        index=None,
        placeholder="Select company size",
    )
st.divider()

answers_by_id: dict[str, dict] = {}

tabs = st.tabs(topics)

for tab, topic in zip(tabs, topics):
    with tab:
        for q in questions_by_topic[topic]:
            qid = q.question_id
            props = q.propositions
            dep = q.dependency

            # Hide dependent question if parent not answered affirmatively
            if dep and dep != qid:
                parent_answer = st.session_state.get(f"answer_{dep}")
                if parent_answer is None:
                    continue
                if isinstance(parent_answer, str) and parent_answer == "No":
                    continue
                if isinstance(parent_answer, list) and len(parent_answer) == 0:
                    continue

            st.markdown(f"**{qid}. {q.question}**")

            if isinstance(props, OptionPropositions):
                options = [p.proposition for p in props.propositions]
                selected = st.radio(
                    "Select one",
                    options=options,
                    index=None,
                    key=f"answer_{qid}",
                    label_visibility="collapsed",
                )
                if selected is not None:
                    score = next(p.score for p in props.propositions if p.proposition == selected)
                    answers_by_id[qid] = {"question_id": qid, "score": score, "value": selected}
                    for p in props.propositions:
                        if p.text_inputs and p.proposition == selected:
                            st.text_area("Please provide details", key=f"text_{qid}")

            elif isinstance(props, ChoicesPropositions):
                if props.none_of_the_above and st.session_state.get(f"none_{qid}", False):
                    for i in range(len(props.propositions)):
                        st.session_state[f"choice_{qid}_{i}"] = False

                st.caption("Select all that apply")
                selected_choices = [
                    choice
                    for i, choice in enumerate(props.propositions)
                    if st.checkbox(choice, key=f"choice_{qid}_{i}")
                ]

                none_checked = False
                if props.none_of_the_above:
                    none_checked = st.checkbox("None of the above", key=f"none_{qid}")

                st.session_state[f"answer_{qid}"] = selected_choices
                if selected_choices or none_checked:
                    count = len(selected_choices)
                    if props.count_score_map:
                        score = props.count_score_map[min(count, len(props.count_score_map) - 1)]
                    else:
                        score = count * props.count_score_coeff
                    answers_by_id[qid] = {"question_id": qid, "score": score, "value": selected_choices}

            elif isinstance(props, TextProposition):
                text_val = st.text_area(
                    props.proposition,
                    key=f"answer_{qid}",
                    label_visibility="collapsed",
                    placeholder=props.proposition,
                )
                if text_val:
                    answers_by_id[qid] = {"question_id": qid, "score": 0.0, "value": text_val}

            st.divider()

# Live score panel in sidebar
running_score = sum(a["score"] for a in answers_by_id.values())
running_pct = (running_score / max_score * 100) if max_score else 0.0

with st.sidebar:
    st.divider()
    st.markdown("### Live score")
    st.progress(
        min(running_pct / 100, 1.0),
        text=f"{running_pct:.0f}% — {running_score:.1f} / {max_score:.1f}",
    )
    st.caption("Updates as you answer")
    for topic in topics:
        topic_answers = [
            a for a in answers_by_id.values() if questions_by_id[a["question_id"]].topic == topic
        ]
        topic_score = sum(a["score"] for a in topic_answers)
        topic_max = max_score_by_topic.get(topic, 0.0)
        topic_pct = (topic_score / topic_max * 100) if topic_max else 0.0
        st.caption(f"**{topic}** — {topic_score:.1f} / {topic_max:.1f} ({topic_pct:.0f}%)")

submitted = st.button("Submit assessment", type="primary", use_container_width=True)

if submitted:
    if not company_name or len(company_name) < 2 or not country or not company_size:
        st.warning(
            "Please enter your company name, country, and company size before submitting. Company name needs to be at least 2 characters long."
        )
    elif not answers_by_id:
        st.warning("Please answer at least one question before submitting.")
    else:
        payload = {
            "company_name": company_name,
            "country": country,
            "company_size": company_size,
            "answers": list(answers_by_id.values()),
        }
        try:
            with st.spinner("Computing recommendations..."):
                resp = requests.post(
                    f"{API_BASE_URL}/survey/answers",
                    json=payload,
                    timeout=30,
                )
                resp.raise_for_status()
                recommandations = [Recommandation.model_validate(r) for r in resp.json()]

            scores_by_id: dict[str, float] = {a["question_id"]: a["score"] for a in payload["answers"]}
            overall_score = sum(scores_by_id.values())
            overall_pct = (overall_score / max_score * 100) if max_score else 0.0

            recos_by_topic_lookup: defaultdict[str, list[Recommandation]] = defaultdict(list)
            for r in recommandations:
                question = questions_by_id.get(r.question_id)
                if question is not None:
                    recos_by_topic_lookup[question.topic].append(r)

            by_topic_results: dict[str, TopicResult] = {}
            for topic in topics:
                topic_score = sum(scores_by_id.get(q.question_id, 0.0) for q in questions_by_topic[topic])
                topic_max = max_score_by_topic[topic]
                topic_pct = (topic_score / topic_max * 100) if topic_max else 0.0
                by_topic_results[topic] = TopicResult(
                    score=topic_score,
                    max_score=topic_max,
                    pct=topic_pct,
                    recos=recos_by_topic_lookup.get(topic, []),
                )

            st.session_state["survey_results"] = SurveyResults(
                company_name=company_name,
                country=country,
                company_size=company_size,
                overall_score=overall_score,
                overall_pct=overall_pct,
                grade=percentage_to_grade(overall_pct),
                n_recos=len(recommandations),
                by_topic=by_topic_results,
            )
            st.rerun()

        except requests.exceptions.ConnectionError:
            st.error("Cannot reach the API. Make sure the server is running on " + API_BASE_URL)
        except requests.exceptions.HTTPError as exc:
            detail = exc.response.json().get("detail", str(exc))
            st.error(f"API error: {detail}")
