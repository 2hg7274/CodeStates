from flask import Flask, redirect, render_template, request
import joblib
import sklearn
import pandas as pd

def create_app():
    app = Flask(__name__)
    model = joblib.load('model.pkl')

    @app.route('/', methods=['GET'])
    def main():
        return render_template('main.html')


    @app.route('/data')
    def data():
        return redirect("http://bpms.kemco.or.kr/transport_2012/car/car_choice.aspx?serorigin=&serecode=&serfuel=3&sergear=&sercartype=&sergrade=&sertypegb=&sertab=&otype=YD&ptype=50&f=system&sermileage1=&sermileage2=&serco21=&serco22=&seramt1=&seramt2=&sermname=&serstyear=#search_top")


    @app.route('/predict', methods=['GET', 'POST'])
    def predict():
        return render_template('predict.html')

    @app.route('/predict/ans', methods=['GET', 'POST'])
    def answer():
        if request.method == "POST":
            pred_list = []
            manuf=request.form['manuf']
            fuel=request.form['fuel']
            cc=request.form['cc']
            fuelefficiency=request.form['fuelefficiency']
            grade=request.form['grade']
            di=request.form['di']
            cartype=request.form['cartype']
            carcategory=request.form['carcategory']
            obj=request.form['obj']

            pred_list.append((manuf,fuel, cc, fuelefficiency, grade, di, cartype, carcategory, obj))
            pred_df = pd.DataFrame(pred_list, columns=['제조사', '유종', '배기량', '복합연비', '등급', '국산/수입', '자동차형식' ,'자동차종류', '자동차유형'])

            prediction=model.predict(pred_df)
            output=round(prediction[0],2)
            
            
            return render_template('result.html', prediction_text="당신이 선택한 차량의 CO2 배출량 예상은 {} g/km 입니다. " .format(output))
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')


    @app.errorhandler(500)
    def pageerror(error):
        return render_template('result.html', prediction_text="값을 제대로 입력하지 않았습니다! 이전 화면으로 돌아가 다시 입력해 주세요!")


    @app.route('/github')
    def github():
        return redirect("https://github.com/2hg7274")

    return app 