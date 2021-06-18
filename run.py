from flask import Flask, request
from flask import render_template

import pandas as pd

import folium
from folium.plugins import HeatMap

from loaded_data_frame import LoadedDataFrame


SECRET_KEY = 'development'
app = Flask(__name__)
app.config.from_object(__name__)
app.static_folder = 'static'
app.template_folder = 'templates'
app.jinja_env.filters['zip'] = zip


def plot_heat_map(df):
    y_center, x_center = 55.7522, 37.6156

    folium_map = folium.Map(location=[y_center, x_center],
                            tiles = "openstreetmap",
                            zoom_start = 8,
                            max_zoom=12)

    heat_data = [[row['latitude'], row['longitude']] for index, row in df.iterrows()]
    HeatMap(heat_data, min_opacity=0.3).add_to(folium_map)

    return folium_map


@app.route('/', methods=['GET', 'POST'])
def hello():
    # TODO: придумать нормальное имя вместо full_df.
    df = pd.DataFrame({
        'Имя': ["Катя", "Вася", "Даша", "Петя"],
        'Пол': ["Женский", "Мужской", "Женский", "Мужской"],
        'Возраст': [15, 24, 15, 35],
        'latitude': [55.4522, 55.1522, 55.9522, 55.3522],
        'longitude': [37.7156, 37.1156, 37.3156, 37.5156]
    })
    loaded_df = LoadedDataFrame(df)

    folium_map = plot_heat_map(df)

    forms = loaded_df.get_forms_components()

    if request.method == 'GET':
        return render_template(
            'index.html',
            m=folium_map._repr_html_(),
            headings=loaded_df.get_table_components()[0],
            df=loaded_df.get_table_components()[1],
            plot_id=loaded_df.get_graphs_components()[0],
            plot_json=loaded_df.get_graphs_components()[1],
            forms=forms
        )
    # TODO: кодревью.
    elif request.method == 'POST':
        selected_data = request.form.getlist('checkbox')
        for form in forms:
            correct_data = [ec[0] for ec in form.checkbox.choices]
            form.checkbox.data = list(set(selected_data) & set(correct_data))

        # TODO: переименовать переменную.
        is_okay = True
        for form in forms:
            # print(form.checkbox.data)
            # print(form.checkbox.choices)
            if not form.validate_on_submit():
                print(form.errors)
                print()
                is_okay = False
            else:
                print('ok')

        if is_okay:
            print('is okay!')
            filters = []
            # TODO: если есть числовой столбец, код умирает. Придумать логику для числовых данных.
            #  И в целом подумать над возможными типами (чтобы не возникало таких ошибок, это важно).
            for i in range(len(forms)):
                print(df[df.columns[i]])
                print(forms[i].checkbox.data)
                filters.append(df[df.columns[i]].isin(forms[i].checkbox.data))
                print(filters[i])
            # TODO: убрать костыль.
            total_filter = filters[0]
            for i in range(1, len(filters)):
                total_filter = total_filter & filters[i]
            loaded_df = LoadedDataFrame(df[total_filter])
            print(df[total_filter])

            folium_map = plot_heat_map(df[total_filter])

            return render_template(
                'index.html',
                m=folium_map._repr_html_(),
                headings=loaded_df.get_table_components()[0],
                df=loaded_df.get_table_components()[1],
                plot_id=loaded_df.get_graphs_components()[0],
                plot_json=loaded_df.get_graphs_components()[1],
                forms=forms
            )
        else:
            # TODO: изменить вывод на какой-то другой.
            return render_template(
                'index.html',
                headings=loaded_df.get_table_components()[0],
                df=loaded_df.get_table_components()[1],
                plot_id=loaded_df.get_graphs_components()[0],
                plot_json=loaded_df.get_graphs_components()[1],
                forms=forms
            )


if __name__ == '__main__':
    app.run(debug=True)
