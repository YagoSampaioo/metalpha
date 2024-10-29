import requests
import pandas as pd
import streamlit as st

# Configurações da página
st.set_page_config(page_title="Dashboard de Campanhas", layout="wide")

# Configurações do login
USERNAME = 'admin@assessorialpha.com'  # Altere para o seu usuário
PASSWORD = 'Alpha123'     # Altere para a sua senha

# Função para verificar credenciais
def check_credentials(username, password):
    return username == USERNAME and password == PASSWORD

# Verificar se o usuário está autenticado
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Página de login
if not st.session_state.authenticated:
    st.title("Login")
    username_input = st.text_input("Usuário")
    password_input = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if check_credentials(username_input, password_input):
            st.session_state.authenticated = True
            st.success("Login bem-sucedido!")
        else:
            st.error("Usuário ou senha incorretos.")
else:
    # Código do aplicativo após o login
    access_token = 'EAAOUAvlbqgYBO9Np8hbuHo8XIURqEjRGuZCJUPMm6ZAzGbOQ2DxQRZBolzoD9hKfaDuySGF4fsh6rb229KL9b8YQ1hqsRQfKfq5GVeZBIGHJs8zUhaU8uyy9ydZCriZC7D4wFGk7RWHG3iZCQZC4ZCTKhKIkMKDUZChr9UKZAQc5zNxGpVBK4gP8Y5xOPyInvgUOOGyLWhqoHGvvrFgqlueNTiRPzXtcqZAX1o1c1QZDZD'
    ad_account_id = 'act_1021480798184024'

    # URL para obter as campanhas
    campaigns_url = (
        f'https://graph.facebook.com/v21.0/{ad_account_id}'
        f'?fields=campaigns{{name,campaign_group_active_time,ads{{name,updated_time,insights{{'
        f'conversions,action_values,actions,clicks,marketing_messages_delivery_rate,cpc,cpm,cpp,ctr,'
        f'cost_per_conversion,cost_per_action_type,conversion_values}},copies}}}}&access_token={access_token}'
    )

    # Fazer a solicitação à API
    response = requests.get(campaigns_url)

    if response.status_code == 200:
        campaigns_data = response.json().get('campaigns', {}).get('data', [])
    else:
        st.error(f"Erro ao buscar campanhas: {response.status_code} - {response.text}")
        campaigns_data = []

    # Processar os dados das campanhas
    campaigns_info = []
    campaign_ads_mapping = {}

    for campaign in campaigns_data:
        campaign_name = campaign.get('name', 'N/A')
        campaigns_info.append(campaign_name)

        # Adicionar anúncios ao mapeamento
        ads = campaign.get('ads', {}).get('data', [])
        campaign_ads_mapping[campaign_name] = []

        for ad in ads:
            insights = ad.get('insights', {}).get('data', [{}])[0]
            ad_info = {
                'Nome': ad.get('name', 'N/A'),
                'Atualizado em': ad.get('updated_time', 'N/A'),
                'Conversões': insights.get('conversions', 0),
                'Custo por Resultado': insights.get('action_values', [{}])[0].get('value', 0),
                'Cliques': insights.get('clicks', 0),
                'Custo por Clique (CPC)': insights.get('cpc', 0),
                'Custo por Mil Impressões (CPM)': insights.get('cpm', 0),
                'Custo por Compra (CPP)': insights.get('cpp', 0),
                'Taxa de Cliques (CTR)': insights.get('ctr', 0),
                'Custo por Conversão': insights.get('cost_per_conversion', 0),
                'Mensagens Entregues (%)': insights.get('marketing_messages_delivery_rate', 0),
            }
            campaign_ads_mapping[campaign_name].append(ad_info)

    # Menu suspenso para selecionar a campanha
    selected_campaign = st.selectbox("Selecione uma Campanha", options=campaigns_info)

    # Mostrar os anúncios da campanha selecionada
    if selected_campaign:
        ads_list = campaign_ads_mapping.get(selected_campaign, [])
        if ads_list:
            st.write(f"Anúncios na Campanha: **{selected_campaign}**")
            # Usar uma tabela que preenche a tela
            ads_df = pd.DataFrame(ads_list)
            st.dataframe(ads_df.style.set_table_attributes('style="width: 100%;"'))
        else:
            st.write(f"Nenhum anúncio encontrado para a campanha: **{selected_campaign}**")
