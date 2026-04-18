"""
Multilingual AI System with Translation, Summarization, and Q&A

This version uses Streamlit so the project runs in a browser with
clickable buttons and simple student-friendly sections.
"""

import streamlit as st
from deep_translator import GoogleTranslator
from langdetect import LangDetectException, detect


LANGUAGE_LABELS = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
}


def split_sentences(text: str) -> list[str]:
    """
    Split text into simple sentences without extra libraries.
    """
    cleaned_text = text.replace("\n", " ").strip()
    sentences = []
    current_sentence = ""

    for character in cleaned_text:
        current_sentence += character
        if character in ".!?":
            sentence = current_sentence.strip()
            if sentence:
                sentences.append(sentence)
            current_sentence = ""

    if current_sentence.strip():
        sentences.append(current_sentence.strip())

    return sentences


def tokenize_words(text: str) -> list[str]:
    """
    Convert text into lowercase alphabetic words.
    """
    word = ""
    words = []

    for character in text.lower():
        if character.isalpha():
            word += character
        elif word:
            words.append(word)
            word = ""

    if word:
        words.append(word)

    return words


def translate_text(text: str, target_lang: str, source_lang: str = "en") -> str:
    """
    Translate text from one language to another.
    """
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty.")

    if source_lang not in LANGUAGE_LABELS or target_lang not in LANGUAGE_LABELS:
        raise ValueError("Please choose a valid language code: en, hi, or mr.")

    if source_lang == target_lang:
        return text

    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        return translator.translate(text)
    except Exception as error:
        raise ValueError(
            f"Translation failed. Please check your internet connection and try again. Details: {error}"
        ) from error


def summarize_text(text: str) -> str:
    """
    Summarize the given text using a fast extractive method.
    """
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty.")

    if len(text.split()) < 35:
        return text

    sentences = split_sentences(text)

    if len(sentences) <= 2:
        return text

    stop_words = {
        "a", "an", "the", "is", "are", "was", "were", "and", "or", "of", "to", "in",
        "on", "for", "with", "by", "as", "at", "from", "that", "this", "it", "be",
        "can", "into", "more", "than", "their", "its", "these", "those", "will",
        "has", "have", "had", "also", "such", "through", "using", "use",
    }

    word_frequency = {}
    for word in tokenize_words(text):
        if word not in stop_words and len(word) > 2:
            word_frequency[word] = word_frequency.get(word, 0) + 1

    if not word_frequency:
        return " ".join(sentences[:2])

    sentence_scores = []
    for index, sentence in enumerate(sentences):
        score = 0
        words = tokenize_words(sentence)
        for word in words:
            score += word_frequency.get(word, 0)
        sentence_scores.append((index, score, sentence))

    ranked_sentences = sorted(sentence_scores, key=lambda item: item[1], reverse=True)
    top_sentences = sorted(ranked_sentences[:2], key=lambda item: item[0])
    return " ".join(sentence for _, _, sentence in top_sentences)


def answer_question(context: str, question: str) -> str:
    """
    Answer a question using a simple sentence-matching approach.
    """
    if not context or not context.strip():
        raise ValueError("Context cannot be empty.")

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    question_words = {
        word for word in tokenize_words(question)
        if word not in {"what", "when", "where", "which", "who", "why", "how", "is", "are"}
    }
    sentences = split_sentences(context)

    if not sentences:
        return "Answer not found in the given text."

    best_sentence = ""
    best_score = 0

    for sentence in sentences:
        sentence_words = set(tokenize_words(sentence))
        overlap_score = len(question_words.intersection(sentence_words))

        if overlap_score > best_score:
            best_score = overlap_score
            best_sentence = sentence.strip()

    if best_score == 0 or not best_sentence:
        return "Answer not found in the given text."

    return best_sentence


def detect_language_safe(text: str) -> str:
    """
    Detect the language safely.
    """
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def agentic_workflow(text: str, output_lang: str = "hi") -> dict:
    """
    Full agentic workflow:
    Input -> Detect Language -> Translate -> Summarize -> Output
    """
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty.")

    if output_lang not in LANGUAGE_LABELS:
        raise ValueError("Please choose a valid output language: en, hi, or mr.")

    detected_lang = detect_language_safe(text)

    if detected_lang == "unknown":
        raise ValueError("Language could not be detected. Please enter a longer sentence.")

    if detected_lang not in LANGUAGE_LABELS:
        raise ValueError(
            "This demo currently supports only English, Hindi, and Marathi input."
        )

    if detected_lang == "en":
        english_text = text
    else:
        english_text = translate_text(text, target_lang="en", source_lang=detected_lang)

    english_summary = summarize_text(english_text)

    if output_lang == "en":
        final_output = english_summary
    else:
        final_output = translate_text(
            english_summary,
            target_lang=output_lang,
            source_lang="en",
        )

    return {
        "detected_language": detected_lang,
        "english_text": english_text,
        "english_summary": english_summary,
        "final_output": final_output,
    }


def render_header():
    """
    Render the page title and description.
    """
    st.set_page_config(
        page_title="Multilingual AI System",
        page_icon="🌐",
        layout="wide",
    )

    st.title("Multilingual AI System")
    st.write(
        "A browser-based AI project for translation, summarization, question answering, "
        "and an agentic workflow using English, Hindi, and Marathi."
    )


def render_sidebar():
    """
    Render the sidebar instructions.
    """
    st.sidebar.header("Project Guide")
    st.sidebar.write("Supported languages:")
    st.sidebar.write("- English (`en`)")
    st.sidebar.write("- Hindi (`hi`)")
    st.sidebar.write("- Marathi (`mr`)")
    st.sidebar.info(
        "Translation uses internet. Summarization and Q&A run locally and respond quickly."
    )
    st.sidebar.markdown(
        "**Workflow:** `Input -> Detect Language -> Translate -> Summarize -> Output`"
    )


def render_translation_tab():
    """
    UI for text translation.
    """
    st.subheader("Translate Text")
    source_lang = st.selectbox(
        "Select source language",
        options=list(LANGUAGE_LABELS.keys()),
        format_func=lambda code: f"{LANGUAGE_LABELS[code]} ({code})",
        key="translate_source",
    )
    target_lang = st.selectbox(
        "Select target language",
        options=list(LANGUAGE_LABELS.keys()),
        format_func=lambda code: f"{LANGUAGE_LABELS[code]} ({code})",
        key="translate_target",
    )
    text = st.text_area(
        "Enter text to translate",
        height=180,
        placeholder="Type your text here...",
        key="translate_text_box",
    )

    if st.button("Translate", key="translate_button", use_container_width=True):
        try:
            with st.spinner("Translating text..."):
                translated_text = translate_text(text, target_lang, source_lang)
            st.success("Translation completed successfully.")
            st.text_area("Translated Output", translated_text, height=180)
        except Exception as error:
            st.error(f"Error: {error}")


def render_summarization_tab():
    """
    UI for text summarization.
    """
    st.subheader("Summarize Text")
    text = st.text_area(
        "Enter English text to summarize",
        height=220,
        placeholder="Paste a paragraph or article here...",
        key="summarize_text_box",
    )

    if st.button("Generate Summary", key="summary_button", use_container_width=True):
        try:
            with st.spinner("Generating summary..."):
                summary = summarize_text(text)
            st.success("Summary generated successfully.")
            st.text_area("Summary Output", summary, height=180)
        except Exception as error:
            st.error(f"Error: {error}")


def render_qa_tab():
    """
    UI for question answering.
    """
    st.subheader("Ask Questions from Text")
    context = st.text_area(
        "Enter context text",
        height=220,
        placeholder="Paste the passage here...",
        key="qa_context",
    )
    question = st.text_input(
        "Enter your question",
        placeholder="Example: What is the main idea of the passage?",
        key="qa_question",
    )

    if st.button("Get Answer", key="qa_button", use_container_width=True):
        try:
            with st.spinner("Finding answer..."):
                answer = answer_question(context, question)
            st.success("Answer generated successfully.")
            st.text_area("Answer", answer, height=100)
        except Exception as error:
            st.error(f"Error: {error}")


def render_workflow_tab():
    """
    UI for the complete agentic workflow.
    """
    st.subheader("Run Agentic Workflow")
    st.caption("Input -> Detect Language -> Translate -> Summarize -> Output")

    text = st.text_area(
        "Enter input text",
        height=220,
        placeholder="Enter English, Hindi, or Marathi text here...",
        key="workflow_text",
    )
    output_lang = st.selectbox(
        "Select final output language",
        options=list(LANGUAGE_LABELS.keys()),
        format_func=lambda code: f"{LANGUAGE_LABELS[code]} ({code})",
        key="workflow_output_lang",
    )

    if st.button("Run Workflow", key="workflow_button", use_container_width=True):
        try:
            with st.spinner("Running full workflow..."):
                result = agentic_workflow(text, output_lang)

            st.success("Workflow completed successfully.")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Detected Language", LANGUAGE_LABELS[result["detected_language"]])
            with col2:
                st.metric("Output Language", LANGUAGE_LABELS[output_lang])

            st.text_area("English Version", result["english_text"], height=150)
            st.text_area("English Summary", result["english_summary"], height=150)
            st.text_area("Final Output", result["final_output"], height=150)

        except Exception as error:
            st.error(f"Error: {error}")

    st.markdown("### Text-Based Flowchart")
    st.code(
        """
+------------------+
|   User Input     |
+------------------+
          |
          v
+------------------+
| Detect Language  |
+------------------+
          |
          v
+------------------------------+
| Translate to English if needed |
+------------------------------+
          |
          v
+------------------+
|  Summarize Text  |
+------------------+
          |
          v
+-----------------------------+
| Translate Summary to Output |
+-----------------------------+
          |
          v
+------------------+
| Final Output     |
+------------------+
        """.strip(),
        language="text",
    )


def render_about_tab():
    """
    UI for project information.
    """
    st.subheader("About This Project")
    st.write(
        "This project demonstrates multilingual natural language processing with "
        "translation, summarization, and question answering in a simple browser interface."
    )
    st.markdown(
        """
**Main Features**
- Translate text between English, Hindi, and Marathi
- Summarize English passages
- Answer questions from a given context
- Run a full agentic workflow

**Functions Used**
- `translate_text()`
- `summarize_text()`
- `answer_question()`
        """
    )


def main():
    """
    Main Streamlit app entry point.
    """
    render_header()
    render_sidebar()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Translation",
            "Summarization",
            "Q&A",
            "Workflow",
            "About",
        ]
    )

    with tab1:
        render_translation_tab()

    with tab2:
        render_summarization_tab()

    with tab3:
        render_qa_tab()

    with tab4:
        render_workflow_tab()

    with tab5:
        render_about_tab()


if __name__ == "__main__":
    main()
