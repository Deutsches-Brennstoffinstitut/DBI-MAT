#  imports
from dbimat.source.modules.GenericUnit import GenericUnit
from dbimat.source.helper._FunctionDef import range_limit
from dbimat.source.basic.Streamtypes import StreamDirection
from dbimat.source.model_base.Dataclasses.TechnicalDataclasses import GenericTechnicalInput


class Burner(GenericUnit):

    def __init__(self, size=None, technology=None, stream_type='METHANE', active=False, efficiency=1.0, fuel_type='CH4',
                 heating_value_fuel=None, new_investment=False, investment_costs=0,
                 generic_technical_input: GenericTechnicalInput = None):
        """
        :param size:         installed nominal Power, should be in kW
        :param technology:   type of installation
        :param controlled_medium: select the controlling port {'electric', fuel_type}
        :param active:       define whether the component controls the system
        :param efficiency:   net efficiency for the charge and discharge process
        :param fuel_type:    define the fuel of the burner (=fuel port type)
        :param heating_value_fuel: set the heating value of the fuel. Leave None for listed fuels; Choose higher or lower heating value according to the given efficiency!!!
        """
        super().__init__(size=size, technology=technology, stream_type=stream_type, active=active,
                         new_investment=new_investment,
                         investment_costs=investment_costs,
                         generic_technical_input=generic_technical_input)  # initialize class generic unit
        # set class specific variables
        self.fuel_type = str(fuel_type)
        if heating_value_fuel is not None:
            self.heating_value = heating_value_fuel
        elif self.fuel_type == 'H2':
            self.heating_value = const.higher_heating_value['H2']
        elif self.fuel_type == 'methane':
            self.heating_value = const.higher_heating_value['methane']

        super()._add_port(self.fuel_type, True)  # [kg/h], input
        super()._add_port('heat', True)  # [kW],   output
        super()._add_port('CO2', True)  # [kg/h], output
        if not active:
            super()._set_adaptive_port(self.controlled_medium)

    def run(self, inputs={}, runcount=0):
        """
        runs the module,
        sets values of output and dependend input ports
        :param inputs: dictionary for input parameters (e.g. size of control port input)
        :param runcount: Step Index, runtime = runcount * resolution
        """

        self.status = 0  # set default status with 0:ok; >0:warning; <0:error

        # check if control strategy is temporarily changed
        [controlled_medium, inputs, loop_control] = self._calc_control_var(inputs)

        # --- alternative port calculation without switch routine ---
        # check incoming port
        if inputs[controlled_medium] is None:
            raise ValueError(f'ERROR Electrolyser: None value at controlled_medium port {controlled_medium} received!')

        # calculate controlled_medium port
        if self.active & (not loop_control):
            if self.profile is None:
                self.ports[controlled_medium] = 0 if self.size is None else self.size
            else:
                self.ports[controlled_medium] = self.profile[runcount]
        else:
            self.ports[controlled_medium] = inputs[controlled_medium] if self.size is None else range_limit(
                inputs[controlled_medium], 0, self.size)

        if controlled_medium == 'heat':
            powerApplied = self.ports['heat']
        else:
            powerApplied = self.ports[controlled_medium] * self.efficiency * self.heating_value

        self.ports['heat'] = powerApplied
        self.ports[self.fuel_type] = powerApplied / self.efficiency / self.heating_value

    #############################
    # Module specific functions #
    #############################


if __name__ == '__main__':
    print('T E S T: burner')
    # import time

    # start = time.time()
    # with open('..\\..\\..\\Input_data\\BaseLib.pickle', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    #    BaseLib = pickle.load(f)
    # end = time.time()
    # print(f"Total runtime of pickle-load is {end - start}")
    ## testing:
    # tmp_list = BaseLib['Profile']['EnergySupply']['RegionalPV']  # why is this so slow?
    # tmp_array = np.array(tmp_list).T  # convert to numpy array and transpose
    # my_profile = tmp_array[0]  # first column

    My_Plant = Burner(size=2000, efficiency=0.5)
    My_Plant._set_adaptive_port('METHANE')
    My_Plant.run({'METHANE': 1})
    print(f'Burner controlled by {My_Plant.controlled_medium}; resulting ports={My_Plant.ports}')
    My_Plant._set_adaptive_port('heat')
    My_Plant.run({'heat': 1})
    print(f'Burner controlled by {My_Plant.controlled_medium,}; resulting ports={My_Plant.ports}')

    try:
        My_Plant._set_adaptive_port('heaat')
        print('wrong controlled_medium port: has been accepted')
    except:
        print('test failed successfully')

    # Cost calculation test
    # capex calculation
    print(My_Plant.get_infostring())
