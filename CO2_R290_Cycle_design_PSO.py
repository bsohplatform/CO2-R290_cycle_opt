import sys
sys.path.append('D:\\01_Projects\\2021년 스마트플랫폼과제\\1단계\\STED_source\\Level 2')
from VCHP_layout import VCHP
from HP_dataclass import ProcessFluid, Settings
import CoolProp.CoolProp as CP
import joblib
import random as rd
import numpy as np

def Cycle_calculation(DSH_CO2, DSC_CO2, DSH_R290, DSC_R290, T_tes, CO2_dict, R290_dict): 
    CO2_dict["inputs"].DSH = DSH_CO2
    CO2_dict["inputs"].DSC = DSC_CO2
    R290_dict["inputs"].DSH = DSH_R290
    R290_dict["inputs"].DSC = DSC_R290
    CO2_dict["InCond"].T = T_tes
    CO2_dict["OutCond"].T = T_tes+1
    Q_cond_co2 = CO2_dict["InCond"].m*(CP.PropsSI("H","T",CO2_dict["OutCond"].T,"P",CO2_dict["OutCond"].p,"water") - CP.PropsSI("H","T",CO2_dict["InCond"].T,"P",CO2_dict["InCond"].p,"water"))

    co2_comp_eff_1 = 0.7
    while 1:
        CO2_dict["inputs"].comp_eff = co2_comp_eff_1
        vchp_co2 = VCHP(CO2_dict["InCond"], CO2_dict["OutCond"], CO2_dict["InEvap"], CO2_dict["OutEvap"], CO2_dict["inputs"])
        (CO2_dict["InCond"], CO2_dict["OutCond"], CO2_dict["InEvap"], CO2_dict["OutEvap"], InCond_REF_co2, OutCond_REF_co2, InEvap_REF_co2, OutEvap_REF_co2, outputs_co2) = vchp_co2()
        co2_comp_eff_2 = CO2_dict["comp"].predict([[CO2_dict["inputs"].DSC, OutEvap_REF_co2.p, InCond_REF_co2.p]])
        co2_comp_eff_2 = float(co2_comp_eff_2)
        if abs(co2_comp_eff_1 - co2_comp_eff_2)/co2_comp_eff_2 < 1.0e-6:
            break
        else:
            co2_comp_eff_1 = co2_comp_eff_2
            CO2_dict["InEvap"].m = 0.0
            CO2_dict["OutEvap"].m = 0.0
    
    CO2_dict["InCond_REF"] = InCond_REF_co2
    CO2_dict["OutCond_REF"] = OutCond_REF_co2
    CO2_dict["InEvap_REF"] = InEvap_REF_co2
    CO2_dict["OutEvap_REF"] = OutEvap_REF_co2
    CO2_dict["outputs"] = outputs_co2
    CO2_dict["method"] = vchp_co2
    
    m_r290 = Q_cond_co2/(CP.PropsSI("H","T",T_tes,"P",101300,"water") - CP.PropsSI("H","T",T_tes-1,"P",101300,"water"))
    R290_dict["InEvap"].m = m_r290
    R290_dict["InEvap"].T = T_tes
    R290_dict["OutEvap"].m = m_r290
    R290_dict["OutEvap"].T = T_tes-1

    r290_comp_eff_1 = 0.7
    while 1:
        R290_dict["inputs"].comp_eff = r290_comp_eff_1
        vchp_r290 = VCHP(R290_dict["InCond"], R290_dict["OutCond"], R290_dict["InEvap"], R290_dict["OutEvap"], R290_dict["inputs"])
        (R290_dict["InCond"], R290_dict["OutCond"], R290_dict["InEvap"], R290_dict["OutEvap"], InCond_REF_r290, OutCond_REF_r290, InEvap_REF_r290, OutEvap_REF_r290, outputs_r290) = vchp_r290()
        r290_comp_eff_2 = R290_dict["comp"].predict([[R290_dict["inputs"].DSC, OutEvap_REF_r290.p, InCond_REF_r290.p]])
        r290_comp_eff_2 = float(r290_comp_eff_2)
        if abs(r290_comp_eff_1 - r290_comp_eff_2)/r290_comp_eff_2 < 1.0e-6:
            break
        else:
            r290_comp_eff_1 = r290_comp_eff_2
            R290_dict["InCond"].m = 0.0
            R290_dict["OutCond"].m = 0.0
    
    R290_dict["InCond_REF"] = InCond_REF_r290
    R290_dict["OutCond_REF"] = OutCond_REF_r290
    R290_dict["InEvap_REF"] = InEvap_REF_r290
    R290_dict["OutEvap_REF"] = OutEvap_REF_r290
    R290_dict["outputs"] = outputs_r290
    R290_dict["method"] = vchp_r290
    
    return (CO2_dict, R290_dict)

inputs_co2 = Settings()
inputs_co2.second = 'process'
inputs_co2.cycle = 'vcc'
inputs_co2.layout = 'bas'

inputs_co2.cond_type = 'phe'
inputs_co2.cond_N_element = 20
inputs_co2.cond_T_pp = 1.0
inputs_co2.cond_dp = 0.01

inputs_co2.evap_type = 'fthe'
inputs_co2.evap_N_row = 5
inputs_co2.evap_N_element = 20
inputs_co2.evap_T_lm = 5.0
inputs_co2.evap_dp = 0.01

inputs_co2.Y = {"CO2":1.0}
co2_comp = joblib.load('co2_comp.pkl')


inputs_r290 = Settings()
inputs_r290.second = 'process'
inputs_r290.cycle = 'vcc'
inputs_r290.layout = 'bas'

inputs_r290.cond_type = 'phe'
inputs_r290.cond_N_element = 20
inputs_r290.cond_T_pp = 1.0
inputs_r290.cond_dp = 0.01

inputs_r290.evap_type = 'phe'
inputs_r290.evap_N_element = 20
inputs_r290.evap_T_pp = 1.0
inputs_r290.evap_dp = 0.01

inputs_r290.Y = {"R290":1.0}
r290_comp = joblib.load('r290_comp.pkl')


InCond_co2 = ProcessFluid(Y={'water':1.0}, m=1.0, T=0.0, p=101300)
OutCond_co2 = ProcessFluid(Y={'water':1.0}, m=1.0, T=0.0, p=101300)
InEvap_co2 = ProcessFluid(Y={'air':1.0}, m=0.0, T=7+273.15, p=101300)
OutEvap_co2 = ProcessFluid(Y={'air':1.0}, m=0.0, T=5+273.15, p=101300)

InCond_r290 = ProcessFluid(Y={'water':1.0}, m=0.0, T=40+273.15, p=101300)
OutCond_r290 = ProcessFluid(Y={'water':1.0}, m=0.0, T=45+273.15, p=101300)
InEvap_r290 = ProcessFluid(Y={'water':1.0}, m=0.0, T=0.0, p=101300)
OutEvap_r290 = ProcessFluid(Y={'water':1.0}, m=0.0, T=0.0, p=101300)

CO2_dict = {"inputs":inputs_co2, "InCond":InCond_co2, "OutCond":OutCond_co2, "InEvap":InEvap_co2, "OutEvap":OutEvap_co2, "comp":co2_comp}
R290_dict = {"inputs":inputs_r290, "InCond":InCond_r290, "OutCond":OutCond_r290, "InEvap":InEvap_r290, "OutEvap":OutEvap_r290, "comp":r290_comp}

DSH_co2_ub = 5.0
DSC_co2_ub = 5.0
DSH_r290_ub = 5.0
DSC_r290_ub = 5.0
DSH_co2_lb = 1.0
DSC_co2_lb = 1.0
DSH_r290_lb = 1.0
DSC_r290_lb = 1.0
T_tes_lb = InEvap_co2.T
#T_tes_ub = InCond_r290.T
T_tes_ub = CP.PropsSI("TCRIT","CO2")-1.0

num_time = 20
num_position = 30

DSH_co2 = np.array([rd.randrange(DSH_co2_lb, DSH_co2_ub) for i in range(num_position)])
DSC_co2 = np.array([rd.randrange(DSC_co2_lb, DSC_co2_ub) for i in range(num_position)])
DSH_r290 = np.array([rd.randrange(DSH_r290_lb, DSH_r290_ub) for i in range(num_position)])
DSC_r290 = np.array([rd.randrange(DSC_r290_lb, DSC_r290_ub) for i in range(num_position)])
T_tes = np.array([T_tes_lb+(T_tes_ub-T_tes_lb)*rd.random() for i in range(num_position)])

xx = np.stack((DSH_co2, DSC_co2, DSH_r290, DSH_r290, T_tes), axis = 1)
vv = xx
factor_vec = np.array([2/(DSH_co2_ub-DSH_co2_lb), 2/(DSC_co2_ub-DSC_co2_lb), 2/(DSH_r290_ub-DSH_r290_lb), 2/(DSC_r290_ub-DSC_r290_lb), 2/(T_tes_ub-T_tes_lb)])

w = 1.5*np.repeat(np.reshape(factor_vec,(1,5)),repeats = num_position, axis = 0)
c1 = 3.0*np.repeat(np.reshape(factor_vec,(1,5)),repeats = num_position, axis = 0)
c2 = 4.5*np.repeat(np.reshape(factor_vec,(1,5)),repeats = num_position, axis = 0)


opt_result = []

for tt in range(num_time):
    print("No.%d flight------------------------------------------" %tt)
    fit_array = []
    for dsh_co2, dsc_co2, dsh_r290, dsc_r290, t_tes in xx:
        CO2_dict["InEvap"].m = 0.0
        CO2_dict["OutEvap"].m = 0.0
        R290_dict["InCond"].m = 0.0
        R290_dict["OutCond"].m = 0.0
        
        try:
            (CO2_dict, R290_dict) = Cycle_calculation(dsh_co2, dsc_co2, dsh_r290, dsc_r290, t_tes, CO2_dict, R290_dict)
            tot_COP = R290_dict["OutCond"].q/(CO2_dict["outputs"].Wcomp+R290_dict["outputs"].Wcomp)
        except:
            tot_COP = 0.0
        
        fit_array.append(tot_COP)
            
        print("Particle DSH-co2:%.2f[℃], DSC-co2:%.2f[℃], DSH-r290:%.2f[℃], DSC-r290:%.2f[℃], TES_temp:%.2f[℃], COP:%.2f" %(dsh_co2, dsc_co2, dsh_r290, dsc_r290, t_tes, tot_COP))
    print("Global best: %.2f (gdx:%d)------------------------------------------" %(np.max(fit_array),int(np.argmax(fit_array))))
    opt_result.append(np.max(fit_array))
    
    if tt == 0:
        fit_best = np.array(fit_array)
        gdx = int(np.argmax(fit_best))
        g_pos = np.repeat(np.reshape(xx[gdx][:],(1,5)), repeats = num_position, axis=0)
        vv_new = np.multiply(w, vv)+np.multiply(np.multiply(c2,np.random.rand(num_position, 5)),g_pos-xx)
        i_pos = xx
    else:
        idx = np.where(fit_array > fit_best)
        i_pos[idx,:] = xx[idx,:]
        fit_best = np.maximum(fit_array, fit_best)
        gdx = int(np.argmax(fit_best))
        g_pos = np.repeat(np.reshape(xx[gdx][:],(1,5)), repeats = num_position, axis=0)
        vv_new = np.multiply(w, vv)+np.multiply(np.multiply(c1,np.random.rand(num_position, 5)),i_pos - xx)+np.multiply(np.multiply(c2,np.random.rand(num_position, 5)),g_pos-xx)
    
    
    xx = xx + vv_new
    vv = vv_new
    
    for i in range(num_position):
        xx[i][0] = min(max(DSH_co2_lb, xx[i][0]),DSH_co2_ub)
        xx[i][1] = min(max(DSC_co2_lb, xx[i][1]),DSC_co2_ub)
        xx[i][2] = min(max(DSH_r290_lb, xx[i][2]),DSH_r290_ub)
        xx[i][3] = min(max(DSC_r290_lb, xx[i][3]),DSC_r290_ub)
        xx[i][4] = min(max(T_tes_lb, xx[i][4]),T_tes_ub)
        
import matplotlib.pyplot as plt

plt.plot(np.arange(1,num_time+1)[1:],opt_result[1:])
plt.xlabel("Trial", fontsize=20)
plt.xticks(np.arange(1,num_time+1))
plt.ylabel("Total COP",fontsize=20)
plt.savefig('optimize.png')