from flask import Flask, request
from flask import render_template
import pandas as pd
from loaded_data_frame import LoadedDataFrame
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
SECRET_KEY = 'development'
app = Flask(__name__)
app.config.from_object(__name__)
app.static_folder = 'static'
app.template_folder = 'templates'
app.jinja_env.filters['zip'] = zip
csrf.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def hello():
    example_df = pd.DataFrame({
        'Имя': ["Катя", "Вася", "Даша", "Петя"],
        'Пол': ["Женский", "Мужской", "Женский", "Мужской"],
        'Возраст': [15, 24, 15, 35],
        'latitude': [55.4522, 55.1522, 55.9522, 55.3522],
        'longitude': [37.7156, 37.1156, 37.3156, 37.5156]
    })

    # TODO: организовать считывание файлика пользователя/парсить какой-нибудь сайт
    # TODO: пока что считываем все данные как строки, в идеале нужно обрабатывать числа как числа
    df = pd.read_csv('datasets/akhmatova.csv').astype(str)
    # df = example_df.astype(str)

    loaded_df = LoadedDataFrame(df)
    forms = loaded_df.get_forms_components()

    if request.method == 'GET':
        return render_template(
            'index.html',
            heat_map=loaded_df.get_heat_map()._repr_html_(),
            headings=loaded_df.get_table_components()[0],
            df=loaded_df.get_table_components()[1],
            plot_id=loaded_df.get_graphs_components()[0],
            plot_json=loaded_df.get_graphs_components()[1],
            forms=forms
        )

    elif request.method == 'POST':
        # обновим данные в каждой форме
        for form in forms:
            form.checkbox.data = request.form.getlist(form.checkbox.name)
            print(form.checkbox.name)

        for form in forms:
            # если возникает ошибка с обработкой форм
            if not form.validate_on_submit():
                print(form.errors)
                # перезапишем loaded_df и выведем на экран сообщение об ошибке
                # TODO: добавить оповещение про ошибку
                loaded_df = LoadedDataFrame(df)

                return render_template(
                    'index.html',
                    heat_map=loaded_df.get_heat_map()._repr_html_(),
                    headings=loaded_df.get_table_components()[0],
                    df=loaded_df.get_table_components()[1],
                    plot_id=loaded_df.get_graphs_components()[0],
                    plot_json=loaded_df.get_graphs_components()[1],
                    forms=forms
                )

        # для каждого столбца в датафрейме создадим фильтр по отмеченным чекбоксам
        filters = []
        for i in range(len(forms)):
            print(df[df.columns[i]])
            filters.append(df[forms[i].checkbox.name].isin(forms[i].checkbox.data))
            print(filters[i])
        # объединим фильтры
        # TODO: убрать костыль
        total_filter = filters[0]
        for i in range(1, len(filters)):
            total_filter = total_filter & filters[i]
        # перезапишем loaded_df с учетом фильтров
        loaded_df = LoadedDataFrame(df[total_filter])
        return render_template(
            'index.html',
            heat_map=loaded_df.get_heat_map()._repr_html_(),
            headings=loaded_df.get_table_components()[0],
            df=loaded_df.get_table_components()[1],
            plot_id=loaded_df.get_graphs_components()[0],
            plot_json=loaded_df.get_graphs_components()[1],
            forms=forms
        )


if __name__ == '__main__':
    app.run(debug=True)
