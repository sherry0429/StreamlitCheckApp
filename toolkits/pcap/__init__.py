import streamlit as st
from .. import BaseView


class PcapTracker(BaseView):

    SERVICE_NAME = 'pcap_tracker'

    def main_page_render(self):
        """ rendered here """
        pcap_names = self.stats_get('pcap_names')
        if pcap_names is None:
            pcap_names = []
        cur_pcap = st.sidebar.selectbox('pcap name', options=pcap_names)
        if cur_pcap:
            res = self.db.selectall("""
            select * from t_pcap_task_detail_action where detail_task_id = (select id from t_pcap_task_detail where task_id = (
            select id from t_pcap_task where task_name='%s'));
            """ % cur_pcap, dict_value=True)
            st.table(res)

    def __init__(self, name):
        """ load data here, use self.stats"""
        super().__init__(name)
        res = self.db.selectall("""
        select task_name from t_pcap_task
        """)
        pcap_names = [i[0] for i in res]
        self.stats_set('pcap_names', pcap_names)


SUPPORT_SERVICES = [
    PcapTracker
]
