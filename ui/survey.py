from collections import defaultdict
import os

import requests
import streamlit as st

from survey_schemas import (
    ChoicesPropositions,
    OptionPropositions,
    Question,
    Recommandation,
    TextProposition,
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

INTRO = """
To support SMEs in the fight against malnutrition, ATNI initiated a 3-year project in April 2019 (ending March 2022), to design a voluntary self-assessment tool for SMEs called the **Nutrition Business Monitor (NBM)** in partnership with the Global Alliance for Improved Nutrition (GAIN). The aim of the tool is to evaluate the performance of SMEs on their commitments and practices related to increasing the affordability and accessibility of nutritious foods and beverages in their respective markets. The tool also produces a document of country-specific recommendations and information for each company, which is based on gaps and areas in need of improvement identified during completion of the tool.

**How to use the file**

This assessment is intended to be used as a self-assessment tool. You can navigate freely from one category to the other.

When filling in the category, you can see your score appearing in the top row. You can also read the corresponding recommendations on the Recommendations Tab and view your overall results on the Results tab.

**How to navigate the file?**

Click on the relevant tab to toggle the category you want to fill in.
"""

st.set_page_config(page_title="Nutrition Self-Assessment", page_icon="📋", layout="centered")
st.title("📋 Nutrition Self-Assessment")
st.caption("Powered by the ATNi Nutri API")

with st.expander("Introduction", expanded=True):
    st.markdown(INTRO)


@st.cache_data(ttl=600)
def fetch_questions() -> list[dict]:
    resp = requests.get(f"{API_BASE_URL}/survey/questions", timeout=10)
    resp.raise_for_status()
    return resp.json()


try:
    raw_questions = fetch_questions()
    all_questions = [Question.model_validate(q) for q in raw_questions]
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

# Collect all answers keyed by question_id
answers_by_id: dict[str, dict] = {}

tabs = st.tabs(topics)

for tab, topic in zip(tabs, topics):
    with tab:
        for q in questions_by_topic[topic]:
            qid = q.question_id
            props = q.propositions
            dep = q.dependency

            # Handle dependency: hide if parent not answered affirmatively
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
                selected_choices = [choice for i, choice in enumerate(props.propositions) if st.checkbox(choice, key=f"choice_{qid}_{i}")]

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

# Submit button
submitted = st.button("Submit assessment", type="primary", use_container_width=True)

if submitted:
    if not answers_by_id:
        st.warning("Please answer at least one question before submitting.")
    else:
        payload = list(answers_by_id.values())
        try:
            with st.spinner("Computing recommendations..."):
                resp = requests.post(
                    f"{API_BASE_URL}/survey/answers",
                    json=payload,
                    timeout=30,
                )
                resp.raise_for_status()
                recommandations = [Recommandation.model_validate(r) for r in resp.json()]

            st.success(f"Assessment complete — {len(recommandations)} recommendations generated.")

            questions_by_id: dict[str, Question] = {q.question_id: q for q in all_questions}
            scores_by_id: dict[str, float] = {a["question_id"]: a["score"] for a in payload}

            recos_by_topic: defaultdict[str, list[Recommandation]] = defaultdict(list)
            for r in recommandations:
                question = questions_by_id.get(r.question_id)
                if question is not None:
                    recos_by_topic[question.topic].append(r)

            for topic, topic_recos in recos_by_topic.items():
                st.subheader(topic)
                topic_score = sum(scores_by_id.get(r.question_id, 0.0) for r in topic_recos)
                st.metric("Topic score", f"{topic_score:.1f}")
                for r in topic_recos:
                    question = questions_by_id[r.question_id]
                    with st.expander(f"{r.question_id}. {question.question}"):
                        st.markdown(r.recommandation)

        except requests.exceptions.ConnectionError:
            st.error("Cannot reach the API. Make sure the server is running on " + API_BASE_URL)
        except requests.exceptions.HTTPError as exc:
            detail = exc.response.json().get("detail", str(exc))
            st.error(f"API error: {detail}")
