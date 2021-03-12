import numpy as np

def MinMax(dats,newMin,newMax) :
	dataX = np.array(dats) #ubah ke array
	dataX = dataX.transpose()

	dataBaru = [] #untuk nampung data baru

	#1. masuk rekursif baris
	for re in dataX:

		#2. ambil satu variabel
		varia = [] #bentuk list
		for me in re:
			varia.append(me)

		#3. Mencari min dan max dalam variabel dan menyiapkan perhitungan lain
		dataMin = min(varia)
		dataMax = max(varia)
		doldol = newMax - newMin
		daldal = dataMax - dataMin
		variabel = []
		
		#4. Melakukan perhitungan
		for se in varia:
			if ((dataMin == 0) and (dataMax == 0)):
				variabel.append(0)
			else:
				yeah = se - dataMin
				haha = ((yeah/daldal)*doldol)+newMin
				variabel.append(haha)

		#5. masukkin ke array baru
		dataBaru.append(variabel)

	#6. menyiapkan output
	dataBaru = np.array(dataBaru) #ngubah ke bentuk array
	dataBaru = dataBaru.transpose()
	# print('\n\nData Normalisasi:')
	# print(dataBaru)
	# print('\n')
	dataBaru = dataBaru.tolist() #balikin lagi ke bentuk list
	
	return dataBaru

def konversi_label(data,labelpos,labelneg) :
	labeldata = [] #bentuk list
	for i in range(len(data)):
		if ((data[i].lower() == labelpos.lower())):
			labeldata.append(1)
		elif((data[i].lower()==labelneg.lower())):
			labeldata.append(-1)
		else:
			labeldata.append(0)

	return labeldata #bentuk list
