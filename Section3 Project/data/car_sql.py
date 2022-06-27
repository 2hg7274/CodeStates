import sqlite3
import pandas as pd

conn = sqlite3.connect('/Users/hanhyeongu/Section3/Project/data/car.db')
cur = conn.cursor()


cur.execute("""
    DROP TABLE IF EXISTS wheel;
""")
cur.execute("""
    DROP TABLE IF EXISTS fuel_supply;
""")
cur.execute("""
    DROP TABLE IF EXISTS wheel_fuel_supply;
""")
cur.execute("""
    DROP TABLE IF EXISTS DI;
""")
cur.execute("""
    DROP TABLE IF EXISTS manufacturer;
""")
cur.execute("""
    DROP TABLE IF EXISTS fuel;
""")
cur.execute("""
    DROP TABLE IF EXISTS grade;
""")
cur.execute("""
    DROP TABLE IF EXISTS car_purpose;
""")
cur.execute("""
    DROP TABLE IF EXISTS car_type;
""")
cur.execute("""
    DROP TABLE IF EXISTS purpose_type;
""")
cur.execute("""
    DROP TABLE IF EXISTS car_form;
""")
cur.execute("""
    DROP TABLE IF EXISTS type_form;
""")
cur.execute("""
    DROP TABLE IF EXISTS car_model;
""")
conn.commit()


# 1. 굴림
cur.execute("""
    CREATE TABLE wheel(
        wheel_id INTEGER NOT NULL PRIMARY KEY,
        wheel_name VARCHAR 
    );
""")

# 2. 연료공급방식
cur.execute("""
    CREATE TABLE fuel_supply(
        fuel_supply_id INTEGER NOT NULL PRIMARY KEY,
        fuel_supply_name VARCHAR 
    );
""")

# 3. 연료_굴림
cur.execute("""
    CREATE TABLE wheel_fuel_supply(
        wheel_fuel_id INTEGER NOT NULL PRIMARY KEY,
        wheel_id INTEGER,
        fuel_supply_id INTEGER,
        FOREIGN KEY (wheel_id) REFERENCES wheel(wheel_id),
        FOREIGN KEY (fuel_supply_id) REFERENCES fuel_supply(fuel_supply_id)
    );
""")


# 4. 국산/수입 (Domestic/Import)
cur.execute("""
    CREATE TABLE DI(
        DI_id INTEGER NOT NULL PRIMARY KEY,
        DI_name VARCHAR
    );
""")

# 5. 제조사
cur.execute("""
    CREATE TABLE manufacturer(
        manuf_id INTEGER NOT NULL PRIMARY KEY,
        manuf_name VARCHAR,
        DI_id INTEGER,
        FOREIGN KEY (DI_id) REFERENCES DI(DI_id)
    );
""")


# 6. 유종 (경유, 휘발유, LPG 등등)
cur.execute("""
    CREATE TABLE fuel(
        fuel_id INTEGER NOT NULL PRIMARY KEY,
        fuel_name VARCHAR
    );
""")

# 7. 등급
cur.execute("""
    CREATE TABLE grade(
        grade_id INTEGER NOT NULL PRIMARY KEY,
        grade_score VARCHAR
    );
""")

# 8. 자동차 유형 (일반형, 다목적형, 기타형)
cur.execute("""
    CREATE TABLE car_purpose(
        car_purpose_id INTEGER NOT NULL PRIMARY KEY,
        car_purpose_name VARCHAR
    );
""")

# 9. 자동차 종류 (승용차, 화물차)
cur.execute("""
    CREATE TABLE car_type(
        car_type_id INTEGER NOT NULL PRIMARY KEY,
        car_type_name VARCHAR
    );
""")

# 10. 자동차 유형_종류
cur.execute("""
    CREATE TABLE purpose_type(
        purpose_type_id INTEGER NOT NULL PRIMARY KEY,
        car_purpose_id INTEGER,
        car_type_id INTEGER,
        FOREIGN KEY (car_purpose_id) REFERENCES car_purpose(car_purpose_id),
        FOREIGN KEY (car_type_id) REFERENCES car_type(car_type_id)
    );
""")


# 11. 자동차 형식 (내연기관, 하이브리드, ...)
cur.execute("""
    CREATE TABLE car_form(
        car_form_id INTEGER NOT NULL PRIMARY KEY,
        car_form_name VARCHAR
    );
""")

#12.  종류_형식 
cur.execute("""
    CREATE TABLE type_form(
        type_form_id INTEGER NOT NULL PRIMARY KEY,
        car_type_id INTEGER,
        car_form_id INTEGER,
        FOREIGN KEY (car_type_id) REFERENCES car_type(car_type_id),
        FOREIGN KEY (car_form_id) REFERENCES car_form(car_form_id)
    );
""")


# 13. 자동차 model 테이블 
cur.execute("""
    CREATE TABLE car_model(
        model_id INTEGER NOT NULL PRIMARY KEY,
        model_name VARCHAR,
        manuf_id INTEGR, 
        fuel_id INTEGER, 
        displacement INTEGER,
        weight INTEGER,
        fuel_efficiency NUMERIC(5,1),
        grade_id INTEGER, 
        car_form_id INTEGER, 
        fuel_supply_id INTEGER, 
        CO2 NUMERIC(4,1), 
        FOREIGN KEY (manuf_id) REFERENCES manufacturer(manuf_id),
        FOREIGN KEY (fuel_id) REFERENCES fuel(fuel_id),
        FOREIGN KEY (grade_id) REFERENCES grade(grade_id),
        FOREIGN KEY (car_form_id) REFERENCES car_form(car_form_id),
        FOREIGN KEY (fuel_supply_id) REFERENCES fuel_supply(fuel_supply_id)
    );
""")
conn.commit()



# csv 파일 불러온 후 전처리 진행 (제조사 푸조와 시트로앵 삽입, 결측치 행 삭제, 모델명 중복값 삭제)
car_df = pd.read_csv("/Users/hanhyeongu/Section3/Project/data/car_list.csv", encoding='cp949', header=1)
na_index = car_df[car_df['제조사'].isna()].index
for i in na_index:
    if "Peugeot" in car_df.iloc[i]['모델명']  :
        car_df.loc[i, '제조사'] = '푸조'
    elif "Citroen" in car_df.iloc[i]['모델명']:
        car_df.loc[i, '제조사'] = '시트로앵'
    else:
        pass

car_df = car_df.dropna(axis=0)
car_df = car_df.drop_duplicates(['모델명'], keep='first')

def hasNumber(stringVal):
    return any(elem.isdigit() for elem in stringVal)

for i in car_df[car_df['CO2배출량'].apply(hasNumber)==False].index:
    car_df = car_df.drop([i], axis=0)
car_df = car_df.reset_index(drop=True)

def cc(data):
    data = data.str.replace(',','')
    data = data.str.replace('cc','')
    data = data.astype(int)
    return data

def kg(data):
    data = data.str.replace(',','')
    data = data.str.replace('kg','')
    data = data.astype(int)
    return data

def co2(data):
    data = data.str.replace('g/km', '')
    data = data.astype(float)
    return data

def km_l(data):
    if '㎞/ℓ' in data:
        data = data.replace('㎞/ℓ', '')
        data = float(data)
    elif 'km/kWh' in data:
        data = data.replace('km/kWh', '')
        data = float(data)
    return data

car_df['배기량'] = cc(car_df['배기량'])

car_df['공차중량'] = kg(car_df['공차중량'])

car_df['CO2배출량'] = co2(car_df['CO2배출량'])

car_df['복합연비'] = car_df['복합연비'].apply(km_l)




# 데이터 테이블에 넣기
## 1. 테이블
for i in car_df['굴림방식'].unique():
    cur.execute(f"INSERT INTO wheel (wheel_name) VALUES ('{i}');")



## 2. 테이블
for i in car_df['연료공급방식'].unique():
    cur.execute(f"INSERT INTO fuel_supply (fuel_supply_name) VALUES ('{i}');")


## 3. 테이블
for i in car_df.groupby(['굴림방식','연료공급방식']).size().index:
    cur.execute(f"""
        SELECT wheel_id FROM wheel WHERE wheel_name='{i[0]}';
    """)
    a = cur.fetchone()
    
    cur.execute(f"""
        SELECT fuel_supply_id FROM fuel_supply WHERE fuel_supply_name="{i[1]}";
    """)
    b = cur.fetchone()

    cur.execute(f"INSERT INTO wheel_fuel_supply (wheel_id, fuel_supply_id) VALUES ('{a[0]}','{b[0]}');")


## 4. 테이블
for i in car_df['국산/수입'].unique():
    cur.execute(f"INSERT INTO DI (DI_name) VALUES ('{i}');")


## 5. 테이블
for i in car_df.groupby(['제조사','국산/수입']).size().index:
    cur.execute(f"SELECT DI_id FROM DI WHERE DI_name='{i[1]}';")
    c = cur.fetchone()

    cur.execute(f"INSERT INTO manufacturer (manuf_name, DI_id) VALUES ('{i[0]}','{c[0]}');")


## 6. 테이블
for i in car_df['유종'].unique():
    cur.execute(f"INSERT INTO fuel (fuel_name) VALUES ('{i}');")


## 7. 테이블
for i in car_df['등급'].unique():
    cur.execute(f"INSERT INTO grade (grade_score) VALUES ('{i}');")


## 8. 테이블
for i in car_df['자동차유형'].unique():
    cur.execute(f"INSERT INTO car_purpose (car_purpose_name) VALUES ('{i}');")


## 9. 테이블
for i in car_df['자동차종류'].unique():
    cur.execute(f"INSERT INTO car_type (car_type_name) VALUES ('{i}');")


## 10. 테이블
for i in car_df.groupby(['자동차유형','자동차종류']).size().index:
    cur.execute(f"SELECT car_purpose_id FROM car_purpose WHERE car_purpose_name='{i[0]}';")
    d = cur.fetchone()

    cur.execute(f"SELECT car_type_id FROM car_type WHERE car_type_name='{i[1]}';")
    e = cur.fetchone()

    cur.execute(f"INSERT INTO purpose_type (car_purpose_id, car_type_id) VALUES ('{d[0]}','{e[0]}');")


## 11. 테이블 
for i in car_df['자동차형식'].unique():
    cur.execute(f"INSERT INTO car_form (car_form_name) VALUES ('{i}');")


## 12. 테이블
for i in car_df.groupby(['자동차종류','자동차형식']).size().index:
    cur.execute(f"SELECT car_type_id FROM car_type WHERE car_type_name='{i[0]}';")
    f = cur.fetchone()

    cur.execute(f"SELECT car_form_id FROM car_form WHERE car_form_name='{i[1]}';")
    g = cur.fetchone()

    cur.execute(f"INSERT INTO type_form (car_type_id, car_form_id) VALUES ('{f[0]}','{g[0]}');")

# 13. 테이블
for i in range(len(car_df)):
    cur.execute(f"SELECT manuf_id FROM manufacturer WHERE manuf_name='{car_df.loc[i]['제조사']}';")
    f1 = cur.fetchone()

    cur.execute(f"SELECT fuel_id FROM fuel WHERE fuel_name='{car_df.loc[i]['유종']}';")
    f2 = cur.fetchone()

    cur.execute(f"SELECT grade_id FROM grade WHERE grade_score='{car_df.loc[i]['등급']}';")
    f3 = cur.fetchone()

    cur.execute(f"SELECT car_form_id FROM car_form WHERE car_form_name='{car_df.loc[i]['자동차형식']}';")
    f4 = cur.fetchone()

    cur.execute(f"SELECT fuel_supply_id FROM fuel_supply WHERE fuel_supply_name='{car_df.loc[i]['연료공급방식']}';")
    f5 = cur.fetchone()
    
    try:
        cur.execute(f"""
            INSERT INTO car_model (model_name, manuf_id, fuel_id, displacement, weight, fuel_efficiency, grade_id, car_form_id, fuel_supply_id, CO2)
            VALUES (\"{car_df.loc[i]['모델명']}\", '{f1[0]}', '{f2[0]}', '{car_df.loc[i]['배기량']}', '{car_df.loc[i]['공차중량']}', '{float(car_df.loc[i]['복합연비'])}', '{f3[0]}', '{f4[0]}', '{f5[0]}', '{float(car_df.loc[i]['CO2배출량'])}');
        """)
    except sqlite3.OperationalError:
        pass

conn.commit()
conn.close()
