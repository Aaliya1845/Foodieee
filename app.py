import streamlit as st
import pandas as pd
import re

st.set_page_config(
    page_title="AI Food Recommendation System",
    layout="wide"
)

st.title("🍲 AI Food Recommendation System")

@st.cache_data
def load_data():

    df = pd.read_csv("cleaned_recipes.csv")

    return df


df = load_data()

# Detect columns automatically

name_col = None
ing_col = None
inst_col = None
cuisine_col = None
time_col = None
img_col = None

for c in df.columns:

    cl = c.lower()

    if "recipe" in cl and name_col is None:

        name_col = c

    if "ingredient" in cl and ing_col is None:

        ing_col = c

    if "instruction" in cl and inst_col is None:

        inst_col = c

    if "cuisine" in cl:

        cuisine_col = c

    if "time" in cl:

        time_col = c

    if "image" in cl:

        img_col = c


# Hindi + Marathi synonyms

synonyms = {

    "aloo":"potato",

    "batata":"potato",

    "बटाटा":"potato",

    "pyaz":"onion",

    "kanda":"onion",

    "कांदा":"onion",

    "tamatar":"tomato",

    "टोमॅटो":"tomato",

    "chawal":"rice",

    "tandul":"rice",

    "तांदूळ":"rice",

    "mirchi":"chilli",

    "मिरची":"chilli"

}


def normalize(text):

    words = text.lower().split()

    result = []

    for w in words:

        result.append(

            synonyms.get(w,w)

        )

    return " ".join(result)


def short_steps(text):

    text = str(text)

    parts = text.split(".")

    ans = []

    for i in range(

        min(4,len(parts))

    ):

        if parts[i].strip()!="":

            ans.append(

                f"{i+1}. {parts[i].strip()}"

            )

    return "\n".join(ans)


def recommend(user_input):

    user_words = set(

        re.findall(

            r"\w+",

            user_input.lower()

        )

    )

    scores = []

    for _,row in df.iterrows():

        recipe_words = set(

            re.findall(

                r"\w+",

                str(

                    row[ing_col]

                ).lower()

            )

        )

        score = len(

            user_words.intersection(

                recipe_words

            )

        )

        scores.append(score)

    temp = df.copy()

    temp["score"] = scores

    temp = temp.sort_values(

        by="score",

        ascending=False

    )

    return temp.head(10)


user_input = st.text_input(

    "Ingredients",

    placeholder="rice tomato potato OR aloo pyaz tamatar"

)

if st.button(

    "Get Recipes"

):

    if user_input.strip()=="":

        st.warning(

            "Enter ingredients"

        )

    else:

        user_input = normalize(

            user_input

        )

        st.success(

            f"Input : {user_input}"

        )

        results = recommend(

            user_input

        )

        for _,row in results.iterrows():

            st.markdown(

                f"## 🍲 {row[name_col]}"

            )

            if cuisine_col:

                st.write(

                    f"🍛 Cuisine : {row[cuisine_col]}"

                )

            if time_col:

                st.write(

                    f"⏱ Time : {row[time_col]}"

                )

            st.write(

                "🥬 Ingredients"

            )

            st.write(

                row[ing_col]

            )

            if inst_col:

                st.write(

                    "👨‍🍳 Short Steps"

                )

                st.text(

                    short_steps(

                        row[inst_col]

                    )

                )

            st.write(

                f"📊 Match Score : {row['score']}"

            )

            if img_col:

                try:

                    if pd.notna(

                        row[img_col]

                    ):

                        st.image(

                            row[img_col],

                            width=300

                        )

                except:

                    st.write(

                        "Image not available"

                    )

            st.write("---")
