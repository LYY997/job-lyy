# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="就业市场可视化", layout="wide")
st.title("数据岗位就业市场分析仪表盘")
st.caption("数据来源：阿里云天池招聘数据集 | 样本量：5000条")

df = pd.read_csv('jobs_clean.csv', encoding='utf-8-sig')

# ---- 侧边栏筛选器 ----
st.sidebar.header("筛选条件")
cities = sorted(df['city'].dropna().unique().tolist())
selected_cities = st.sidebar.multiselect("选择城市", cities, default=cities[:5])

edu_options = sorted(df['education'].dropna().unique().tolist())
selected_edu = st.sidebar.multiselect("选择学历", edu_options, default=edu_options)

# 过滤数据
filtered = df[df['city'].isin(selected_cities) & df['education'].isin(selected_edu)]

if len(filtered) == 0:
    st.warning("当前筛选条件下没有数据，请调整筛选器")
    st.stop()

# ---- 指标卡 ----
col1, col2, col3 = st.columns(3)
col1.metric("岗位总数", f"{len(filtered)} 个")
col2.metric("平均薪资", f"{filtered['salary_K'].mean():.1f} K/月")
col3.metric("覆盖城市", f"{filtered['city'].nunique()} 个")

# ---- 图表区：两列布局 ----
left, right = st.columns(2)

with left:
    city_counts = filtered['city'].value_counts().head(10).reset_index()
    city_counts.columns = ['城市', '岗位数量']
    fig1 = px.bar(city_counts, x='城市', y='岗位数量', title='各城市岗位数量 Top10',
                  color='岗位数量', color_continuous_scale='Blues')
    st.plotly_chart(fig1, use_container_width=True)

with right:
    city_salary = filtered.groupby('city')['salary_K'].mean().sort_values(ascending=False).head(10).reset_index()
    city_salary.columns = ['城市', '平均薪资K']
    fig2 = px.bar(city_salary, x='城市', y='平均薪资K', title='各城市平均薪资 Top10',
                  color='平均薪资K', color_continuous_scale='Oranges')
    st.plotly_chart(fig2, use_container_width=True)

# ---- 经验薪资箱线图（整行）----
exp_order = ['应届生', '1-3年', '3-5年', '5-10年', '10年以上']
df_exp = filtered[filtered['experience'].isin(exp_order)]
if len(df_exp) > 0:
    fig3 = px.box(df_exp, x='experience', y='salary_K',
                  category_orders={'experience': exp_order},
                  title='不同经验等级薪资分布',
                  labels={'salary_K': '薪资（K/月）', 'experience': '经验要求'},
                  color='experience')
    st.plotly_chart(fig3, use_container_width=True)

# ---- 数据表 ----
st.subheader("筛选后数据预览")
df_show = filtered[['job_title', 'city', 'education', 'experience', 'salary_K']].head(20).copy()
df_show = df_show.astype(str)  
st.dataframe(df_show)
