def render_monthly_insights():
    """第一页：月度 AI 进展（优化版）"""
    st.markdown("""
    <div class="page-header">
        <h1>📆 月度 AI 进展 · 动态看板</h1>
        <p>追踪全球 AI 基建、应用与金融领域的每月动态</p>
    </div>
    """, unsafe_allow_html=True)

    all_data = load_monthly_data()

    if all_data.empty:
        st.info("📭 等待数据接入 — 请确保数据源已配置并包含所需字段。")
        return

    # 初始化 session state 用于记录选中的分类
    if 'active_category' not in st.session_state:
        st.session_state.active_category = "全部"

    # 水平筛选栏
    month_options = sorted(all_data['选择月份'].unique().tolist(), reverse=True)
    region_col = next((c for c in all_data.columns if c in ['地域', '地区']), None)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="filter-label">📅 月份</div>', unsafe_allow_html=True)
        selected_month = st.selectbox("月份", month_options, label_visibility="collapsed")
    with col2:
        if region_col:
            region_values = sorted(all_data[region_col].unique().tolist())
            region_options = ["全部地区"] + region_values
            st.markdown('<div class="filter-label">🌐 地域</div>', unsafe_allow_html=True)
            selected_region = st.selectbox("地域", region_options, label_visibility="collapsed")
        else:
            selected_region = "全部地区"
            st.markdown('<div class="filter-label">🌐 地域</div>', unsafe_allow_html=True)
            st.selectbox("地域", ["全部地区"], disabled=True, label_visibility="collapsed")

    # 应用筛选
    df = all_data[all_data['选择月份'] == selected_month].copy()
    if region_col and selected_region != "全部地区":
        df = df[df[region_col] == selected_region]

    # 计算分类计数
    cat_col = '分类' if '分类' in df.columns else None
    if cat_col:
        infra_n = len(df[df[cat_col] == '基建'])
        app_n = len(df[df[cat_col] == '应用'])
        fin_n = len(df[df[cat_col] == '金融'])
    else:
        infra_n = app_n = fin_n = 0
    total_n = len(df)

    # ---------- 可点击的统计卡片（按钮式）----------
    st.markdown("### 点击卡片筛选分类")
    c1, c2, c3, c4 = st.columns(4)

    # 自定义按钮样式（与卡片融合）
    button_style = """
    <style>
    .cat-btn {
        width: 100%;
        background: var(--bg-secondary);
        border: 1px solid var(--border-light);
        border-radius: 20px;
        padding: 1.5rem 0.5rem;
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
        cursor: pointer;
        text-align: center;
    }
    .cat-btn:hover {
        box-shadow: var(--shadow-md);
        transform: scale(1.01);
        border-color: var(--accent-blue);
    }
    .cat-btn.active {
        border: 2px solid var(--accent-blue);
        background: linear-gradient(145deg, #ffffff, #f8faff);
    }
    .cat-btn .stat-val {
        font-size: 2.5rem;
        font-weight: 650;
        color: var(--text-primary);
    }
    .cat-btn .stat-label {
        color: var(--text-secondary);
        font-weight: 500;
        font-size: 0.9rem;
        text-transform: uppercase;
    }
    </style>
    """

    # 用 st.button 实现点击切换
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button(f"📊 全部\n\n{total_n}", key="btn_all", use_container_width=True):
            st.session_state.active_category = "全部"
    with col2:
        if st.button(f"🏗️ 基建\n\n{infra_n}", key="btn_infra", use_container_width=True):
            st.session_state.active_category = "基建"
    with col3:
        if st.button(f"🎨 应用\n\n{app_n}", key="btn_app", use_container_width=True):
            st.session_state.active_category = "应用"
    with col4:
        if st.button(f"💰 金融\n\n{fin_n}", key="btn_fin", use_container_width=True):
            st.session_state.active_category = "金融"

    # 显示当前激活分类
    active_cat = st.session_state.active_category
    st.caption(f"当前筛选：**{active_cat}** 类动态")

    # 根据激活分类过滤数据
    if cat_col and active_cat != "全部":
        display_df = df[df[cat_col] == active_cat]
    else:
        display_df = df

    # 渲染信息流卡片（直接显示，无标签页）
    render_feed_cards(display_df)
