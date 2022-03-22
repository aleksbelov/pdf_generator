from math import log10

import pandas as pd
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


def get_month_name(x, short_month_name):
    if short_month_name:
        return months[x][:3]
    return months[x]


def get_value_order(x: int):
    return {1: 'тыс.',
            2: 'млн.',
            3: 'млрд.'}.get(int(log10(x) / 3), '')


def create_volume_by_month_bar_fig(df: pd.DataFrame,
                                   short_month_name=True,
                                   custom_value_label=None,
                                   draw_percentage_line=True,
                                   legend_inside=False) -> Figure:
    value_label = f"Объем, {get_value_order(df['value'].max())} рублей"
    if custom_value_label is not None:
        value_label = custom_value_label

    x_label = "Месяц"

    RF = "Российская Федерация"

    df["year"] = df["year"].astype(str)
    df["month_order"] = df["year"] + df["month"].apply(lambda x: f'{x:02}')
    df["x_label"] = df['month'].apply(lambda x: get_month_name(x, short_month_name)) + ' ' + df["year"]
    df["month"] = df["month"].astype(str)
    df = df.sort_values(by=["month_order"])
    df["ru_frac"] = df.groupby('month_order')["value"].apply(lambda x: x / x.sum() if x.all() else x)
    df["ru_frac"] = df["ru_frac"].where(df["country"] == RF, other=0)

    def px_fig():
        bar_and_line = make_subplots(specs=[[{"secondary_y": True}]])

        bar = px.bar(df,
                     x="x_label",
                     y="value",
                     color='country',
                     labels={
                         "x_label": x_label,
                         "value": value_label,
                         "country": "Страна"
                     },
                     category_orders={
                         "x_label": df["x_label"]
                     },
                     text_auto='.2s',
                     height=650,
                     width=1100)
        bar.update_xaxes(tickangle=45)
        bar.update_yaxes(ticklabelposition="inside")

        bar.update_traces(textposition="outside")

        bar.update_layout(title_x=0.5,
                          title_y=0.9,
                          font_color="black",
                          font_size=13)

        scatter = px.line(df,
                          x="x_label",
                          y="ru_frac",
                          markers=True)
        scatter.update_traces(line_color='#00ff00')
        bar_and_line.add_traces(data=bar.data + scatter.data)
        bar_and_line.layout = bar.layout

        return bar_and_line

    def go_fig():
        bar_and_line = go.Figure()
        for country in df["country"].unique():
            cur_values = df.where(df["country"] == country, other=0)["value"]
            bar_and_line.add_trace(go.Bar(x=df["x_label"],
                                          y=cur_values,
                                          name=country))
        # bar_and_line.update_traces(textposition="outside")
        bar_and_line.update_xaxes(tickangle=45)
        bar_and_line.update_layout(barmode="stack",
                                   xaxis_title=x_label,
                                   yaxis_title=value_label,
                                   height=650,
                                   width=1100,
                                   legend=dict(bgcolor='rgba(0, 0, 0, 0)'))
        if not draw_percentage_line:
            return bar_and_line

        dup_mask = df.duplicated(keep=False, subset=["x_label"])

        ru_frac = pd.concat([
            df[~dup_mask],
            df[dup_mask][df[dup_mask]["country"] == RF]
        ]).sort_values("month_order")

        line_name = "Процент товаров российского производства"
        bar_and_line.add_trace(
            go.Scatter(
                x=ru_frac["x_label"],
                y=ru_frac["ru_frac"],
                name=line_name,
                mode="lines+markers",
                yaxis="y2"
            )
        )

        bar_and_line.update_layout(
            yaxis2=dict(
                title=line_name,
                overlaying="y",
                side="right",
                tickformat='.0%'
            )
        )
        return bar_and_line

    fig = go_fig()

    if legend_inside is not None:
        fig.update_layout(
            legend=dict(
                x=0,
                y=1.0,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)'
            )
        )

    return fig
