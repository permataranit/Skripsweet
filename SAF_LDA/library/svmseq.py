import numpy as np
from sklearn.metrics import accuracy_score

def FAlpha(label): #fungsi untuk membuat alpha awal
    alphaX = []  
    for i in range(len(label)):
        alphaX.append(0)
    alphaX = np.array(alphaX)
    return alphaX

def FMatrixHes1(datil,target,lamda): #fungsi untuk konversi ke matrix hessian (sudah termasuk kernel linier)
    matrixDij = []
    for i in range(len(datil)):
        titip = []
        for j in range(len(datil)):
            a = np.transpose(datil[j])
            data = np.dot(a,datil[i])
            data = target[i]*target[j]*(data + (lamda*lamda))
            #print(data)
            titip.append(data)
        matrixDij.append(titip)
    matrixDij = np.array(matrixDij)
    #print(matrixDij)
    
    return matrixDij

def FErorRate(alpha,matrix): #fungsi untuk menghitung error per baris
    Erorrate = []
    for i in range(len(matrix)):
        Totbar=0
        for j in range(len(matrix[i])):
            index = matrix[i][j]*alpha[j] #sebenernya i j itu sama panjangnya. ati ati makenya maemunah~
            Totbar = Totbar + index
        Erorrate.append(Totbar)
    Erorrate = np.array(Erorrate)
    #print('Erorr Rate Dij:')
    #print(Erorrate)
    return Erorrate

def FDeltaAlpha(gamma,Erorrate,alpha,C): #fungsi untuk menghitung delta error per baris
    Delta = []
    for i in range(len(Erorrate)):
        index = gamma*(1-Erorrate[i])
        alphamin = alpha[i]*-1
        index2 = C-alpha[i]
        delt=min(max(index,alphamin),index2)
        Delta.append(delt)
    Delta = np.array(Delta)
    #print('DeltaError Dij:')
    #print(DeltaError)
    return Delta

def FAlphaBaru(alpha,DeltaAlpha):
    alphaBaru = []
    for i in range(len(alpha)):
        alphaB = alpha[i]+DeltaAlpha[i]
        alphaBaru.append(alphaB)
    alphaBaru = np.array(alphaBaru)
    # print('Alpha Baru Dij:')
    # print(alphaBaru)
    return alphaBaru

def FCariSV(alpha,C,label):
    SupportVec = []
    for i in range(len(alpha)):
        if ((alpha[i] > 0)&(alpha[i]<=C)):
            SupportVec.append(i)
    SupportVec = np.array(SupportVec)
    #print("ini SV")
    #print(SupportVec)

    return (SupportVec)

def FCariB1(sv,matriks,alpha,target):
    svs = []
    for i in range(len(sv)):
        svs.append(matriks[sv[i]])
    sigma2 = 0
    for s in range(len(sv)):
        sigma = 0
        for m in range(len(sv)):
            dummy = svs[m]
            dummy = np.transpose(dummy)
            data = np.dot(dummy,svs[s])
            data = data * alpha[m] * target[m]
            sigma = sigma + data
        dummy2 = target[s] - sigma
        sigma2 = sigma2 + dummy2

    bias = sigma2/(len(sv))
    #print("bias = ",bias)

    return bias
        
def SVMTraining(matriks,label,gamma,lamda,C,epsilon, maxEpoh):
    
    #algoritma
    alpha = FAlpha(label)
    matrixH = FMatrixHes1(matriks,label,lamda)
    maxDeltaAlpha = 2 #ini bisa angka berapa aja sih asal ga 0
    epoh = 1
    while((maxDeltaAlpha > epsilon) and (epoh <= maxEpoh)):
        #print("\nEpoch ke-",epoh)
        ErrorRate = FErorRate(alpha,matrixH)
        DeltaAlpha = FDeltaAlpha(gamma,ErrorRate,alpha,C)
        alpha = FAlphaBaru(alpha,DeltaAlpha)
        # maxDeltaAlpha = DeltaAlpha[0]
        # for i in range(len(DeltaAlpha)):
        #     maxim = abs(DeltaAlpha[i])
        #     if(maxim>maxDeltaAlpha):
        #         maxDeltaAlpha = maxim
        maxDeltaAlpha = max(DeltaAlpha)#kondisi berhenti
        epoh = epoh + 1
    #print("\nAlpha :")
    #print(alpha)
    SV = FCariSV(alpha, C, label)

    # print("epoch : ",epoh)
    #bias = FCariB1(SV,matriks,alpha,label)
    return (SV,alpha) #(bias,alpha)

################# TESTING ########################


# def caraUji1(dataUji,dataLatih,target,alpha,B):
#     prediksi = []
#     for i in range(len(dataUji)):
#         total = 0
#         for j in range(len(dataLatih)):
#             we = alpha[j]*target[j]*(np.dot(dataLatih[j],dataUji[i]))
#             total = total + we
#         total = total + B
#         #print(total)
#         if (total >= 0):
#             prediksi.append(1)
#         else:
#             prediksi.append(-1)
#     prediksi = np.array(prediksi)
#     #print('\nHasil Prediksi:')
#     #print(prediksi)
#     return prediksi

def caraUji3(dataLatih,dataUji,sv,alpha,target,lamda):
    svs = []
    for i in range(len(sv)):
        svs.append(dataLatih[sv[i]])

    prediksi = []
    for i in range(len(dataUji)):
        total = 0
        for j in range(len(svs)):
            paris = svs[j] #svs merupakan dataLatih[sv[j]]
            paris = np.transpose(paris)
            rain = np.dot(paris,dataUji[i])
            we = (alpha[j]*target[sv[j]]*rain) + (alpha[j]*target[sv[j]]*lamda*lamda)
            total = total + we
        # print(total)
        if (total >= 0):
            prediksi.append(1)
        else:
            prediksi.append(-1)
    prediksi = np.array(prediksi)
    #print('\nHasil Prediksi:')
    #print(prediksi)
    return prediksi

# def Cakurasi(labelUji,pred):
#     akurasi = 0
#     for i in range(len(labelUji)):
#         if(labelUji[i]==pred[i]):
#             akurasi = akurasi + 1
#     print("akurasi =",akurasi," / ",len(labelUji))

def SVMTesting(matrixData,labelData,matrixUji,labelUji,alpha,sv,lamda):
#SVMTesting(matrixData,labelData,matrixUji,labelUji,alpha,B):
    pred = caraUji3(matrixData,matrixUji,sv,alpha,labelData,lamda)
    #caraUji1(matrixUji,matrixData,labelData,alpha,B)
    akurasi = accuracy_score(labelUji,pred)*100
    #print('\n\nAkurasi : %.2f' % akurasi, '%')
    return (akurasi,pred)

def laporanNilai(pred,labelUji,dapos,daneg):
    errorlabel = 0

    TN = 0
    FP = 0
    for i in range(len(dapos)):
        if (labelUji[dapos[i]]==pred[dapos[i]]):
            #print("label :" , labelUji[dapos[i]])
            #print("pred :" , pred[dapos[i]])
            TN = TN + 1
        elif(pred[dapos[i]] == -1):
            FP = FP + 1
        else:
            errorlabel = errorlabel + 1

    TP = 0
    FN = 0
    for i in range(len(daneg)):
        if (labelUji[daneg[i]]==pred[daneg[i]]):
            TP = TP + 1
        elif(pred[daneg[i]] == 1):
            FN = FN + 1
        else:
            errorlabel = errorlabel + 1

    sensit = float(TP/(TP+FN))*100
    spesif = float(TN/(FP+TN))*100

    return (sensit,spesif,errorlabel)