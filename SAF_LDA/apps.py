from flask import Flask, render_template, request, flash, redirect, session, abort, make_response, url_for, send_file
import mysql.connector
import os
import pickle
import timeit
import numpy as np
import math as ma
import pandas as pd
from library.preprocess import *
from library.svmseq import SVMTraining,SVMTesting,laporanNilai


#==============================================================================================================#
#==============================================================================================================#

app = Flask(__name__)
app.secret_key = "rahasia loooh"
#==============================================================================================================#

db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="rfesvm"
)
#==============================================================================================================#

@app.route("/")
def index():
    return render_template(
        'home.html')

#==============================================================================================================#
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////#
#==============================================================================================================#

@app.route('/dataset')
def view_dataset():
    cursor = db.cursor()
    cursor.execute("SELECT * from dataset ORDER BY id_data desc")
    daftar = cursor.fetchall()
    cursor.close()
    
    return render_template('view_database.html', daftar=daftar, active='adatabase')

@app.route('/form_upload', methods=['POST']) #ini harus pake get krn ngerender template yg ga pake post
def form_upload():
    df = pd.read_csv(request.files.get('file'))
    dataheader = df.columns.values#pengembaliannya array
    if (len(dataheader) <= 50) | (len(df) <= 100) :
        dataX = np.array(df)
    else :
        df_elements = df.sample(n=50)
        dataX = np.array(df_elements)


    ##PICKLING
    perlu = { 'dtset' : df }
    namah = 'parssob' #buat parsing dataset

    #membuat suatu file
    some = open('database/'+namah, 'wb')
    
    #mendump objek ke file
    pickle.dump(perlu, some)
    some.close()

    #hapus perlu dari daftar memori
    del perlu

    #ini buat ngecek aja siii kebaca apa engga
    print(df.shape)
    print("kebaca woooy")

    return render_template('upload_dataset.html', data = dataX, kol = len(dataheader), bar = len(df), header = dataheader, active='adatabase')

    #return render_template('upload_dataset1.html', tabel= tabel_data, data = dataX, active='adatabase')

    # if request.method == 'POST':
    # return render_template('upload_dataset.html', active='adatabase')

@app.route('/upload', methods=['POST'])
def upload():
    nama = request.form['namaFile']
    header = request.form['header'] #nama kolom targetnya
    label1 = request.form['label1']
    label2 = request.form['label2']

    if request.method == "POST":
        cursor = db.cursor()
        sql = "INSERT INTO dataset (id_data,nama,header,label1,label2) VALUES (%s,%s,%s,%s,%s)"
        val = ('',nama,header,label1,label2)
        cursor.execute(sql,val)
        idbaru = cursor.lastrowid
        db.commit()

        #Buat ngecek aja
        print("sampe sini bisa")
        print(idbaru)

        #Tutup koneksi
        cursor.close()

        #Buka Pickle yang tadi udah disimpen
        infile = open('database/parssob','rb')
        diterima = pickle.load(infile)

        dtset = diterima['dtset']
        
        infile.close()

        #Membuat nama file
        namabaru = str(idbaru)+'_'+nama+'.csv'

        #Data yang tadi dibuat ke file csv
        dtset.to_csv('database/'+namabaru, index=False, header=True)

        flash('Dataset berhasil ditambahkan!')
        return redirect('/dataset')

    else:
        return render_template('500.html', bek='bdata')

@app.route('/hapus_data/<string:id_data>', methods=["GET"])
def hapus(id_data):
    #Membuka koneksi
    cursor = db.cursor()

    #Menghapus filenya dulu
    cursor.execute("SELECT nama FROM dataset WHERE id_data=%s", (id_data,))
    hasil = cursor.fetchone()
    nama = str(hasil[0])

    #buat ngecek
    print("\n\n",nama)
    print(type(nama),"\n\n")

    filename = id_data+'_'+nama+'.csv'
    print(filename)
    folder = 'database/'
    fullpath = os.path.join(folder, filename)
    print(fullpath)

    if os.path.exists(fullpath):
        os.remove(fullpath) #menghapus filenya

        #Menghapus databasenya
        cursor.execute("DELETE FROM dataset WHERE id_data=%s", (id_data,))
        db.commit()
        cursor.close()

        flash('Dataset berhasil dihapus!')
        return redirect('/dataset')

    else:
        cursor.close()
        return render_template('500.html', bek='bdata')

@app.route('/lihat_data/<string:id_data>', methods=["GET"])
def lihat(id_data):
    #Membuka koneksi
    cursor = db.cursor()

    #Menghapus filenya dulu
    cursor.execute("SELECT nama FROM dataset WHERE id_data=%s", (id_data,))
    hasil = cursor.fetchone()
    nama = str(hasil[0])
    cursor.close()

    #buat ngecek
    print("\n\n",nama)
    print(type(nama),"\n\n")

    filename = id_data+'_'+nama+'.csv'
    print(filename)
    folder = 'database/'
    fullpath = os.path.join(folder, filename)
    print(fullpath)

    if os.path.exists(fullpath):
        df = pd.read_csv(fullpath)
        dataheader = df.columns.values#pengembaliannya array
        dataX = np.array(df)

        return render_template('lihat_data.html', data = dataX, header = dataheader, active='adatabase')

    else:
        return render_template('500.html', bek='bdata')


#==============================================================================================================#
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////#
#==============================================================================================================#


@app.route('/proses1') #SVM
def form_proses1():
    cursor = db.cursor()
    cursor.execute("SELECT id_data, nama from dataset ORDER BY id_data desc")
    daftar = cursor.fetchall()
    cursor.close()
    
    return render_template('form_proses1.html', daftar=daftar, active='aproses')

@app.route('/terima_proses1', methods=['POST']) #SVM
def terima1():
     ##MEMBACA INPUTAN
    if request.method    == 'POST':
        id_dataset = int(request.form['datasid'])
        lrate = float(request.form['lrate'])
        lambdas = float(request.form['lammada'])
        ce = float(request.form['ce'])
        epsi = float(request.form['epsi'])
        maepoh = int(request.form['epoh'])

        ##MENGAMBIL INPUTAN LAIN DARI DATABASE
        cursor = db.cursor()
        cursor.execute("SELECT * from dataset WHERE id_data=%s", (id_dataset,))
        daftar = cursor.fetchone()

        idfile = daftar[0]
        namah = daftar[1]
        namaheader = daftar[2]
        label1 = daftar[3] #ini label positif
        label2 = daftar[4] #ini label negatif
        cursor.close()

        namafile = str(idfile)+'_'+namah+'.csv'

        dataset = pd.read_csv('database/'+namafile)
        # print(dataset)
        # print("\n\n\n")

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////#
        ##MEMISAHKAN DATA DENGAN LABEL
        dataheader = dataset.columns.values#pengembaliannya array
        indeks = -1
        for i in range(len(dataheader)):
            if (dataheader[i] == namaheader) :
                indeks = i
        # if (indeks == -1) :
        #     fail = "Pastikan File yang dikirim memiliki header label yang dimasukkan"
        #     return redirect(url_for('svm1', fail=fail))

        dataX = dataset.drop([namaheader], axis=1) #ini data, bentuk df
        dataX = np.array(dataX)
        dataX = MinMax(dataX,0,1) #sekalian di normalisasi

        labelX = dataset.loc[:,namaheader] #ini label, bentuk df
        labelX = np.array(labelX)
        label = konversi_label(labelX,label1,label2)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////#
        ##MEMISAHKAN DATA SESUAI LABEL (untuk keperluan bagi data)
        dataPos = [] #berisi index data2 yang berlabel positif
        dataNeg = [] #berisi index data2 yang berlabel negatif
        #dataPos
        for i in range(len(dataX)):
            if (label[i] == 1):
                dataPos.append(i) #bentuk list
        #dataNeg
        for i in range(len(dataX)):
            if (label[i] == -1):
                dataNeg.append(i) #bentuk list

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////#
        kf = int(request.form['kafold'])

        ###Membuat list sejumlah K
        KFold = []
        for i in range(kf):
            KFold.append([])

        ###Distribusi + dan - ke wadah
        #dataPos
        j = 0
        for i in range(len(dataPos)):
            if (j != (kf-1)):
                KFold[j].append(dataPos[i])
                j = j + 1
            else:
                KFold[j].append(dataPos[i])
                j = 0
        #dataNeg
        o = 0
        for i in range(len(dataNeg)):
            if (o != (kf-1)):
                KFold[o].append(dataNeg[i])
                o = o + 1
            else:
                KFold[o].append(dataNeg[i])
                o = 0
        ###Masuk perulangan, menentukan mana data test mana data training, lalu di training dan testing
        k = 0
        akur = []
        sensi = []
        spesi = []
        while(k != kf):
            ###Menentukan data test
            test = KFold[k]
            ###Menentukan data training
            train = []
            for i in range(kf):
                if(i != k):
                    train = train + KFold[i]

            ###Melakukan pelatihan dan pengetesan
            dataTrain = []
            labelTrain = []
            for i in range(len(train)):
                dataTrain.append(dataX[train[i]])
                labelTrain.append(label[train[i]])
            dataTrain = np.array(dataTrain)
            labelTrain = np.array(labelTrain)

            dataTest = []
            labelTest = []
            #Scan label test untuk sub dataset yg baru
            dataPositif = [] #berisi index test data2 yang berlabel positif
            dataNegatif = [] #berisi index test data2 yang berlabel negatif

            for i in range(len(test)):
                dataTest.append(dataX[test[i]])
                labelTest.append(label[test[i]])
                
                if (label[test[i]] == 1) :
                    dataPositif.append(i) #bentuk list
                else :
                    dataNegatif.append(i) #bentuk list
            
            dataTest = np.array(dataTest)
            labelTest = np.array(labelTest)
            
            (support,alpha) = SVMTraining(dataTrain,labelTrain,lrate,lambdas,ce,epsi,maepoh)
            (Accur,predic) = SVMTesting(dataTrain,labelTrain,dataTest,labelTest,alpha,support,lambdas)
            (sensit,spesif,EL) = laporanNilai(predic,labelTest,dataPositif,dataNegatif)
            
            akur.append(round(Accur,2))
            sensi.append(round(sensit,2))
            spesi.append(round(spesif,2))
            #print("\n\n")
            print("fold :", k)
            k = k + 1
        # for i in range(len(akur)):
        #     print('\nAkurasi fold-',i+1,' : %.2f' % akur[i], '%')
        hasilnya = round(np.average(akur) ,2)
        hasilnya2 = round(np.average(sensi) ,2)
        hasilnya3 = round(np.average(spesi) ,2)
        sisa = round(100 - hasilnya, 2)
        # print('\nRata-rata akurasi : %.2f' % np.average(akur),'%')
       
        return render_template('hasil_form1.html', akur = hasilnya, sisanya = sisa, listakur = akur,
            sensi = hasilnya2, listsensi = sensi, spesi = hasilnya3, listspesi = spesi, kfol = kf,
            id_data = id_dataset, lrate = lrate, lambdas = lambdas, ce = ce, epsi = epsi, maepoh = maepoh,
            active='aproses')
    
    else :
        return render_template('500.html', bek='bproses')

@app.route("/proses2", methods=['POST']) #RFE
def rfe():
    ##MEMBACA INPUTAN
    if request.method    == 'POST':
        id_dataset = int(request.form['datasid'])
        lrate = float(request.form['lrate'])
        lambdas = float(request.form['lammada'])
        ce = float(request.form['ce'])
        epsi = float(request.form['epsi'])
        maepoh = int(request.form['epoh'])
        kafold = int(request.form['kf'])

        ##MENGAMBIL INPUTAN LAIN DARI DATABASE
        cursor = db.cursor()
        cursor.execute("SELECT * from dataset WHERE id_data=%s", (id_dataset,))
        daftar = cursor.fetchone()

        idfile = daftar[0]
        namah = daftar[1]
        namaheader = daftar[2]
        label1 = daftar[3] #ini label positif
        label2 = daftar[4] #ini label negatif
        cursor.close()

        namafile = str(idfile)+'_'+namah+'.csv'

        datas = pd.read_csv('database/'+namafile)
        # print(dataset)
        # print("\n\n\n")

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////#
        ##MEMISAHKAN DATA DENGAN LABEL
        dataheader = datas.columns.values#pengembaliannya array
        indeks = -1
        headerX = []
        for i in range(len(dataheader)):
            if (dataheader[i] == namaheader) :
                indeks = i
            else :
                headerX.append(dataheader[i])
        #print("\nheader:\n",headerX)
        # if (indeks == -1) :
        #     fail = "Pastikan File yang dikirim memiliki header label yang dimasukkan"
        #     return flask.redirect(flask.url_for('rfe1', fail=fail))

        dataX = datas.drop([namaheader], axis=1) #ini data, bentuk df
        dataX = np.array(dataX)
        dataX = MinMax(dataX,0,1) #sekalian di normalisasi

        labelX = datas.loc[:,namaheader] #ini label, bentuk df
        labelX = np.array(labelX)
        label = konversi_label(labelX,label1,label2)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////#
        ##MEMISAHKAN DATA SESUAI LABEL
        ##INITIALISASI
        s = []
        for i in range(len(headerX)):
            s.append(i)
        #print("\nsurviving feature:\n",s)
        r = []
        dataXS = np.transpose(dataX) #biar bisa ngambil perfitur

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////#
        ##PERULANGAN RFE
        while(len(s)!=0):
            print("sisa fitur :", len(s))
            dataset = []
            for i in range(len(s)):
                dataset.append(dataXS[s[i]])

            dataset = np.transpose(dataset)#ngebalikin sebelum masuk SVM

            ##SVM TRAINING
            (support,alpha) = SVMTraining(dataset,label,lrate,lambdas,ce,epsi,maepoh)

            ##COMPUTE WEIGHT VECTOR
            w = 0
            for i in range(len(dataset)):
                we = alpha[i]*label[i]*dataset[i]
                w = w + we

            ##COMPUTE THE RANKING CRITERIA
            for i in range(len(w)):
                w[i] = w[i]*w[i]

            ##FIND THE FEATURE WITH THE SMALLEST RANKING CRITERION
            fmin = w[0]
            for i in range(len(w)):
                if(w[i]<=fmin):
                    fmin = w[i]
                    c = i

            ##UPDATE FEATURE RANKED LIST
            r.append(s[c])
            ##ELIMINATE THE FEATURE
            s.remove(s[c])

            #print("\nsurviving feature:\n",s)
            #print("\nrank feature:\n",r)
        r.reverse()

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////#
        ##MEMBUAT RANKING
        rank = [] #ini untuk yang ditampilin
        for i in range(len(r)):
            rank.append(headerX[r[i]]) 

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////#
        ##Mempersiapkan data untuk dimodif jadi data baru
        datab = datas.drop([namaheader], axis=1)
        datalab = np.array(datab)
        datalab = np.transpose(datalab)#ngebalikin

        ##MEMBENTUK DATA BARU
        headerbaru = []
        databaru = []
        for i in range(len(r)):
            headerbaru.append(headerX[r[i]])
            databaru.append(datalab[r[i]]) #datab ini data dengan label ya!w
        headerbaru.append(namaheader)#ini masukkin header labelnya
        databaru.append(labelX) #ini masukkin labelnya

        databaru = np.array(databaru)#krn mau di transpose
        databaru = np.transpose(databaru)#ngebalikin lagi
        databaru = list(databaru)#krn mau di insert list
        databaru.insert(0,headerbaru)
        databaru = np.array(databaru)#krn dataframe ga terima list

        my_df = pd.DataFrame(databaru)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////#
        #AMBIL SISA INFO
        akur = float(request.form['akur'])
        sensi = float(request.form['sensi'])
        spesi = float(request.form['spesi'])
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////#
        ##PICKLING
        perlu = {'dataid' : id_dataset, 'lrate' : lrate, 'lambdas' : lambdas, 'ce' : ce, 'epsi' : epsi, 'maepoh' : maepoh,
                    'akur' : akur, 'sensi' : sensi, 'spesi' : spesi, 'kafold' : kafold, 'dtset' : my_df}
        namafile = 'perlubanget'

        #membuat suatu file
        some = open('library/'+namafile, 'wb')
        
        #mendump objek ke file
        pickle.dump(perlu, some)
        some.close()

        #hapus perlu dari daftar memori
        del perlu

        return render_template('hasil_form2.html', rank = rank, active='aproses')

    else:
        return render_template('500.html', bek='bproses')

#==============================================================================================================#
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////#
#==============================================================================================================#
@app.route("/proses3") #Simpan
def simpan_hasil():
    
    infile = open('library/perlubanget','rb')
    diterima = pickle.load(infile)

    id_dataset = diterima['dataid']
    lrate = diterima['lrate']
    lambdas = diterima['lambdas']
    ce = diterima['ce']
    epsi = diterima['epsi']
    maepoh = diterima['maepoh']
    kafold = diterima['kafold']
    akur = diterima['akur']
    sensi = diterima['sensi']
    spesi = diterima['spesi']
    evaluasi = "belum"
    dtsetbaru = diterima['dtset']

    infile.close()

    print("lrate : ",lrate)
    print("lambda : ",lambdas)
    print("ce : ",ce)
    print("epsi : ",epsi)
    print("akurasi : ",akur)
    print("sensi : ",sensi)
    print("spesi : ",spesi)

    cursor = db.cursor()
    cursor.execute("SELECT nama FROM dataset WHERE id_data=%s", (id_dataset,))
    hasil = cursor.fetchone()
    nama = str(hasil[0])
    cursor.close()

    cursor1 = db.cursor()
    sql = "INSERT INTO riwayat_hasil (id_hasil,id_data,nama_dtset,lrate,lammada,ce,epsi,maxepoh,kafold,akurasi,sensi,spesi,evaluasi) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    val = ('',id_dataset,nama,lrate,lambdas,ce,epsi,maepoh,kafold,akur,sensi,spesi,evaluasi)
    cursor1.execute(sql,val)
    idhasilbaru = cursor1.lastrowid
    db.commit()
    cursor1.close()

    #Buat ngecek aja
    print("sampe sini bisa")
    print(idhasilbaru)

    #Tutup koneksi
    cursor.close()

    ##MENGCONVERT DATASET BARU
    namafbaru = str(idhasilbaru)+"_hasil.csv"
    dtsetbaru.to_csv('hasil/'+namafbaru, index=False, header=False)

    flash('Informasi hasil proses berhasil disimpan!')
    return redirect('/riwayat_hsl')

@app.route("/riwayat_hsl") #Simpan
def tampil_hasil():
    cursor = db.cursor()
    cursor.execute("SELECT * from riwayat_hasil ORDER BY id_hasil desc")
    daftar_hasil = cursor.fetchall()
    cursor.close()
    
    return render_template('view_hasil.html', daftar_hasil=daftar_hasil, active='ahisto')

# @app.route("/lihat_rank/<string:id_hasil>", methods=["GET"]) #Simpan
# def tampil_rank(id_hasil):
#     nama = id_hasil+"_hasil.csv"
#     data_hasil = pd.read_csv('hasil/'+nama)
#     header = data_hasil.columns.values#pengembaliannya array
#     dataheader=header[:-1]

#     return render_template('view_rank.html', rank=dataheader, active='ahisto')

@app.route('/download_hasil/<string:id_hasil>', methods=["GET"])
def download_hasil(id_hasil):
    file_name = id_hasil+"_hasil.csv"
    folder = 'hasil/'
    fullpath = os.path.join(folder, file_name)

    if os.path.exists(fullpath):
        return send_file(fullpath, as_attachment=True)
    else:
        return render_template('500.html', bek='bhisto')

@app.route('/cek_evaluasi/<string:id_hasil>', methods=["GET"])
def cek_evaluasi(id_hasil):

    #CEK ADA YANG SALAH GA
    file_name = id_hasil+"_eval.csv"
    folder = 'hasil/'
    fullpath = os.path.join(folder, file_name)

    if os.path.exists(fullpath):
        cursor = db.cursor()
        cursor.execute("UPDATE riwayat_hasil SET evaluasi=%s WHERE id_hasil=%s", ("sudah",id_hasil,))
        db.commit()
        cursor.close()
    
        return redirect('/lihat_eval?id_hasil='+str(id_hasil)+'&status=sudah')
    
    else :
        ##MENGAMBIL INFO DARI DATABASE
        cursor1 = db.cursor()
        cursor1.execute("SELECT * from riwayat_hasil WHERE id_hasil=%s", (id_hasil,))
        daftar = cursor1.fetchone()

        id_data = str(daftar[1])
        #nama_data = daftar[2]
        lrate = daftar[3]
        lammada = daftar[4]
        ce = daftar[5]
        epsi = daftar[6]
        maepoh = daftar[7]
        kafold = daftar[8]

        cursor1.close()

        cursor2 = db.cursor()
        cursor2.execute("SELECT label1,label2 from dataset WHERE id_data=%s", (id_data,))
        daftar1 = cursor2.fetchone()

        label1 = daftar1[0]
        label2 = daftar1[1]

        cursor2.close()

        ##MEMBACA FILE
        namafile = id_hasil+"_hasil.csv"
        dataset = pd.read_csv('hasil/'+namafile)
        header = dataset.columns.values#pengembaliannya array
        
        ##MENDEFINISIKAN BEBERAPA VARIABEL
        some = len(header)
        best_centino = 0
        noah = []
        noah.append(("akurasi","sensitifitas","spesifisitas"))#noah.append(("akurasi","sensitifitas","spesifisitas","runtime"))
        best = 0

        ##MASUK PERULANGAN EVALUASI
        for x in range(1,some):
            print("ini yang ke :", x) #untuk cek proses
            #mulai_waktu = timeit.default_timer()

            dataX = dataset.iloc[:,:x]
            dataX = np.array(dataX)
            dataX = MinMax(dataX,0,1)

            ####KONVERSI LABEL
            labelX = dataset.iloc[:,(some-1)]
            labelX = np.array(labelX)
            label = konversi_label(labelX, label1, label2)
            #print(label)

            ####1.MISAHIN DATA SESUAI LABEL
            dataPos = []
            dataNeg = []
            #dataPos
            for i in range(len(dataX)):
                if ((label[i] == 1)):
                    dataPos.append(i)
            dataPos = np.array(dataPos) #berisi index data2 yang berlabel positif
            #print("banyak data label 1 :",len(dataPos))

            #dataNeg
            for i in range(len(dataX)):
                if (label[i] == -1):
                    dataNeg.append(i)
            dataNeg = np.array(dataNeg) #berisi index data2 yang berlabel negatif
            #print("banyak data label 2 :",len(dataNeg))

            ###3.Bikin list sejumlah K
            KFold = []
            for i in range(kafold):
                KFold.append([])

            ###4. mendistribusikan + dan - ke wadah
            #dataPos
            j = 0
            for i in range(len(dataPos)):
                if (j != (kafold-1)):
                    KFold[j].append(dataPos[i])
                    j = j + 1
                else:
                    KFold[j].append(dataPos[i])
                    j = 0

            #dataNeg
            o = 0
            for i in range(len(dataNeg)):
                if (o != (kafold-1)):
                    KFold[o].append(dataNeg[i])
                    o = o + 1
                else:
                    KFold[o].append(dataNeg[i])
                    o = 0

            #print(KFold)

            ###5. masuk perulangan, menentukan mana data test mana data training, lalu di training dan testing
            k = 0
            akur = []
            sensi = []
            spesi = []
            while(k != kafold):
                ###5.1 menentukan data test
                test = KFold[k]
                #print("fold ke-",k+1)
                #print("datatest : \n",test)

                ###5.2 menentukan data training
                train = []
                for i in range(kafold):
                    if(i != k):
                        train = train + KFold[i]
                #print("dataset : \n",train)

                ###5.3 melakukan pelatihan dan pengetesan
                dataTrain = []
                labelTrain = []
                for i in range(len(train)):
                    dataTrain.append(dataX[train[i]])
                    labelTrain.append(label[train[i]])
                dataTrain = np.array(dataTrain)
                labelTrain = np.array(labelTrain)

                dataTest = []
                labelTest = []
                #Scan label test untuk sub dataset yg baru
                dataPositif = [] #berisi index test data2 yang berlabel positif
                dataNegatif = [] #berisi index test data2 yang berlabel negatif

                for i in range(len(test)):
                    dataTest.append(dataX[test[i]])
                    labelTest.append(label[test[i]])

                    if (label[test[i]] == 1) :
                        dataPositif.append(i) #bentuk list
                    else :
                        dataNegatif.append(i) #bentuk list

                dataTest = np.array(dataTest)
                labelTest = np.array(labelTest)

                (support,alpha) = SVMTraining(dataTrain,labelTrain,lrate,lammada,ce,epsi,maepoh)
                (Accur,predic) = SVMTesting(dataTrain,labelTrain,dataTest,labelTest,alpha,support,lammada)
                (sensit,spesif,EL) = laporanNilai(predic,labelTest,dataPositif,dataNegatif)

                akur.append(round(Accur,2))
                sensi.append(round(sensit,2))
                spesi.append(round(spesif,2))
                #print("\n\n")
                print("fold :", k)
                k = k + 1

            # for i in range(len(akur)):
            #print('\nAkurasi fold-',i+1,' : %.2f' % akur[i], '%')
            ##NGUKUR WAKTU
            #selesai_waktu = timeit.default_timer()
            #jadinya = round(selesai_waktu - mulai_waktu ,4)

            centino = round(np.average(akur) ,2)
            centino2 = round(np.average(sensi) ,2)
            centino3 = round(np.average(spesi) ,2)
            noah.append((centino,centino2,centino3))#noah.append((centino,centino2,centino3,jadinya))
        ##MENAMPILKAN & MENGELUARKAN HASIL
        myarray = np.vstack(noah)
        print(myarray)
        ##MENGCONVERT HASIL EVALUASI
        my_df = pd.DataFrame(myarray)
        namanya = str(id_hasil)+"_eval.csv"   
        my_df.to_csv('hasil/'+namanya, index=False, header=False)
        ##MASUKIN EVAL TADI KE DATABASE
        cursor3 = db.cursor()
        cursor3.execute("UPDATE riwayat_hasil SET evaluasi=%s WHERE id_hasil=%s", ("sudah",id_hasil,))
        db.commit()
        cursor3.close()

        return redirect('/lihat_eval?id_hasil='+str(id_hasil)+'&status=sudah')

@app.route("/lihat_eval", methods=["GET"]) #Simpan
def tampil_eval():

    id_hasil  = request.args.get('id_hasil', None)
    status  = request.args.get('status', None)

    nama = id_hasil+"_hasil.csv"
    data_hasil = pd.read_csv('hasil/'+nama)
    header = data_hasil.columns.values#pengembaliannya array
    dataheader=header[:-1]

    ##BEDA FILE YAAA
    nama = id_hasil+"_eval.csv"
    folder = 'hasil/'
    fullpath = os.path.join(folder, nama)

    if os.path.exists(fullpath):
        data_eval = pd.read_csv('hasil/'+nama)
        data_eval = np.array(data_eval)
    else:
        data_eval = "nopepe" #ini intinya ga bisa dikasih error, kalo mau ya ganti status = belum

    return render_template('view_eval.html', rank = dataheader,idnya = id_hasil, status=status, eval=data_eval, active='ahisto')

@app.route('/hapus_hasil/<string:id_hasil>', methods=["GET"])
def hapus_hasil(id_hasil):
    #Menghapus filenya dulu
    folder = 'hasil/'

    data_hasil = id_hasil+"_hasil.csv"
    data_eval = id_hasil+"_eval.csv"

    fullpath1 = os.path.join(folder, data_hasil)
    fullpath2 = os.path.join(folder, data_eval)

    if os.path.exists(fullpath1):
        os.remove(fullpath1) #menghapus filenya

        #mengecek data_eval
        if os.path.exists(fullpath2):
            os.remove(fullpath2) #menghapus filenya

        #Menghapus databasenya
        cursor = db.cursor()
        cursor.execute("DELETE FROM riwayat_hasil WHERE id_hasil=%s", (id_hasil,))
        db.commit()
        cursor.close()

        flash('Informasi hasil proses berhasil dihapus!')
        return redirect('/riwayat_hsl')

    else:
        return render_template('500.html', bek='bhisto')

# @app.route("/500error")
# def eror500():
#     return render_template('500.html', bek='bdata')
# db.close() #ini untuk ngedisconect dari app nya

if __name__ == '__main__':
    app.run(debug = True)
    # from library.preprocess import *
    # from library.svmseq import SVMTraining
    