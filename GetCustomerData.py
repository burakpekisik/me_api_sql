import mysql.connector
import userInfo

def getCustomerData():
    # MySQL bağlantısı
    mydb = mysql.connector.connect(
        host=userInfo.db_host,
        user=userInfo.db_username,
        password=userInfo.db_password,
        database=userInfo.db_database
    )
    
    # MySQL üzerinden veri çekme
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM customer_list")

    # Sütun isimlerini al
    column_names = [i[0] for i in mycursor.description]

    # Verileri çek ve DataFrame'e dönüştür
    data = [dict(zip(column_names, row)) for row in mycursor.fetchall()]

    # DataFrame'i oluştur
    # df = pd.DataFrame(data)

    # MySQL bağlantısını kapat
    mycursor.close()
    mydb.close()

    return data