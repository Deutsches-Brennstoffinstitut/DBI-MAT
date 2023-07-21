################################################
# FRW 3 - Sektorenkopplung                     #
# -------------------------------------------- #
# Szenario 3 soll eine Energieversorgung mit   #
# Sektorenkopplung bei den Fränkischen Rohr-   #
# werken in Königsberg darstellen.             #
# -------------------------------------------- #
################################################

# import all necessary model information
from dbimat.source.model_base.ModelBase import *
from dbimat.source.helper.polarisation_curve_to_efficiency import ElectrolyserEff


class Model_Test_3b(ModelBase):

    def __init__(self, database_name, db_location, logging_level: LoggingLevels = LoggingLevels.WARNING):
        # init
        super().__init__(database_name, db_location, logging_level)
        self.modeldir = inspect.getfile(self.__class__)

        self.basic_technical_settings = BasicTechnicalSettings(time_resolution=60,
                                                               absolute_model_error=1e-10)

        self.basic_economical_settings = BasicEconomicalSettings(reference_year=2021,
                                                                 start_year=2021,
                                                                 end_year=2030,
                                                                 basic_interest_rate=0.03,
                                                                 estimated_inflation_rate=0
                                                                 )
        # --------------------------
        # --- declare components ---
        # --------------------------
        # insert your code here
        """ description of objects
            name = "any unique text string you like"
            components[name]  = model class     - create instance of class member
            connections[name] = [ a list of tuples of connection, where each tuple consists of a pair of tuples  ]
                                [ ((source definition), (target definition)) ]
                                [ ((name, 'electric'), ('mySource1', 'electric')), ((name, 'H2'), ('mySource2', 'special H2')) ]

            # automatic processing #
            names.append(name)                   - insert object into the list of known objects
            ports[name] = {'electric':0, 'H2':0} - transcript the copmonents ports to the model
        """

        electrical_cost_wind = 0.05

        name = 'Windkraftanlage'
        self.components[name] = Source(active=True,
                                       size=49600,
                                       stream_type=StreamEnergy.ELECTRIC,
                                       economical_parameters=EconomicalParameters(
                                       )
                                       )

        electrical_costs_in_dictionary_for_all_components = {
            'Strombezugspreis': 0.08}

        name = 'Netzbezug'
        self.components[name] = Source(active=False,
                                       size=0,  # 4260.26,
                                       stream_type=StreamEnergy.ELECTRIC,
                                       economical_parameters=EconomicalParameters(
                                           stream_econ=[
                                               StreamEconParameters(
                                                   stream_type=StreamEnergy.ELECTRIC,
                                                   first_payment_year=2023,
                                                   include_inflation=False,
                                                   amount_related_costs=Direction(
                                                       unit=Unit.euro_per_kWh,
                                                       costs_out=electrical_costs_in_dictionary_for_all_components)
                                               )
                                           ]
                                       )
                                       )

        name = 'Netzbezug_BOP'
        self.components[name] = Source(active=False,
                                       size=1000,
                                       stream_type=StreamEnergy.ELECTRIC,
                                       economical_parameters=EconomicalParameters(
                                           stream_econ=[
                                               StreamEconParameters(
                                                   stream_type=StreamEnergy.ELECTRIC,
                                                   first_payment_year=2023,
                                                   include_inflation=False,
                                                   amount_related_costs=Direction(
                                                       unit=Unit.euro_per_kWh,
                                                       costs_out=electrical_costs_in_dictionary_for_all_components
                                                   )
                                               )
                                           ]
                                       )
                                       )

        name = 'Netz'
        self.components[name] = Grid(stream_type=StreamEnergy.ELECTRIC,
                                     economical_parameters=EconomicalParameters(
                                     )
                                     )

        """Pre Processing for getting efficiency charactristic"""
        efficiency_characteristic_base = ElectrolyserEff(upper_currentdensity=0.8,
                                                         lower_currentdensity=0.2,
                                                         upper_voltage=2.2,
                                                         lower_voltage=1.8,
                                                         number_of_stacks=10).result()
        efficiency_characteristic_variable = ElectrolyserEff(upper_currentdensity=2,
                                                             lower_currentdensity=0.4,
                                                             upper_voltage=2,
                                                             lower_voltage=1.65,
                                                             number_of_stacks=10).result()

        name = 'Ely'
        self.components[name] = Electrolyser_Unit(active=True,
                                                  specify_balance_of_plant=Electrolyser_Unit.SpecifyBalanceOfPlant(
                                                      power_consumption_BOP_standby=-800,
                                                      power_consumption_BOP_operating=-1000,
                                                      unit_power=Unit.kW
                                                  ),
                                                  variable_electrolyser=Electrolyser(active=False,
                                                                                     size=10000,
                                                                                     technology=Electrolyser.Technology.PEM,
                                                                                     generic_technical_input=GenericTechnicalInput(
                                                                                         pressures=[
                                                                                             Pressure(
                                                                                                 stream_type_of_port=StreamMass.HYDROGEN,
                                                                                                 stream_direction_of_port=StreamDirection.stream_out_of_component,
                                                                                                 pressure_value=30 * 100000,
                                                                                                 unit=Unit.Pa
                                                                                             )],
                                                                                         temperatures=[
                                                                                             Temperature(
                                                                                                 stream_type_of_port=StreamMass.HYDROGEN,
                                                                                                 stream_direction_of_port=StreamDirection.stream_out_of_component,
                                                                                                 temperature_value=313.15,
                                                                                                 unit=Unit.K
                                                                                             )
                                                                                         ],
                                                                                         efficiencies=[
                                                                                             Efficiency(
                                                                                                 medium_calculated=StreamMass.HYDROGEN,
                                                                                                 medium_referenced=StreamEnergy.ELECTRIC,
                                                                                                 unit_calculated=Unit.kWh,
                                                                                                 unit_referenced=Unit.norm_cubic_meters,
                                                                                                 load_range=efficiency_characteristic_variable.index,
                                                                                                 efficiencies_at_load=
                                                                                                 efficiency_characteristic_variable[
                                                                                                     'stack_efficiency_at_load_of_electrolyser [kg/kWh_el]']
                                                                                             )
                                                                                         ]
                                                                                     ),
                                                                                     ),
                                                  base_electrolyser=Electrolyser(
                                                      technology=Electrolyser.Technology.ALKALY,
                                                      size=20000,
                                                      generic_technical_input=GenericTechnicalInput(
                                                          pressures=[
                                                              Pressure(
                                                                  stream_type_of_port=StreamMass.HYDROGEN,
                                                                  stream_direction_of_port=StreamDirection.stream_out_of_component,
                                                                  pressure_value=30 * 100000,
                                                                  unit=Unit.Pa
                                                              )],
                                                          temperatures=[
                                                              Temperature(
                                                                  stream_type_of_port=StreamMass.HYDROGEN,
                                                                  stream_direction_of_port=StreamDirection.stream_out_of_component,
                                                                  temperature_value=313.15,
                                                                  unit=Unit.K
                                                              )
                                                          ],
                                                          efficiencies=[
                                                              Efficiency(
                                                                  medium_calculated=StreamMass.HYDROGEN,
                                                                  medium_referenced=StreamEnergy.ELECTRIC,
                                                                  unit_calculated=Unit.kWh,
                                                                  unit_referenced=Unit.norm_cubic_meters,
                                                                  load_range=efficiency_characteristic_base.index,
                                                                  efficiencies_at_load=efficiency_characteristic_base[
                                                                      'stack_efficiency_at_load_of_electrolyser [kg/kWh_el]']
                                                              )
                                                          ]
                                                      ),
                                                  ))

        name = 'Storage_H2'
        self.components[name] = Storage_Gas(active=False,
                                            cushion_gas_volume=15e6,
                                            initial_value=2800000,
                                            stream_type=StreamMass.HYDROGEN,
                                            technology=Storage_Gas.Technology.CAVERN,
                                            pressure_max=14000000,
                                            pressure_min=3000000,
                                            include_compression=True,
                                            new_investment=True,
                                            economical_parameters=EconomicalParameters(
                                                component_capex=([
                                                    CAPEXParameters(
                                                        name='Untertageausrüstung und Kaverne',
                                                        investment_cost=11143982.91,
                                                        reference_year=2027,
                                                        investment_year=2027,
                                                        life_cycle=25,
                                                        interest_rate=0.068
                                                    )
                                                ]
                                                ),
                                                operational_opex=OPEXOperationalParameters(
                                                    opex_in_percentage_per_year=0.02)
                                            ))

        self.components[name].set_sub_component(Compressor(size=1225,
                                                           technology=Compressor.Technology.PISTON,
                                                           stages=2,
                                                           stream_type=StreamMass.HYDROGEN,
                                                           new_investment=True,
                                                           max_stream=-40000 * 0.0899,
                                                           cooling_temperature=313.15,
                                                           ))

        name = 'Pipeline_H2'
        self.components[name] = Pipeline_Segment(technology=Pipeline_Segment.Technology.ONSHORE_UNDERGROUND,
                                                 stream_type=StreamMass.HYDROGEN,
                                                 new_investment=True,
                                                 inner_diameter_in_m=20 * 25.4 / 1000 - 0.016,
                                                 length=25000,
                                                 roughness_in_mm=0.1,
                                                 iterate_heat_flux=False)

        name = 'Consumer_H2'
        self.components[name] = Consumer(active=False,
                                         stream_type=StreamMass.HYDROGEN,
                                         new_investment=False)
        branch_name = 'Electric'
        self.add_branch(branch_name=branch_name, branch_type=StreamEnergy.ELECTRIC,
                        port_connections=[
                            ('Windkraftanlage', StreamDirection.stream_out_of_component),
                            ('Netzbezug', StreamDirection.stream_out_of_component),
                            ('Ely', StreamDirection.stream_into_component,
                             Electrolyser_Unit.PortIdentifiers.MainElectricInput),
                            ('Netz', StreamDirection.stream_bidirectional)])

        branch_name = 'Electric_BOP'
        self.add_branch(branch_name=branch_name, branch_type=StreamEnergy.ELECTRIC,
                        port_connections=[
                            ('Ely', StreamDirection.stream_into_component, Electrolyser_Unit.PortIdentifiers.BOP),
                            ('Netzbezug_BOP', StreamDirection.stream_out_of_component)])

        branch_name = 'H2_2'
        self.add_branch(branch_name=branch_name, branch_type=StreamMass.HYDROGEN, port_connections=[
            ('Ely', StreamDirection.stream_out_of_component),
            ('Pipeline_H2', StreamDirection.stream_into_component),
            ('Storage_H2', StreamDirection.stream_into_component),
            ('Storage_H2', StreamDirection.stream_out_of_component)
        ])

        branch_name = 'H2_3'
        self.add_branch(branch_name=branch_name, branch_type=StreamMass.HYDROGEN, port_connections=[
            ('Pipeline_H2', StreamDirection.stream_out_of_component),
            ('Consumer_H2', StreamDirection.stream_into_component)
        ])

        # define operation rules
        self.passive_priorityRules.extend(['Pipeline_H2', 'Storage_H2'])

        self.loop_control_rules.update({'Electric': ['Ely', 'Netzbezug'],
                                        'H2_3': ['Pipeline_H2']
                                        })

        # --- Add profiles -------

        # Auslastung = np.linspace(0,100,101)
        Last = list(np.linspace(0, 30000, 101))
        # Daten = np.zeros((101, 2))
        # Daten[:,0] = Auslastung
        # Daten[:,1] = Last
        # profile_ramp =  pd.DataFrame(data = Daten, columns=['Stunde','Last'])

        wind_profile = Last

        self.add_stream_profile_to_port(component_name='Windkraftanlage',
                                        port_stream_type=StreamEnergy.ELECTRIC,
                                        port_stream_direction=StreamDirection.stream_out_of_component,
                                        profile=wind_profile, unit=Unit.kW, time_resolution=60)
        self.add_binary_stream_profile_to_port(component_name='Ely',
                                               port_stream_type=StreamEnergy.ELECTRIC,
                                               port_stream_direction=StreamDirection.stream_into_component,
                                               profile=[1] * len(wind_profile), time_resolution=60, active=True)
        self.add_binary_stream_profile_to_port(component_name='Netz',
                                               port_stream_type=StreamEnergy.ELECTRIC,
                                               port_stream_direction=StreamDirection.stream_out_of_component,
                                               profile=[0] * len(wind_profile),
                                               time_resolution=60,
                                               active=True)
        # self.add_stream_profile_to_port(component_name='Consumer_H2',
        #                                port_stream_type=StreamMass.HYDROGEN,
        #                                port_stream_direction=StreamDirection.stream_into_component,
        #                                profile=[0] * 8760,  # list(profiles['Abnahme [kg/step]']),
        #                                active=True)

        # --- do automated declaration processing ---
        self.init_structure()  # init names, ports, branches

    def report(self):
        for name in list(self.components.keys()):
            logging.info('ports of ' + name + ': {}'.format(self.ports[name]))


def run_local(logging_level: LoggingLevels):
    my_system_model = Model_Test_3b(database_name='dbi_mat', db_location='local', logging_level=logging_level)
    my_system_model.run()
    my_system_model.calculate_costs()

if __name__ == '__main__':
    run_local(LoggingLevels.CRITICAL)
