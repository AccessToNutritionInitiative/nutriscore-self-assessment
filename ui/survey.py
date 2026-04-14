from collections import defaultdict
import os

import requests
import streamlit as st

from survey_schemas import (
    ChoicesPropositions,
    OptionPropositions,
    Question,
    QuestionResult,
    TextProposition,
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Nutrition Self-Assessment", page_icon="📋", layout="centered")
st.title("📋 Nutrition Self-Assessment")
st.caption("Powered by the ATNi Nutri API")


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
                    answers_by_id[qid] = {"question_id": qid, "score": score}
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
                    answers_by_id[qid] = {"question_id": qid, "score": score}

            elif isinstance(props, TextProposition):
                text_val = st.text_area(
                    props.proposition,
                    key=f"answer_{qid}",
                    label_visibility="collapsed",
                    placeholder=props.proposition,
                )
                if text_val:
                    answers_by_id[qid] = {"question_id": qid, "score": 0.0}

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
                results = [QuestionResult.model_validate(r) for r in resp.json()]

            st.success(f"Assessment complete — {len(results)} recommendations generated.")

            results_by_topic: defaultdict[str, list[QuestionResult]] = defaultdict(list)
            for r in results:
                results_by_topic[r.topic].append(r)

            for topic, topic_results in results_by_topic.items():
                st.subheader(topic)
                topic_score = sum(r.score for r in topic_results)
                st.metric("Topic score", f"{topic_score:.1f}")
                for r in topic_results:
                    if r.recommandation:
                        with st.expander(f"{r.question_id}. {r.question}"):
                            st.markdown(r.recommandation)

        except requests.exceptions.ConnectionError:
            st.error("Cannot reach the API. Make sure the server is running on " + API_BASE_URL)
        except requests.exceptions.HTTPError as exc:
            detail = exc.response.json().get("detail", str(exc))
            st.error(f"API error: {detail}")
