# data
import json

# charts
import plotly
import plotly.express as px

# forms
from flask_wtf import FlaskForm
from wtforms import widgets, SelectMultipleField


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=True)
    option_widget = widgets.CheckboxInput()


class CheckboxForm(FlaskForm):
    checkbox = MultiCheckboxField('Label')


class LoadedDataFrame(object):
    """docstring"""

    def __init__(self, df):
        """constructor"""
        self.df = df
        self.df_head = df.head(10)
        self.width = 400
        self.height = 400

    def get_table_components(self):
        """docstring"""
        df_head = self.df_head
        columns = df_head.columns.tolist()
        values = df_head.values.tolist()

        for i in range(len(values)):
            values[i].insert(0, i)

        return columns, values

    def get_graphs_components(self):
        """docstring"""
        charts = []

        df = self.df
        df_columns = self.df.columns

        width = self.width
        height = self.height

        for col in df_columns:
            col_data = df[col]
            len_col_data = len(col_data.unique())

            if len_col_data <= 3:
                col_grouped = col_data.value_counts()
                fig = px.pie(
                    df,
                    values=col_grouped,
                    names=col_grouped.index,
                    width=width,
                    height=height
                )
                plot_json = json.dumps(
                    fig, cls=plotly.utils.PlotlyJSONEncoder
                )
                charts.append(plot_json)

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
                plot_json = json.dumps(
                    fig, cls=plotly.utils.PlotlyJSONEncoder
                )
                charts.append(plot_json)

        charts_id = ['chart_' + str(i) for i in range(len(charts))]
        return charts_id, charts

    def get_forms_components(self):
        """docstring"""
        forms = []

        df = self.df
        df_columns = self.df.columns

        for col in df_columns:
            col_data = df[col]
            col_data_unique = col_data.unique()
            len_col_data = len(col_data_unique)

            if len_col_data <= 10:
                form = CheckboxForm()
                form.checkbox.choices = [(str(data), data) for data in col_data_unique]
                form.checkbox.data = [str(data) for data in col_data_unique]
                forms.append(form)

        return forms
