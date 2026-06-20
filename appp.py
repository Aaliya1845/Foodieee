import streamlit as st
import pandas as pd
import re

st.set_page_config(
    page_title="AI Food Recommendation System",
    layout="wide"
)

st.title("🍲 AI Food Recommendation System")

# ---------- LOAD DATA ----------

@st.cache_data
def load_data():

    recipes = pd.read_csv("cleaned_recipes.csv")

    nutrition = pd.read_csv("food.csv.zip")

    nutrition = nutrition[
        [
            "Description",
            "Data.Kilocalories",
            "Data.Protein",
            "Data.Carbohydrate",
            "Data.Fat.Total Lipid"
        ]
    ]

    nutrition.columns = [

        "food_name",

        "calories",

        "protein",

        "carbs",

        "fat"

    ]

    nutrition["food_name"] = (

        nutrition["food_name"]

        .astype(str)

        .str.lower()

    )

    return recipes, nutrition


df, nutrition_df = load_data()

# ---------- HINDI / MARATHI ----------

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


# ---------- SHORT STEPS ----------

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


# ---------- NUTRITION ----------

def nutrition_estimate(user_input):

    ingredients = user_input.lower().split()

    cal = 0

    protein = 0

    carbs = 0

    fat = 0

    found = []

    for ing in ingredients:

        match = nutrition_df[

            nutrition_df["food_name"]

            .str.contains(

                ing,

                case=False,

                na=False

            )

        ]

        if len(match)>0:

            row = match.iloc[0]

            found.append(ing)

            cal += row["calories"]

            protein += row["protein"]

            carbs += row["carbs"]

            fat += row["fat"]

    st.subheader("🥗 Estimated Nutrition")

    st.write(

        f"Matched Foods : {', '.join(found)}"

    )

    st.write(

        f"🔥 Calories : {round(cal,2)} kcal"

    )

    st.write(

        f"💪 Protein : {round(protein,2)} g"

    )

    st.write(

        f"🍞 Carbs : {round(carbs,2)} g"

    )

    st.write(

        f"🥑 Fat : {round(fat,2)} g"

    )


# ---------- RECOMMEND ----------

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

                    row["Cleaned-Ingredients"]

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


# ---------- UI ----------

user_input = st.text_input(

    "Ingredients",

    placeholder="rice tomato potato OR aloo pyaz tamatar"

)

if st.button(

    "Get Recipes"

):

    if user_input.strip()=="":

        st.warning(

            "Please enter ingredients"

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

        nutrition_estimate(

            user_input

        )

        st.write("---")

        for _,row in results.iterrows():

            st.markdown(

                f"## 🍲 {row['TranslatedRecipeName']}"

            )

            st.write(

                f"🍛 Cuisine : {row['Cuisine']}"

            )

            st.write(

                f"⏱ Time : {row['TotalTimeInMins']} mins"

            )

            st.write(

                "🥬 Ingredients"

            )

            st.write(

                row["TranslatedIngredients"]

            )

            st.write(

                "👨‍🍳 Short Steps"

            )

            st.text(

                short_steps(

                    row["TranslatedInstructions"]

                )

            )

            st.write(

                f"📊 Match Score : {row['score']}"

            )

            try:

                if pd.notna(

                    row["image-url"]

                ):

                    st.image(

                        row["image-url"],

                        width=300

                    )

            except:

                st.write(

                    "Image not available"

                )

            st.write("---")
