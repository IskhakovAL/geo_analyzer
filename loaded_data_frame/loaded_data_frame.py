# data
import json

# charts
import plotly
import plotly.express as px

# forms
from flask_wtf import FlaskForm
from wtforms import widgets, SelectMultipleField

# map
import folium
from folium.plugins import HeatMap


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=True)
    option_widget = widgets.CheckboxInput()


class CheckboxForm(FlaskForm):
    checkbox = MultiCheckboxField('Label')


class LoadedDataFrame(object):

    def __init__(self, df):
        self.df = df
        self.df_head = df.head(5)
        self.width = 400
        self.height = 400

    def get_table_components(self):
        """Возвращает первые пять строк датафрейма."""
        df_head = self.df_head
        columns = df_head.columns.tolist()
        values = df_head.values.tolist()

        for i in range(len(values)):
            values[i].insert(0, i)

        return columns, values

    def get_graphs_components(self):
        """Возвращает графики."""
        charts = []

        df = self.df
        # будем работать со всеми колонками, за исключением широты/долготы
        df_columns = self.df.drop(['latitude', 'longitude'], axis=1).columns

        width = self.width
        height = self.height

        for col in df_columns:
            # для каждой из колонок найдем количество уникальных значений
            col_data = df[col]
            len_col_data = len(col_data.unique())

            def round_str(s):
                """Функция для сокращения строк."""
                if len(s) <= 30:
                    return s
                return s[:30].strip() + '...'

            # если уникальных значений в колонке меньше 3, создадим круговую диаграмму
            if len_col_data <= 3:
                col_grouped = col_data.value_counts()
                col_names = [round_str(str(x)) for x in col_grouped.index]
                fig = px.pie(
                    df,
                    values=col_grouped,
                    names=col_names,
                    width=width,
                    height=height
                )
                fig.update_layout(showlegend=False,
                                  title=col)
                plot_json = json.dumps(
                    fig, cls=plotly.utils.PlotlyJSONEncoder
                )
                charts.append(plot_json)

            # если уникальных значений в колонке меньше 10, создадим столбчатую диаграмму
            elif len_col_data <= 10:
                col_grouped = (
                    df.reset_index()
                    .groupby(col)['index'].count()
                    .to_frame('count').reset_index()
                )
                fig = px.bar(
                    col_grouped,
                    x=col,
                    y='count',
                    width=width,
                    height=height
                )
                fig.update_layout(showlegend=False,
                                  title=col)
                plot_json = json.dumps(
                    fig, cls=plotly.utils.PlotlyJSONEncoder
                )
                charts.append(plot_json)

            elif col_data.dtype != 'object':
                fig = px.histogram(
                    df,
                    x=col,
                    nbins=10,
                    width=width,
                    height=height
                )
                fig.update_layout(showlegend=False,
                                  title=col)
                plot_json = json.dumps(
                    fig, cls=plotly.utils.PlotlyJSONEncoder
                )
                charts.append(plot_json)

        charts_id = ['chart_' + str(i) for i in range(len(charts))]
        return charts_id, charts

    def get_forms_components(self):
        """Возвращает формы с чекбоксами."""
        forms = []

        df = self.df
        # будем работать со всеми колонками, за исключением широты/долготы
        df_columns = self.df.drop(['latitude', 'longitude'], axis=1).columns

        for col in df_columns:
            # для каждой из колонок найдем уникальные значения и их количество
            col_data = df[col]
            col_data_unique = col_data.unique()
            len_col_data = len(col_data_unique)

            # если уникальных значений в колонке меньше 10, создадим форму
            if len_col_data <= 10:
                form = CheckboxForm(col)
                form.checkbox.name = col
                form.checkbox.choices = [(str(data), data) for data in col_data_unique]
                form.checkbox.data = [str(data) for data in col_data_unique]
                forms.append(form)

        return forms

    def get_heat_map(self):
        """Returns heat map."""
        y_center, x_center = 55.7522, 37.6156

        folium_map = folium.Map(location=[y_center, x_center],
                                tiles="openstreetmap",
                                zoom_start=8,
                                max_zoom=12)

        heat_data = [[row['latitude'], row['longitude']] for index, row in self.df.iterrows()]
        HeatMap(heat_data, min_opacity=0.3).add_to(folium_map)

        return folium_map
