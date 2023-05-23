import streamlit as st
import hashlib
import importlib
import redis
from utils import run_service, LOGIN_KEY, _get_session
import os
base_path = '/'.join(__file__.split("/")[:-1])


SESSION_ID = _get_session()
redis_client = redis.StrictRedis()

try:
    is_login = redis_client.get(LOGIN_KEY + '_' + SESSION_ID)
except Exception as exp:
    is_login = st.session_state.get('is_login', None)
    st.sidebar.error('connect redis failed, login record is disabled')

if is_login is None:
    base_username = os.environ.get('internation_streamlit_username', 'test')
    base_pwd = os.environ.get('internation_streamlit_password', '098f6bcd4621d373cade4e832627b4f6')

    username_and_pwd = st.text_input('input username and pwd, eg test@test')

    if username_and_pwd:
        username, password = username_and_pwd.split("@")
        md5_pwd = hashlib.md5(password.encode('utf-8')).hexdigest()
        if username == base_username and base_pwd == md5_pwd:
            is_login = True
            try:
                redis_client.set(LOGIN_KEY + '_' + SESSION_ID, True, ex=300)
            except Exception as exp2:
                pass
            st.session_state['is_login'] = True

if is_login:
    st.sidebar.info('login success, your session id is %s' % SESSION_ID)
    dirs = []
    for i in os.listdir(base_path + '/toolkits'):
        if i.endswith('.py') or i .startswith('__'):
            continue
        dirs.append(i)

    service = st.sidebar.selectbox('Services', options=dirs)
    if service:
        # only import once
        mod = importlib.import_module('toolkits.%s' % service)
        service_list = getattr(mod, 'SUPPORT_SERVICES', None)
        if service_list:
            run_service(service, service_list)
        else:
            st.sidebar.error('this module not prepared yet')
        st.button('refresh page')
else:
    st.info('login Waited')



