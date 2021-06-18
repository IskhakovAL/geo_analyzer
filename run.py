from flask import Flask, request
from flask import render_template

import pandas as pd

import folium

from loaded_data_frame import LoadedDataFrame

SECRET_KEY = 'development'
app = Flask(__name__)
app.config.from_object(__name__)
app.static_folder = 'static'
app.template_folder = 'templates'
app.jinja_env.filters['zip'] = zip


@app.route('/', methods=['GET', 'POST'])
def hello():
    # TODO: придумать нормальное имя вместо full_df.
    # full_df = pd.read_csv('datasets/Mall_Customers.csv')
    full_df = pd.DataFrame({
        'Имя': ["Катя", "Вася", "Даша", "Петя"],
        'Пол': ["Женский", "Мужской", "Женский", "Мужской"],
        'Возраст': [15, 24, 15, 35]
    })
    # full_df = pd.DataFrame({
    #     'Имя': ["kate", "ivan", "daria", "petr"],
    #     'Пол': ["female", "male", "female", "male"],
    #     # 'Возраст': [15, 24, 15, 35]
    # })
    df = full_df
    loaded_df = LoadedDataFrame(df)

    folium_map = folium.Map(location=[45.5236, -122.6750])

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
        # TODO: убрать костыль (я про forms[0]).
        selected_data = forms[0].example.data
        for form in forms:
            correct_data = [ec[0] for ec in form.example.choices]
            form.example.data = list(set(selected_data) & set(correct_data))

        # TODO: переименовать переменную.
        is_okay = True
        for form in forms:
            print(form.example.data)
            print(form.example.choices)
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
                print(full_df[full_df.columns[i]])
                print(forms[i].example.data)
                filters.append(full_df[full_df.columns[i]].isin(forms[i].example.data))
                print(filters[i])
            # TODO: убрать костыль.
            total_filter = filters[0]
            for i in range(1, len(filters)):
                total_filter = total_filter & filters[i]
            df = full_df[total_filter]
            loaded_df = LoadedDataFrame(df)
            print(df)

            return render_template(
                'index.html',
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
