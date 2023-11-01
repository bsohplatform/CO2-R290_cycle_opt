import sys
sys.path.append('D:\\01_Projects\\2021년 스마트플랫폼과제\\1단계\\STED_source\\Level 2')
from VCHP_layout import VCHP
from HP_dataclass import ProcessFluid, Settings
import CoolProp.CoolProp as CP
import joblib

def Cycle_calculation(CO2_dict): 
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
            CO2_dict["OutCond"].m = 0.0
            CO2_dict["InCond"].m = 0.0
    
    CO2_dict["InCond_REF"] = InCond_REF_co2
    CO2_dict["OutCond_REF"] = OutCond_REF_co2
    CO2_dict["InEvap_REF"] = InEvap_REF_co2
    CO2_dict["OutEvap_REF"] = OutEvap_REF_co2
    CO2_dict["outputs"] = outputs_co2
    CO2_dict["method"] = vchp_co2
    
    return CO2_dict

inputs_co2 = Settings()
inputs_co2.second = 'process'
inputs_co2.cycle = 'scc'
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

inputs_co2.DSH = 2.5
inputs_co2.DSC = 10.0
inputs_co2.Y = {"CO2":1.0}
co2_comp = joblib.load('co2_comp.pkl')

InCond_co2 = ProcessFluid(Y={'water':1.0}, m=0.0, T=40.0+273.15, p=101300)
OutCond_co2 = ProcessFluid(Y={'water':1.0}, m=0.0, T=45.0+273.15, p=101300)
InEvap_co2 = ProcessFluid(Y={'air':1.0}, m=1.969, T=7.0+273.15, p=101300)
OutEvap_co2 = ProcessFluid(Y={'air':1.0}, m=1.969, T=5.0+273.15, p=101300)

CO2_dict = {"inputs":inputs_co2, "InCond":InCond_co2, "OutCond":OutCond_co2, "InEvap":InEvap_co2, "OutEvap":OutEvap_co2, "comp":co2_comp}

DSC_lb = 20.0
DSC_ub = 60.0
df = 0.001
a = 1
result_array = []
dsc_array= [] 

while a:
    DSC_avg = 0.5*(DSC_lb+DSC_ub)
    for i in range(2):
        CO2_dict["InCond"].m = 0.0
        CO2_dict["OutCond"].m = 0.0
        
        if i == 0:
            DSC = DSC_avg*(1-df)
        else:
            DSC = DSC_avg*(1+df)
        
        CO2_dict["inputs"].DSC = DSC
        CO2_dict = Cycle_calculation(CO2_dict)
        
        if i == 0:
            COP_0 = CO2_dict["outputs"].COP_heating
        else:
            COP_1 = CO2_dict["outputs"].COP_heating
            dCOP = COP_1 - COP_0
            
            if dCOP < 0:
                DSC_ub = DSC
            else:
                DSC_lb = DSC
                
            result_array.append(0.5*(COP_0+COP_1))
            dsc_array.append(DSC)
            
            if len(result_array) > 2:
                if result_array[-2] > result_array[-1] and result_array[-2] > result_array[-3]:
                    a = 0
                    
            if DSC_ub - DSC_lb < 1.0e-3:
                a = 0

CO2_dict["method"].Post_Processing(CO2_dict["outputs"])

co2_standard = CO2_dict["outputs"].COP_heating

amb_Temp = [-15+273.15, -7+273.15, 2+273.15]
scop_array = []

CO2_dict["inputs"].DSC = dsc_array[-2]
CO2_dict["InCond"].m = InCond_co2.m
CO2_dict["OutCond"].m = OutCond_co2.m

for amb_t in amb_Temp:
    CO2_dict["InCond"].T = 0.0
    CO2_dict['InEvap'].T = amb_t
    CO2_dict['OutEvap'].T = amb_t - 2.0
    
    CO2_dict = {"inputs":inputs_co2, "InCond":InCond_co2, "OutCond":OutCond_co2, "InEvap":InEvap_co2, "OutEvap":OutEvap_co2, "comp":co2_comp}
    (CO2_dict) = Cycle_calculation(CO2_dict)
    CO2_dict["method"].Post_Processing(CO2_dict["outputs"])
    
    scop_array.append(CO2_dict["outputs"].COP_heating)

scop_array.append(co2_standard)
scop = scop_array[0]*0.07+scop_array[1]*0.39+scop_array[2]*0.39+scop_array[3]*0.15
print("SCOP: %.2f" %scop)
