import streamlit as st
import pandas as pd
import re

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


# LOAD DATASET
df = pd.read_csv("SMSSmishCollection.txt", sep="\t", names=["label","message"])

df["label"] = df["label"].map({
    "ham":0,
    "smish":1
})


# CLEAN TEXT
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text


df["message"] = df["message"].apply(clean_text)


# TRAIN MODEL
X_train, X_test, y_train, y_test = train_test_split(
    df["message"], df["label"], test_size=0.2, random_state=42
)

vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2))

X_train = vectorizer.fit_transform(X_train)

model = MultinomialNB()

model.fit(X_train, y_train)


# WEBPAGE
st.title("📱 AI Scam Message Detector")

st.write("Enter a message to check if it is a scam or safe.")


user_input = st.text_area("Enter Message")


scam_keywords = [
    "bank","account","password","otp","verify",
    "urgent","click","link","prize","win",
    "payment","blocked","suspended","update"
]


if st.button("Check Message"):

    clean_input = clean_text(user_input)

    vector_input = vectorizer.transform([clean_input])

    prediction = model.predict(vector_input)

    probability = model.predict_proba(vector_input)

    keyword_flag = any(word in user_input.lower() for word in scam_keywords)

    prob = probability[0][1]

    if prediction[0] == 1 or keyword_flag:
        st.error("🚨 Possible Scam / Smishing Message")
    else:
        st.success("✅ Message looks Safe")

    st.write("Scam Probability:", round(prob,2))