from math import log10

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly import express as px
from plotly.graph_objs import Figure

months = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}

RF = "Российская Федерация"


def get_month_name(x, short_month_name):
    if short_month_name:
        return months[x][:3]
    return months[x]


def get_value_order(x: int):
    return {1: 'тыс.',
            2: 'млн.',
            3: 'млрд.'}.get(int(log10(x) / 3), '')


def add_persentage_scatter(fig: Figure, df: pd.DataFrame):
    dup_mask = df.duplicated(keep=False, subset=["x_label"])

    ru_frac = pd.concat([
        df[~dup_mask],
        df[dup_mask][df[dup_mask]["country"] == RF]
    ]).sort_values("month_order")

    line_name = "Процент товаров российского производства"
    fig.add_trace(
        go.Scatter(
            x=ru_frac["x_label"],
            y=ru_frac["ru_frac"],
            name=line_name,
            mode="lines+markers",
            yaxis="y2"
        )
    )

    fig.update_layout(
        yaxis2=dict(
            title=line_name,
            overlaying="y",
            side="right",
            tickformat='.0%'
        )
    )

    return fig


def get_order_with_rf_first(df: pd.DataFrame):
    tr_order = df["country"].unique()
    if RF in tr_order:
        RF_pos = np.where(tr_order == RF)[0][0]
        tr_order[0], tr_order[RF_pos] = tr_order[RF_pos], tr_order[0]
    return tr_order


def create_volume_by_month_bar_fig(df: pd.DataFrame,
                                   short_month_name=True,
                                   custom_value_label=None,
                                   draw_percentage_line=True,
                                   legend_inside=True) -> Figure:
    value_label = f"Объем, {get_value_order(df['value'].max())} рублей"
    if custom_value_label is not None:
        value_label = custom_value_label

    x_label = "Месяц"

    df["year"] = df["year"].astype(str)
    df["month_order"] = df["year"] + df["month"].apply(lambda x: f'{x:02}')
    df["x_label"] = df['month'].apply(lambda x: get_month_name(x, short_month_name)) + ' ' + df["year"]
    df["month"] = df["month"].astype(str)
    df = df.sort_values(by=["month_order"])
    df["ru_frac"] = df.groupby('month_order')["value"].apply(lambda x: x / x.sum() if x.all() else x)
    df["ru_frac"] = df["ru_frac"].where(df["country"] == RF, other=0)

    def px_fig():
        bar_and_line = px.bar(df,
                              x="x_label",
                              y="value",
                              color='country',
                              labels={
                                  "x_label": x_label,
                                  "value": value_label,
                                  "country": "Страна"
                              },
                              category_orders={
                                  "x_label": df["x_label"],
                                  "country": get_order_with_rf_first(df)
                              },
                              # color_discrete_map={RF: 'red'},
                              text_auto='.2s',
                              height=650,
                              width=1100)
        bar_and_line.update_xaxes(tickangle=45)

        bar_and_line.update_traces(textposition="outside")

        bar_and_line.update_layout(title_x=0.5,
                                   title_y=0.9,
                                   legend_title='',
                                   )
        if not draw_percentage_line:
            return bar_and_line

        bar_and_line = add_persentage_scatter(bar_and_line, df)
        return bar_and_line

    def go_fig():
        bar_and_line = go.Figure()

        for country in reversed(get_order_with_rf_first(df)):
            cur_values = df.where(df["country"] == country, other=0)["value"]
            bar_and_line.add_trace(go.Bar(x=df["x_label"],
                                          y=cur_values,
                                          name=country))

        bar_and_line.update_xaxes(tickangle=45)
        bar_and_line.update_layout(barmode="stack",
                                   xaxis_title=x_label,
                                   yaxis_title=value_label,
                                   height=650,
                                   width=1100,
                                   legend=dict(bgcolor='rgba(0, 0, 0, 0)'))
        if not draw_percentage_line:
            return bar_and_line

        bar_and_line = add_persentage_scatter(bar_and_line, df)
        return bar_and_line

    fig = go_fig()

    if legend_inside:
        fig.update_layout(
            legend=dict(
                x=0,
                y=1.0,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)'
            )
        )

    return fig
