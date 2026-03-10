import pandas as pd
import re

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score


# LOAD DATASET
df = pd.read_csv("SMSSmishCollection.txt", sep="\t", names=["label","message"])

print("Dataset size:", df.shape)
print(df["label"].value_counts())


# CONVERT LABELS TO NUMBERS
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


# SPLIT DATA
X_train, X_test, y_train, y_test = train_test_split(
    df["message"], df["label"], test_size=0.2, random_state=42
)


# TEXT → NUMBERS
vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,3))

X_train = vectorizer.fit_transform(X_train)
X_test = vectorizer.transform(X_test)


# TRAIN MODEL
model = MultinomialNB()
model.fit(X_train, y_train)


# TEST ACCURACY
y_pred = model.predict(X_test)

print("\nModel Accuracy:", accuracy_score(y_test, y_pred))

#spamwords
scam_keywords = [
    "bank","account","password","otp","verify",
    "urgent","click","link","prize","win",
    "payment","blocked","suspended","update"
]



# USER INPUT
print("\nEnter a message to check:")

user_input = input()

clean_input = clean_text(user_input)

vector_input = vectorizer.transform([clean_input])

prediction = model.predict(vector_input)

probability = model.predict_proba(vector_input)

prob = probability[0][1]

keyword_flag = False

for word in scam_keywords:
    if word in user_input.lower():
        keyword_flag = True
        break
    
if prediction[0] == 1 or keyword_flag:
    print("🚨 Possible Scam / Smishing Message")
else:
    print("✅ Message looks Safe")

print("Scam Probability:", round(prob,2))

