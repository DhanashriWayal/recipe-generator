import streamlit as st
import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Recipe Generator",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .recipe-box {
        background-color: #f8f9fa;
        padding: 2.5rem;
        border-radius: 15px;
        border-left: 6px solid #FF6B6B;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        white-space: pre-line;
        line-height: 1.6;
    }
    .ingredient-input {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        margin: 1rem 0;
    }
    .stButton button {
        background-color: #FF6B6B;
        color: white;
        font-weight: bold;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        border: none;
        font-size: 1.1rem;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #FF5252;
        color: white;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin-bottom: 1rem;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


class OpenRouterRecipeGenerator:
    def __init__(self):
        # Get API key from environment variable or use directly
        self.api_key = os.getenv('OPENROUTER_API_KEY',
                                 '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')
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://recipe-generator.streamlit.app",
            "X-Title": "AI Recipe Generator"
        }

    def generate_recipe(self, ingredients, cuisine="Any", diet="Any"):
        try:
            # Enhance the prompt based on user preferences
            enhanced_ingredients = ingredients
            if cuisine != "Any":
                enhanced_ingredients += f", {cuisine.lower()} cuisine style"
            if diet != "Any":
                enhanced_ingredients += f", {diet.lower()} diet"

            prompt = f"""
Create a detailed, practical recipe using mainly these ingredients: {enhanced_ingredients}.

IMPORTANT: Use this exact format:

RECIPE NAME: [Creative name]
PREP TIME: [e.g., 15 minutes]
COOK TIME: [e.g., 30 minutes]
DIFFICULTY: [Easy/Medium/Hard]
SERVINGS: [number]

INGREDIENTS:
- [Specific quantities and ingredients]
- [You can add basic pantry items like salt, oil, etc.]

INSTRUCTIONS:
1. [Clear step-by-step instructions]
2. [Number each step]
3. [Be specific with cooking times and temperatures]

NUTRITIONAL INFO (per serving):
- Calories: [estimate]
- Protein: [g]
- Carbohydrates: [g]
- Fat: [g]

TIPS: [Practical cooking tips]

Make the recipe realistic for home cooking.
"""

            payload = {
                "model": "meta-llama/llama-3-70b-instruct:free",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1500,
                "temperature": 0.7,
                "top_p": 0.9
            }

            response = requests.post(self.url, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                error_msg = f"API Error: {response.status_code}"
                try:
                    error_detail = json.loads(response.text)
                    error_msg += f" - {error_detail.get('error', {}).get('message', 'Unknown error')}"
                except:
                    error_msg += f" - {response.text}"
                return error_msg

        except requests.exceptions.Timeout:
            return "❌ Request timed out. Please try again."
        except Exception as e:
            return f"❌ Error: {str(e)}"


def main():
    # Header
    st.markdown('<div class="main-header">🍳 AI Recipe Generator</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("🎯 About")
        st.info(
            "Welcome to the AI Recipe Generator! "
            "This tool creates delicious recipes based on ingredients you have available. "
            "Just enter what's in your kitchen and let the AI work its magic! ✨"
        )

        st.header("📝 How to Use")
        st.write("1. Enter your ingredients in the main area")
        st.write("2. Select your preferences (optional)")
        st.write("3. Click 'Generate Recipe'")
        st.write("4. Download or copy your recipe!")

        st.header("💡 Tips")
        st.write("• Be specific with ingredients")
        st.write("• The more ingredients, the more creative the recipe!")
        st.write("• Add preferences like 'Italian style' or 'vegetarian'")

        st.header("🔧 Powered By")
        st.write("**OpenRouter AI**")
        st.write("Using Llama 3 70B model")
        st.write("Free • Fast • Reliable")

        st.header("🚀 Quick Examples")
        if st.button("Chicken & Rice"):
            st.session_state.ingredients = "chicken, rice, vegetables"
        if st.button("Pasta Dish"):
            st.session_state.ingredients = "pasta, tomatoes, garlic, basil"
        if st.button("Vegetarian"):
            st.session_state.ingredients = "tofu, broccoli, carrots, rice"

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 Enter Your Ingredients")

        with st.container():
            st.markdown('<div class="ingredient-input">', unsafe_allow_html=True)
            ingredients = st.text_area(
                "What ingredients do you have? (separate with commas)",
                placeholder="Example: chicken breast, rice, tomatoes, onions, garlic, olive oil, spices...",
                height=120,
                key="ingredients",
                value=st.session_state.get('ingredients', '')
            )
            st.markdown('</div>', unsafe_allow_html=True)

        # Recipe preferences
        st.subheader("⚙️ Recipe Preferences")

        col1a, col1b = st.columns(2)
        with col1a:
            cuisine = st.selectbox(
                "Cuisine Style:",
                ["Any", "Italian", "Mexican", "Asian", "Indian", "Mediterranean", "American", "French", "Thai"],
                key="cuisine"
            )

        with col1b:
            diet = st.selectbox(
                "Dietary Preference:",
                ["Any", "Vegetarian", "Vegan", "Gluten-free", "Low-carb", "Dairy-free", "Keto"],
                key="diet"
            )

        # Generate button
        generate_btn = st.button(
            "🚀 Generate Recipe!",
            type="primary",
            use_container_width=True,
            key="generate"
        )

    with col2:
        st.subheader("📄 Your Generated Recipe")

        # Placeholder for recipe output
        recipe_placeholder = st.empty()

        if generate_btn:
            if not ingredients.strip():
                st.error("❌ Please enter some ingredients!")
            else:
                with st.spinner("🔄 AI is creating your custom recipe... This may take 10-20 seconds."):
                    try:
                        # Load generator and create recipe
                        generator = OpenRouterRecipeGenerator()
                        recipe = generator.generate_recipe(ingredients, cuisine, diet)

                        # Display recipe in a nice box
                        with recipe_placeholder.container():
                            st.markdown('<div class="recipe-box">', unsafe_allow_html=True)

                            if recipe.startswith("❌") or "Error" in recipe or "timeout" in recipe.lower():
                                st.markdown(f'<div class="error-box">{recipe}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="success-box">✅ Recipe generated successfully!</div>',
                                            unsafe_allow_html=True)
                                st.markdown("---")
                                st.markdown(recipe)

                                # Download button
                                st.download_button(
                                    label="📥 Download Recipe",
                                    data=recipe,
                                    file_name="my_ai_recipe.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )

                            st.markdown('</div>', unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"❌ Unexpected error: {str(e)}")

        # Show instructions when no recipe generated yet
        if not generate_btn:
            with recipe_placeholder.container():
                st.info(
                    "👆 Enter your ingredients and click 'Generate Recipe' to see your custom recipe here! "
                    "The AI will create a complete recipe with instructions, cooking times, and nutritional info. "
                    "Try the quick examples in the sidebar! 🍽️"
                )


if __name__ == "__main__":
    main()
