"""
五红将分析工具 - Streamlit App
数据来源: htzx_5star_heroes.json + htzx_5star_rankings.json
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# ============ 数据加载 ============
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "htzx_5star_heroes.json"), encoding="utf-8") as f:
        heroes = json.load(f)
    with open(os.path.join(base, "htzx_5star_rankings.json"), encoding="utf-8") as f:
        rankings = json.load(f)
    return heroes, rankings

heroes, rankings = load_data()

# ============ 数据预处理 ============
# 从 heroes 构建 DataFrame（只用5星，211个）
records = []
for h in heroes:
    attr = h.get("attributes", {})
    main_skill = h.get("mainSkill", {})
    self_skill = h.get("selfSkill", {})
    exchange_skill = h.get("exchangeSkill") or {}
    records.append({
        "编号": h["id"],
        "武将名": h["name"],
        "阵营": h.get("faction", ""),
        "星级": h.get("stars", ""),
        "cost": h.get("cost", ""),
        "兵种": h.get("troop", ""),
        "兵种进化": h.get("troopEvolution", ""),
        "武力_基础": attr.get("force", {}).get("base", 0),
        "武力_成长": attr.get("force", {}).get("growth", 0),
        "防御_基础": attr.get("defense", {}).get("base", 0),
        "防御_成长": attr.get("defense", {}).get("growth", 0),
        "智力_基础": attr.get("intellect", {}).get("base", 0),
        "智力_成长": attr.get("intellect", {}).get("growth", 0),
        "速度_基础": attr.get("speed", {}).get("base", 0),
        "速度_成长": attr.get("speed", {}).get("growth", 0),
        "政治_基础": attr.get("politics", {}).get("base", 0),
        "政治_成长": attr.get("politics", {}).get("growth", 0),
        "魅力_基础": attr.get("charm", {}).get("base", 0),
        "魅力_成长": attr.get("charm", {}).get("growth", 0),
        "主战技": main_skill.get("name", ""),
        "主战技_品质": main_skill.get("quality", ""),
        "主战技_类型": main_skill.get("type", ""),
        "主战技_概率": main_skill.get("probability", ""),
        "主战技_描述": main_skill.get("desc", ""),
        "自带技能": self_skill.get("name", ""),
        "自带技能_品质": self_skill.get("quality", ""),
        "自带技能_类型": self_skill.get("type", ""),
        "自带技能_描述": self_skill.get("desc", ""),
        "传承技能": exchange_skill.get("name", ""),
        "传承技能_品质": exchange_skill.get("quality", ""),
        "传承技能_类型": exchange_skill.get("type", ""),
        "传承技能_描述": exchange_skill.get("desc", ""),
        "缘分": " / ".join([b["name"] for b in h.get("bonds", [])]),
        "主战技标签": h.get("tags", {}).get("mainSkill", ""),
        "自带技标签": h.get("tags", {}).get("selfSkill", ""),
        "图片_icon": h.get("images", {}).get("icon", ""),
        "图片_big": h.get("images", {}).get("big", ""),
    })

df = pd.DataFrame(records)
df["总属性"] = df["武力_基础"] + df["防御_基础"] + df["智力_基础"] + df["速度_基础"] + df["政治_基础"] + df["魅力_基础"]

# 六个维度的中英文映射
DIM_MAP = {
    "武力": ("force", "⚔️"),
    "防御": ("defense", "🛡️"),
    "智力": ("intellect", "🧠"),
    "速度": ("speed", "💨"),
    "政治": ("politics", "📋"),
    "魅力": ("charm", "✨"),
}

# 六维基础值列
BASE_COLS = ["武力_基础", "防御_基础", "智力_基础", "速度_基础", "政治_基础", "魅力_基础"]
DIM_COL_CN = {
    "武力_基础": "武力", "防御_基础": "防御", "智力_基础": "智力",
    "速度_基础": "速度", "政治_基础": "政治", "魅力_基础": "魅力",
}

# ============ 页面配置 ============
st.set_page_config(
    page_title="五红将分析工具",
    page_icon="📊",
    layout="wide",
)

st.title("📊 五红将分析工具")
st.markdown("基于官网数据 · 六维属性全解析 · 助力配将决策")

# ============ 侧边栏 ============
st.sidebar.header("🔍 筛选条件")

all_factions = ["全部"] + sorted(df["阵营"].dropna().unique().tolist())
all_costs = ["全部"] + sorted([str(c) for c in df["cost"].dropna().unique()], key=lambda x: int(x) if x.isdigit() else 99)
all_troops = ["全部"] + sorted(df["兵种"].dropna().unique().tolist())

sel_faction = st.sidebar.selectbox("阵营", all_factions)
sel_cost = st.sidebar.selectbox("Cost", all_costs)
sel_troop = st.sidebar.selectbox("兵种", all_troops)
sel_dim = st.sidebar.selectbox("默认排序维度", ["总属性", "武力_基础", "防御_基础", "智力_基础", "速度_基础", "政治_基础", "魅力_基础"])

# 应用筛选
mask = pd.Series(True, index=df.index)
if sel_faction != "全部":
    mask &= df["阵营"] == sel_faction
if sel_cost != "全部":
    mask &= df["cost"].astype(str) == sel_cost
if sel_troop != "全部":
    mask &= df["兵种"] == sel_troop

df_filtered = df[mask].copy()

# ============ 概览卡片 ============
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
col1.metric("武将总数", len(df_filtered))
col2.metric("涉及阵营", df_filtered["阵营"].nunique() if len(df_filtered) else 0)
col3.metric("涉及兵种", df_filtered["兵种"].nunique() if len(df_filtered) else 0)
col4.metric("平均总属性", f"{df_filtered['总属性'].mean():.1f}" if len(df_filtered) else "N/A")

st.markdown("---")

# ============ Tab 1: 六维排行榜 ============
tab1, tab2, tab3, tab4 = st.tabs(["📈 六维排行榜", "🔎 武将搜索", "⚔️ 武将对比", "📋 缘分速查"])

with tab1:
    st.subheader("六维属性排行榜")
    dim_col = st.selectbox("选择维度", BASE_COLS, index=BASE_COLS.index(sel_dim) if sel_dim in BASE_COLS else 0,
                           format_func=lambda x: DIM_COL_CN.get(x, x))
    dim_label = DIM_COL_CN.get(dim_col, dim_col)

    # 排序
    df_sorted = df_filtered.sort_values(dim_col, ascending=False).head(50).reset_index(drop=True)
    df_sorted.index = df_sorted.index + 1
    df_sorted.index.name = "排名"

    display_cols = ["武将名", "阵营", "cost", "兵种", dim_col, "武力_基础", "防御_基础", "智力_基础", "速度_基础", "政治_基础", "魅力_基础"]
    display_cols = [c for c in display_cols if c in df_sorted.columns]

    # 柱状图
    top20 = df_sorted.head(20)
    fig_bar = px.bar(
        top20,
        x="武将名",
        y=dim_col,
        color="阵营",
        title=f"{dim_label}排行榜 TOP20",
        text_auto=True,
    )
    fig_bar.update_layout(
        xaxis_tickangle=-30,
        height=450,
        font=dict(size=12),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # 表格
    st.dataframe(
        df_sorted[display_cols],
        use_container_width=True,
        height=600,
        column_config={
            "武将名": st.column_config.TextColumn("武将名", width="medium"),
            "阵营": st.column_config.TextColumn("阵营", width="small"),
            "cost": st.column_config.TextColumn("cost", width="small"),
            "兵种": st.column_config.TextColumn("兵种", width="small"),
            dim_col: st.column_config.NumberColumn(dim_label, format="%.2f", width="medium"),
        }
    )

# ============ Tab 2: 武将搜索 ============
with tab2:
    st.subheader("🔎 武将详情搜索")
    search_name = st.text_input("输入武将名称（模糊匹配）", placeholder="例如：曹操、赵云")
    
    if search_name:
        results = df[df["武将名"].str.contains(search_name, na=False)].copy()
        st.write(f"找到 **{len(results)}** 个结果")
        for _, row in results.iterrows():
            with st.expander(f"📛 {row['武将名']} [{row['阵营']}] · cost {row['cost']} · {row['兵种']}"):
                # 六维属性
                radar_data = {
                    "维度": ["武力", "防御", "智力", "速度", "政治", "魅力"],
                    "基础值": [row["武力_基础"], row["防御_基础"], row["智力_基础"], 
                               row["速度_基础"], row["政治_基础"], row["魅力_基础"]],
                }
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=radar_data["基础值"],
                    theta=radar_data["维度"],
                    fill="toself",
                    name="基础属性",
                    line_color="orangered",
                    fillcolor="rgba(255,69,0,0.2)",
                ))
                fig_radar.update_layout(
                    polar=dict(raxis=dict(visible=True, range=[0, 150])),
                    showlegend=False,
                    height=300,
                    font=dict(size=13),
                )
                st.plotly_chart(fig_radar, use_container_width=True)

                col_a, col_b, col_c = st.columns(3)
                col_a.metric("武力", f"{row['武力_基础']:.1f} (+{row['武力_成长']})")
                col_b.metric("防御", f"{row['防御_基础']:.1f} (+{row['防御_成长']})")
                col_c.metric("智力", f"{row['智力_基础']:.1f} (+{row['智力_成长']})")
                col_d, col_e, col_f = st.columns(3)
                col_d.metric("速度", f"{row['速度_基础']:.1f} (+{row['速度_成长']})")
                col_e.metric("政治", f"{row['政治_基础']:.1f} (+{row['政治_成长']})")
                col_f.metric("魅力", f"{row['魅力_基础']:.1f} (+{row['魅力_成长']})")
                st.markdown(f"**总属性: {row['总属性']:.1f}**")

                st.markdown("---")
                if row["主战技"]:
                    st.markdown(f"**⚔️ 主战技: {row['主战技_品质']} {row['主战技']}** ({row['主战技_类型']} · {row['主战技_概率']})")
                    st.caption(row["主战技_描述"])
                if row["自带技能"]:
                    st.markdown(f"**🛡️ 自带技能: {row['自带技能_品质']} {row['自带技能']}** ({row['自带技能_类型']})")
                    st.caption(row["自带技能_描述"])
                if row["传承技能"]:
                    st.markdown(f"**🔄 传承技能: {row['传承技能_品质']} {row['传承技能']}** ({row['传承技能_类型']})")
                    st.caption(row["传承技能_描述"])
                if row["缘分"]:
                    st.markdown(f"**🔗 缘分: {row['缘分']}**")
    else:
        st.info("输入武将名称开始搜索，支持模糊匹配")

# ============ Tab 3: 武将对比 ============
with tab3:
    st.subheader("⚔️ 两武将属性对比")
    all_names = df["武将名"].tolist()
    col_left, col_right = st.columns(2)
    with col_left:
        hero1 = st.selectbox("武将 ①", all_names, index=0, key="hero1")
    with col_right:
        hero2 = st.selectbox("武将 ②", all_names, index=min(1, len(all_names)-1), key="hero2")

    if hero1 and hero2 and hero1 != hero2:
        r1 = df[df["武将名"] == hero1].iloc[0]
        r2 = df[df["武将名"] == hero2].iloc[0]

        # 雷达图对比
        fig_compare = go.Figure()
        dims = ["武力", "防御", "智力", "速度", "政治", "魅力"]
        vals1 = [r1["武力_基础"], r1["防御_基础"], r1["智力_基础"], r1["速度_基础"], r1["政治_基础"], r1["魅力_基础"]]
        vals2 = [r2["武力_基础"], r2["防御_基础"], r2["智力_基础"], r2["速度_基础"], r2["政治_基础"], r2["魅力_基础"]]

        fig_compare.add_trace(go.Scatterpolar(
            r=vals1, theta=dims, fill="toself", name=hero1,
            line_color="orangered", fillcolor="rgba(255,69,0,0.15)",
        ))
        fig_compare.add_trace(go.Scatterpolar(
            r=vals2, theta=dims, fill="toself", name=hero2,
            line_color="steelblue", fillcolor="rgba(70,130,180,0.15)",
        ))
        fig_compare.update_layout(
            polar=dict(raxis=dict(visible=True, range=[0, 150])),
            showlegend=True, height=450, font=dict(size=13),
        )
        st.plotly_chart(fig_compare, use_container_width=True)

        # 差值表格
        diff_df = pd.DataFrame({
            "维度": dims,
            hero1: vals1,
            hero2: vals2,
            "差值(①-②)": [round(v1-v2, 2) for v1, v2 in zip(vals1, vals2)],
        })
        st.dataframe(diff_df, use_container_width=True, hide_index=True)

        # 六维各自对比柱状
        fig_diff = go.Figure()
        colors1 = ["orangered" if v1 >= v2 else "lightcoral" for v1, v2 in zip(vals1, vals2)]
        colors2 = ["steelblue" if v2 >= v1 else "lightblue" for v1, v2 in zip(vals1, vals2)]
        fig_diff.add_trace(go.Bar(x=dims, y=vals1, name=hero1, marker_color="orangered", text=vals1, textposition="outside"))
        fig_diff.add_trace(go.Bar(x=dims, y=vals2, name=hero2, marker_color="steelblue", text=vals2, textposition="outside"))
        fig_diff.update_layout(barmode="group", height=350, font=dict(size=13))
        st.plotly_chart(fig_diff, use_container_width=True)

# ============ Tab 4: 缘分速查 ============
with tab4:
    st.subheader("📋 缘分武将速查")
    # 从bonds构建缘分映射
    bond_map = {}  # hero_name -> [(bond_name, other_hero_ids), ...]
    hero_name_map = {h["id"]: h["name"] for h in heroes}
    for h in heroes:
        for bond in h.get("bonds", []):
            names = [hero_name_map.get(i, f"ID:{i}") for i in bond.get("heroIds", [])]
            bond_map.setdefault(h["name"], []).append((bond["name"], names))

    bond_search = st.text_input("搜索缘分名或武将名", placeholder="例如：魏武之治、曹操")
    if bond_search:
        found = [(name, bonds) for name, bonds in bond_map.items()
                 if bond_search in name or any(bond_search in bn for bn, _ in bonds)]
        st.write(f"找到 **{len(found)}** 个武将")
        for name, bonds in found:
            bond_items = [bn for bn, _ in bonds if bond_search in bn] or [bn for bn, _ in bonds]
            st.markdown(f"### 📛 {name}")
            cols = st.columns(min(3, len(bond_items)))
            for i, (bn, members) in enumerate(bonds):
                with cols[i % len(cols)]:
                    st.markdown(f"**{bn}**")
                    st.caption(" · ".join(members))
            st.markdown("---")
    else:
        # 缘分数量统计
        bond_count = {name: len(bonds) for name, bonds in bond_map.items()}
        top_bond = sorted(bond_count.items(), key=lambda x: -x[1])[:20]
        st.markdown("缘分数量排行 TOP20")
        bond_df = pd.DataFrame(top_bond, columns=["武将", "缘分数"])
        st.dataframe(bond_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("📊 数据来源: 官网 · 由 AI 自动整理 · 仅供配将参考")
