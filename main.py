# System entry point
import streamlit as st
from core.logger import logger

def main():
    st.title('BIST AI Tahmin Sistemi')
    logger.info('System started')

if __name__ == '__main__':
    main()
