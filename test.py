tppdata=natsort.natsorted(glob.glob(datdir+'/'+'*'+self.det_roi+'.txt'))[:-1]*self.bottomform.checkBox.isChecked()+\
                natsort.natsorted(glob.glob(datdir+'/'+'*'+self.det_roi+'.txt'))*(not self.bottomform.checkBox.isChecked())
        #print (tppdata)
ppdata = []

if os.path.isfile(datdir+'/'+'init.yaml'):
    self.dct = yaml.load(open(datdir+'/'+'init.yaml'))
else:
    self.dct = yaml.load(open('init.yaml'))


if len(tppdata) and len(tppdata) != len(self.datasets):
    if self.datasets and not self.plotAll.getImage(legend='ppXAS'):
        ut = self.plotAll.getImage(legend='ppXAS').getData()
        for i in range(len(tppdata[:1])):
            if not tppdata[i] in self.datasets:
                self.datasets.append(tppdata)
    else:
        ut = []
        self.datasets = []
        self.Energy = []
        ppdata = tppdata

    for i in range(len(ppdata)):
        datf = ppdata[i]
        f = open(datf)
        #tut_off = []
        #tut_on =[]
        #tut_off_cam = []
        k = 0
        for l in f:
            tarray = [x for x in l.rstrip().split(' ') if x!='']
            if not self.datasets:
                if i ==0:
                    ut.append(np.array([float(x) for x in tarray[1:-6]]))
                    self.Energy.append(float(tarray[0]))
                else:
                    ut[k] += np.array([float(x) for x in tarray[1:-6]])
                    k+=1
            else:
                ut[k] += np.array([float(x) for x in tarray[1:-6]])
                k+=1
        f.close()

        self.plotAll.addImage(np.transpose(ut),legend='ppXAS')

    if self.dct:
        ut_ng = []
        ut_ng_each = []
        ns_neg = self.dct['Areas']['preTime0'][0]
        ne_neg = self.dct['Areas']['preTime0'][1]
        for j in range(len(ut)):
            ut_ng.append(np.average(ut[j][ns_neg:ne_neg]))
            ut_ng_each.append(np.array(ut[j][ns_neg:ne_neg]))

        ut_err_ = np.std(np.transpose(ut_ng_each),axis=0)
        print (ut_err_)

        i = 0
        for x in self.dct['Areas'].keys():
            if x != 'preTime0':
                ut_ = []
                ns = self.dct['Areas'][x][0]
                ne = self.dct['Areas'][x][1]
                for j in range(len(ut)):
                    ut_.append(np.average(ut[j][ns:ne]))
                self.plotXAS.addCurve(self.Energy,ut_,legend=x,color=colours_XAS[i%6])
            elif x == 'preTime0':
                self.plotXAS.addCurve(self.Energy,ut_ng,legend=x,color=colours_XAS[i%6])
            i += 1
        if self.dct['Plots']['difference'] == 'yes':
            (ut_negx, ut_neg_y, ut_neg_errx, ut_neg_erry) = self.plotXAS.getCurve(legend=self.dct['Plots']['NEG']).getData()
            j = 0
            for x in self.dct['Areas'].keys():
                if x == self.dct['Plots']['NEG']:
                    pass
                else:
                    ns = self.dct['Areas'][x][0]
                    ne = self.dct['Areas'][x][1]
                    (ut_x, ut_y, ut_errx, ut_erry) = self.plotXAS.getCurve(legend=x).getData()
                    ut_err_diff = np.sqrt(ut_err_**2/abs(ne-ns) + ut_err_**2/abs(ne_neg-ns_neg))
                    self.plotXAS.addCurve(ut_x,ut_y-ut_neg_y,yaxis='right',legend='diff: '+x,
                                          yerror=ut_err_diff,color=colours_diff[j%6])
                    j += 1
