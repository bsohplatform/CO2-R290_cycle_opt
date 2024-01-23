import sys
sys.path.append('D:\\01_Projects\\2021년 스마트플랫폼과제\\1단계\\STED_source\\Level 2')
from VCHP_layout import VCHP
from HP_dataclass import ProcessFluid, Settings
import CoolProp.CoolProp as CP
import joblib

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
        co2_comp_eff_2 = CO2_dict["comp"].predict([[CO2_dict["inputs"].DSH, OutEvap_REF_co2.p, InCond_REF_co2.p]])
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
        r290_comp_eff_2 = R290_dict["comp"].predict([[R290_dict["inputs"].DSH, OutEvap_REF_r290.p, InCond_REF_r290.p]])
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
inputs_co2.cond_N_row = 5
inputs_co2.cond_N_element = 20
inputs_co2.cond_T_pp = 1.0
inputs_co2.cond_dp = 0.01

inputs_co2.evap_type = 'fthe'
inputs_co2.evap_N_row = 1
inputs_co2.evap_N_element = 10
inputs_co2.evap_N_turn = 10
inputs_co2.evap_T_lm = 5.0
inputs_co2.evap_dp = 0.01

inputs_co2.Y = {"CO2":1.0}
co2_comp = joblib.load('co2_comp.pkl')


inputs_r290 = Settings()
inputs_r290.second = 'process'
inputs_r290.cycle = 'vcc'
inputs_r290.layout = 'bas'

inputs_r290.cond_type = 'phe'
inputs_r290.cond_N_row = 5
inputs_r290.cond_N_element = 20
inputs_r290.cond_T_pp = 1.0
inputs_r290.cond_dp = 0.01

inputs_r290.evap_type = 'phe'
inputs_r290.evap_N_row = 5
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


(CO2_dict, R290_dict) = Cycle_calculation(3.05, 1.0, 1.00, 1.0, 285.0, CO2_dict, R290_dict)
tot_COP = R290_dict["OutCond"].q/(CO2_dict["outputs"].Wcomp+R290_dict["outputs"].Wcomp)
        
CO2_dict["method"].Post_Processing(CO2_dict["outputs"])
R290_dict["method"].Post_Processing(R290_dict["outputs"])
print("총괄 COP:%.2f" %tot_COP)

