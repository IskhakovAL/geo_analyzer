from flask import Flask, request
from flask import render_template

from flask_wtf import FlaskForm
from wtforms import widgets, SelectMultipleField

import pandas as pd

import folium

from loaded_data_frame import LoadedDataFrame

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


@app.route('/', methods=['GET', 'POST'])
def hello():
	df = pd.read_csv('datasets/Mall_Customers.csv')
	# df = pd.DataFrame({
	#     'Имя': ["Катя", "Вася", "Даша", "Петя"], 
	#     'Пол': ["Женский", "Мужской", "Женский", "Мужской"],
	#     'Возраст': [15, 24, 15, 35]
	# })
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
