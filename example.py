import openai
import streamlit as st
import toml
from streamlit_chat import message

# Set page title and header
st.set_page_config(page_title="WDC", page_icon=":globe_with_meridians:")

st.markdown("<h1 style='text-align: center;'>World Disaster Center 🌐</h1>", unsafe_allow_html=True)

# Load API key from environment variable
openai.api_key = st.secrets["API_KEY"]


# Initialize session state
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{"role": "system", "content": "You are a helpful assistant for disaster and natural catastrophe information."}]
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0

# Sidebar for model selection, cost display, and conversation clearing
st.sidebar.title("World Disaster Center")
#model_name = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
model_name = "GPT-3.5"
counter_placeholder = st.sidebar.empty()
# counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
clear_button = st.sidebar.button("Clear Conversation", key="clear")

# Map model names to OpenAI model IDs
model = "gpt-3.5-turbo" #if model_name == "GPT-3.5" #else "gpt-4"

# Clear conversation
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [{"role": "system", "content": "You are a helpful assistant for disaster and natural catastrophe information."}]
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_cost'] = 0.0
    st.session_state['total_tokens'] = []
    counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")

# Function to check if the question is disaster-related
def is_disaster_related(question):
    keywords = keywords = [
    "disaster", "catastrophe", "emergency", "evacuation", "rescue", "flood", "fire", "earthquake", "hurricane", "cyclone", "tsunami", "landslide", "volcano", "drought", "storm", "tornado", "hailstorm", "blizzard", "avalanche", "heatwave", "aftershock", "wildfire", "mudslide", "storm surge", "lightning", "sinkhole", "famine", "epidemic", "contamination", "radiation", "explosion", "meltdown", "pestilence", "plague", "collapse", "severe weather", "sandstorm", "tropical storm",
    "désastre", "catastrophe", "urgence", "évacuation", "secours", "inondation", "incendie", "tremblement de terre", "ouragan", "cyclone", "tsunami", "glissement de terrain", "volcan", "sécheresse", "tempête", "tornade", "orage de grêle", "blizzard", "avalanche", "canicule", "réplique", "feu de forêt", "coulée de boue", "onde de tempête", "foudre", "dolline", "famine", "épidémie", "contamination", "radiation", "explosion", "fusion", "peste", "effondrement", "intempéries", "tempête de sable", "tempête tropicale",
    "desastre", "catástrofe", "emergencia", "evacuación", "rescate", "inundación", "incendio", "terremoto", "huracán", "ciclón", "tsunami", "deslizamiento", "volcán", "sequía", "tormenta", "tornado", "granizada", "ventisca", "avalancha", "ola de calor", "réplica", "incendio forestal", "deslizamiento de lodo", "marejada ciclónica", "relámpago", "sumidero", "hambruna", "epidemia", "contaminación", "radiación", "explosión", "fusión", "pestilencia", "plaga", "colapso", "clima severo", "tormenta de arena", "tormenta tropical",
    "desastre", "catástrofe", "emergência", "evacuação", "resgate", "inundação", "incêndio", "terremoto", "furacão", "ciclone", "tsunami", "deslizamento de terra", "vulcão", "seca", "tempestade", "tornado", "tempestade de granizo", "nevasca", "avalanche", "onda de calor", "réplica", "incêndio florestal", "deslizamento de lama", "ressaca", "raio", "dolina", "fome", "epidemia", "contaminação", "radiação", "explosão", "colapso", "praga", "peste", "colapso", "tempo severo", "tempestade de areia", "tempestade tropical",
    "бедствие", "катастрофа", "чрезвычайная ситуация", "эвакуация", "спасение", "наводнение", "пожар", "землетрясение", "ураган", "циклон", "цунами", "оползень", "вулкан", "засуха", "шторм", "торнадо", "град", "метель", "лавина", "жара", "афтершок", "лесной пожар", "оползень из грязи", "штормовой нагон", "молния", "карстовая воронка", "голод", "эпидемия", "заражение", "радиация", "взрыв", "расплавление", "мор", "чума", "коллапс", "сильная погода", "песчаная буря", "тропический шторм"
]
    return any(keyword in question.lower() for keyword in keywords)

# Generate response
def generate_response(prompt):
    if not is_disaster_related(prompt):
        response = "I can only answer questions related to disasters and catastrophes. Please rephrase your question."
        return response, 0, 0, 0

    st.session_state['messages'].append({"role": "user", "content": prompt})

    try:
        completion = openai.ChatCompletion.create(
            model=model,
            messages=st.session_state['messages']
        )
        response = completion.choices[0].message.content
        st.session_state['messages'].append({"role": "assistant", "content": response})

        total_tokens = completion.usage.total_tokens
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens

        return response, total_tokens, prompt_tokens, completion_tokens

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return "", 0, 0, 0

# Chat containers
response_container = st.container()
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['model_name'].append(model_name)
        st.session_state['total_tokens'].append(total_tokens)


if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(f"🌐 {st.session_state['generated'][i]}", key=str(i))




