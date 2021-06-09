from flask import Flask, request
from flask import render_template

from flask_wtf import FlaskForm
from wtforms import widgets, SelectMultipleField

import pandas as pd

import plotly
import plotly.express as px

import json

import folium

SECRET_KEY = 'development'
app = Flask(__name__)
app.config.from_object(__name__)
app.static_folder = 'static'
app.template_folder = 'templates'
app.jinja_env.filters['zip'] = zip


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=True)
    option_widget = widgets.CheckboxInput()


class SimpleForm(FlaskForm):
	example = MultiCheckboxField('Label')
 



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
        columns = self.df_head.columns.tolist()
        values = self.df_head.values.tolist()
        
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
                plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                charts.append(plot_json)
            elif len_col_data <= 10:
                col_grouped = (
                    df.reset_index()
                    .groupby(col)['index'].count()
                    .to_frame('count').reset_index()
                )
                fig = px.bar(col_grouped, x=col, y='count', width=width, height=height)
                plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                charts.append(plot_json)
            elif col_data.dtype != 'object':
                fig = px.histogram(df, x=col, nbins=10)
                plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                charts.append(plot_json)

        
        div_id = ['chart_'+ str(i) for i in range(len(charts))]
        return div_id, charts



@app.route('/', methods=['GET', 'POST'])
def hello():
	# df = pd.read_csv('datasets/Mall_Customers.csv')
	df = pd.DataFrame({
	    'Имя': ["Катя", "Вася", "Даша", "Петя"], 
	    'Пол': ["Женский", "Мужской", "Женский", "Мужской"],
	    'Возраст': [15, 24, 15, 35]
	})
	loaded_df = LoadedDataFrame(df)

	


	folium_map = folium.Map(location=[45.5236, -122.6750])

	form = SimpleForm()
	form.example.choices = [('Женский', 'Женский'), ('Мужской', 'Мужской')]

	if request.method == 'GET':
		form.example.data = ['Женский', 'Мужской']
		return render_template(
				'index.html', 
				m = folium_map._repr_html_(),
				headings = loaded_df.get_table_components()[0], 
				df = loaded_df.get_table_components()[1], 
				plot_id = loaded_df.get_graphs_components()[0],
				plot_json = loaded_df.get_graphs_components()[1],
				form = form
			)
	elif request.method == 'POST':
		if form.validate_on_submit():
			print(form.example.data)
			df = df[df['Пол'].isin(form.example.data)]
			loaded_df = LoadedDataFrame(df)

			return render_template(
				'index.html', 
				headings = loaded_df.get_table_components()[0], 
				df = loaded_df.get_table_components()[1], 
				plot_id = loaded_df.get_graphs_components()[0],
				plot_json = loaded_df.get_graphs_components()[1],
				form = form
			)
		else:
			print('Errors')
			print(form.errors)


if __name__ == '__main__':
    app.run(debug=True)
