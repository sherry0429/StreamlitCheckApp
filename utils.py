import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

LOGIN_KEY = 'streamlit_login'


def _get_session():
    ctx = get_script_run_ctx()
    session_id = ctx.session_id
    return session_id


def run_service(cluster_name, service_list):
    if service_list is None:
        return
    services = {}
    for cls in service_list:
        services[cls.SERVICE_NAME] = cls
    child = st.sidebar.selectbox('child services', options=services.keys(), index=0)
    if child:
        tmp_cls = services.get(child)
        if tmp_cls:
            tmp_cls(cluster_name).render()
