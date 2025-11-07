import streamlit as st
from ui.layout import show_sidebar, show_main_page

st.set_page_config(
    page_title="Simulador de Remuneração Internacional",
    layout="wide",
)

def main():
    show_sidebar()
    show_main_page()

if __name__ == "__main__":
    main()
