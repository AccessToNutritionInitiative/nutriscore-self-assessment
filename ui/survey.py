import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

TOPICS = [
    "Management & Products",
    "Marketing",
    "Workforce Programs",
    "Labeling",
    "Engagement",
]

st.set_page_config(page_title="Nutrition Self-Assessment", page_icon="📋", layout="centered")
st.title("📋 Nutrition Self-Assessment")
st.caption("Powered by the ATNi Nutri API")


@st.cache_data(ttl=600)
def fetch_questions() -> list[dict]:
    resp = requests.get(f"{API_BASE_URL}/survey/questions", timeout=10)
    resp.raise_for_status()
    return resp.json()


try:
    all_questions = fetch_questions()
except requests.exceptions.ConnectionError:
    st.error("Cannot reach the API. Make sure the server is running on " + API_BASE_URL)
    st.stop()
except requests.exceptions.HTTPError as exc:
    st.error(f"API error: {exc}")
    st.stop()

# Group questions by topic, preserving order
questions_by_topic: dict[str, list[dict]] = {t: [] for t in TOPICS}
for q in all_questions:
    topic = q["topic"]
    if topic in questions_by_topic:
        questions_by_topic[topic].append(q)

# Collect all answers keyed by question_id
answers_by_id: dict[str, dict] = {}

tabs = st.tabs(TOPICS)

for tab, topic in zip(tabs, TOPICS):
    with tab:
        questions = questions_by_topic[topic]
        for q in questions:
            qid = q["question_id"]
            props = q["propositions"]
            dep = q.get("dependency", "")

            # Handle dependency: hide if parent not answered affirmatively
            if dep and dep != qid:
                parent_answer = st.session_state.get(f"answer_{dep}")
                if parent_answer is None:
                    continue
                # For option parents: skip if "No" was selected
                if isinstance(parent_answer, str) and parent_answer == "No":
                    continue
                # For choices parents: skip if nothing selected
                if isinstance(parent_answer, list) and len(parent_answer) == 0:
                    continue

            st.markdown(f"**{qid}. {q['question']}**")

            if props["type"] == "option":
                options = [p["proposition"] for p in props["propositions"]]
                selected = st.radio(
                    f"Select one",
                    options=options,
                    index=None,
                    key=f"answer_{qid}",
                    label_visibility="collapsed",
                )
                if selected is not None:
                    answers_by_id[qid] = {
                        "question_id": qid,
                        "selected_option": selected,
                    }
                    # Check if the selected option has text_inputs
                    for p in props["propositions"]:
                        if p.get("text_inputs") and p["proposition"] == selected:
                            text_val = st.text_area(
                                "Please provide details",
                                key=f"text_{qid}",
                            )
                            if text_val:
                                answers_by_id[qid]["text_input"] = text_val

            elif props["type"] == "choices":
                choice_options = list(props["propositions"])
                has_none = props.get("none_of_the_above", False)

                if has_none:
                    none_checked = st.checkbox(
                        "None of the above",
                        key=f"none_{qid}",
                    )
                    if none_checked:
                        st.session_state[f"answer_{qid}"] = []
                        answers_by_id[qid] = {
                            "question_id": qid,
                            "selected_choices": [],
                        }
                    else:
                        selected_choices = st.multiselect(
                            "Select all that apply",
                            options=choice_options,
                            key=f"answer_{qid}",
                            label_visibility="collapsed",
                        )
                        if selected_choices:
                            answers_by_id[qid] = {
                                "question_id": qid,
                                "selected_choices": selected_choices,
                            }
                else:
                    selected_choices = st.multiselect(
                        "Select all that apply",
                        options=choice_options,
                        key=f"answer_{qid}",
                        label_visibility="collapsed",
                    )
                    if selected_choices:
                        answers_by_id[qid] = {
                            "question_id": qid,
                            "selected_choices": selected_choices,
                        }

            elif props["type"] == "text":
                text_val = st.text_area(
                    props.get("proposition", "Your answer"),
                    key=f"answer_{qid}",
                    label_visibility="collapsed",
                    placeholder=props.get("proposition", ""),
                )
                if text_val:
                    answers_by_id[qid] = {
                        "question_id": qid,
                        "text_input": text_val,
                    }

            st.divider()

# Submit button
st.markdown("---")
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
                results = resp.json()

            st.success(f"Assessment complete — {len(results)} recommendations generated.")

            # Group results by topic
            results_by_topic: dict[str, list[dict]] = {t: [] for t in TOPICS}
            for r in results:
                t = r["topic"]
                if t in results_by_topic:
                    results_by_topic[t].append(r)

            for topic in TOPICS:
                topic_results = results_by_topic[topic]
                if not topic_results:
                    continue
                st.subheader(topic)
                topic_score = sum(r["score"] for r in topic_results)
                st.metric(f"Topic score", f"{topic_score:.1f}")
                for r in topic_results:
                    if r["recommandation"]:
                        with st.expander(f"{r['question_id']}. {r['question']}"):
                            st.markdown(r["recommandation"])

        except requests.exceptions.ConnectionError:
            st.error("Cannot reach the API. Make sure the server is running on " + API_BASE_URL)
        except requests.exceptions.HTTPError as exc:
            detail = exc.response.json().get("detail", str(exc))
            st.error(f"API error: {detail}")
