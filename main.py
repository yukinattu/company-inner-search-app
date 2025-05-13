"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# 1. ライブラリの読み込み
############################################################
import os
import streamlit as st
from dotenv import load_dotenv
import logging
import traceback

# 自作モジュール
import utils
import components as cn
import constants as ct
from initialize import (
    initialize_session_state,
    initialize_session_id,
    initialize_logger,
    # initialize_retriever  ← コメントアウト（後で戻す）
)

# ✅ ローカル環境用に .env 読み込み
load_dotenv()
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

############################################################
# 2. ページ設定とロガーの初期化
############################################################
st.set_page_config(page_title=ct.APP_NAME)
logger = logging.getLogger(ct.LOGGER_NAME)

############################################################
# 3. 初期化処理（retrieverのみ除外）
############################################################
try:
    initialize_session_state()
    initialize_session_id()
    initialize_logger()
    # initialize_retriever()  ← 一時的に無効化して時間短縮
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        logger.info(ct.APP_BOOT_MESSAGE)
except Exception as e:
    logger.error(f"{ct.INITIALIZE_ERROR_MESSAGE}\n{traceback.format_exc()}")
    st.error(utils.build_error_message(ct.INITIALIZE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    st.stop()

############################################################
# 4. 初期表示
############################################################
cn.display_app_title()
cn.display_select_mode()
cn.display_initial_ai_message()

############################################################
# 5. 会話ログの表示
############################################################
try:
    cn.display_conversation_log()
except Exception as e:
    logger.error(f"{ct.CONVERSATION_LOG_ERROR_MESSAGE}\n{traceback.format_exc()}")
    st.error(utils.build_error_message(ct.CONVERSATION_LOG_ERROR_MESSAGE), icon=ct.ERROR_ICON)
    st.stop()

############################################################
# 6. チャット入力受付
############################################################
chat_message = st.chat_input(ct.CHAT_INPUT_HELPER_TEXT)

############################################################
# 7. チャット処理
############################################################
if chat_message:
    logger.info({"message": chat_message, "application_mode": st.session_state.mode})
    with st.chat_message("user"):
        st.markdown(chat_message)

    res_box = st.empty()
    with st.spinner(ct.SPINNER_TEXT):
        try:
            llm_response = utils.get_llm_response(chat_message)
        except Exception as e:
            logger.error(f"{ct.GET_LLM_RESPONSE_ERROR_MESSAGE}\n{traceback.format_exc()}")
            st.error(utils.build_error_message(ct.GET_LLM_RESPONSE_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            st.stop()

    with st.chat_message("assistant"):
        try:
            if st.session_state.mode == ct.ANSWER_MODE_1:
                content = cn.display_search_llm_response(llm_response)
            elif st.session_state.mode == ct.ANSWER_MODE_2:
                content = cn.display_contact_llm_response(llm_response)
            logger.info({"message": content, "application_mode": st.session_state.mode})
        except Exception as e:
            logger.error(f"{ct.DISP_ANSWER_ERROR_MESSAGE}\n{traceback.format_exc()}")
            st.error(utils.build_error_message(ct.DISP_ANSWER_ERROR_MESSAGE), icon=ct.ERROR_ICON)
            st.stop()

    st.session_state.messages.append({"role": "user", "content": chat_message})
    st.session_state.messages.append({"role": "assistant", "content": content})
