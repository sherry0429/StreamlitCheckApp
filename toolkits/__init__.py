import streamlit as st
try:
    from third.dbconnection import Dbconnection
    from third.redis_helper import RedisHelper
    # use psycopg2 and redis replace this
except Exception as import_exp:
    st.sidebar.error('db & redis for service init failed, %s' % str(import_exp))


class BaseView(object):

    SERVICE_NAME = ''

    def __init__(self, name):
        self.name = name
        self.stats = {
            '%s_redis' % self.name: False,
            '%s_db' % self.name: False
        }
        self.db = None
        self.redis = None
        try:
            self.db = Dbconnection()
            self.stats['%s_db' % self.name] = True
        except Exception as exp:
            st.sidebar.error('db init failed %s' % str(exp))
        try:
            self.redis = RedisHelper()
            self.stats['%s_redis' % self.name] = True
        except Exception as exp:
            st.sidebar.error('redis init failed %s' % str(exp))

    def init_db_with_other_name(self, db_name):
        try:
            db = Dbconnection(db_name=db_name)
            self.stats['%s_%s_db' % (self.name, db_name)] = True
        except Exception as exp:
            st.sidebar.error('%s db init failed %s' % (db_name, str(exp)))
            db = None
        return db

    def stats_init(self):
        for k, v in self.stats.items():
            st.session_state['%s_%s' % (self.name, k)] = v

    def stats_get(self, k):
        return st.session_state.get('%s_%s' % (self.name, k), None)

    def stats_set(self, k, v):
        st.session_state['%s_%s' % (self.name, k)] = v

    def main_page_render(self):
        raise NotImplementedError

    def render(self):
        self.main_page_render()