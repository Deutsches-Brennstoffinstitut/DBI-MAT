################################################
# Test 1 - Basic_Production_H2                 #
################################################

from dbimat.source.model_base.ModelBase import *

class Model_Test_1(ModelBase):

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
            ports[name] = {'electric':0, 'H2':0} - transcript the components ports to the model
        """

        name = 'RE_Wind'
        self.components[name] = Source(stream_type=StreamEnergy.ELECTRIC,
                                       size=50,
                                       technology=Source.Technology.WIND_ONSHORE,
                                       active=True,
                                       )

        # Energie Dump:
        name = "dump_el"
        self.components[name] = Consumer(size=100,
                                         stream_type=StreamEnergy.ELECTRIC,
                                         active=False)
        name = 'Ely'
        self.components[name] = Electrolyser(size=50,
                                             active=False,
                                             technology=Electrolyser.Technology.PEM,
                                             economical_parameters=EconomicalParameters(
                                                 use_database_values=True)
                                             )

        name = 'Consumer_H2'
        self.components[name] = Consumer(stream_type=StreamMass.HYDROGEN)

        branch_name = 'power_el'
        self.add_branch(branch_name, branch_type=StreamEnergy.ELECTRIC,
                        port_connections=[('Ely', StreamDirection.stream_into_component),
                                          ('RE_Wind', StreamDirection.stream_out_of_component),
                                          ('dump_el', StreamDirection.stream_into_component)])

        branch_name = 'H2'
        self.add_branch(branch_name, branch_type=StreamMass.HYDROGEN,
                        port_connections=[('Ely', StreamDirection.stream_out_of_component),
                                          ('Consumer_H2', StreamDirection.stream_into_component)])

        self.loop_control_rules.update({'Stromnetz': ['dump_el'],
                                        'H2': ['Ely']
                                        })

        self.set_time_resolution(60)
        self.add_stream_profile_to_port(component_name='RE_Wind',
                                        port_stream_type=StreamEnergy.ELECTRIC,
                                        port_stream_direction=StreamDirection.stream_out_of_component,
                                        profile=[10] * 8760)
        self.profile_len = 8760

        # --- do automated declaration processing ---
        self.init_structure()  # init names, ports, branches


def run_local(logging_level: LoggingLevels):
    my_system_model = Model_Test_1(database_name='dbi_mat', db_location='local', logging_level=logging_level)
    ## reset Branch and Component ID#s
    #ModelBase.reset_IDs()
    #del my_system_model
    my_system_model = Model_Test_1(database_name='dbi_mat', db_location='local', logging_level=logging_level)

    my_system_model.run()
    my_system_model.calculate_costs()
    my_model_results = my_system_model.system_results
    df_econ_main = my_model_results.component_economic_results[0].to_dataframe()
    df_branch_info = my_model_results.branch_information.to_dataframe()

    Ely_annuity1 = df_econ_main['B01', 'C03']['component_Annuity']
    annuities1 = my_system_model.system_results.get_annuity_of_all_components()

    my_system_model.run()
    my_system_model.calculate_costs()
    my_model_results = my_system_model.system_results

    df_econ_main = my_model_results.component_economic_results[0].to_dataframe()
    Ely_annuity2 = df_econ_main['B01', 'C03']['component_Annuity']
    annuities2 = my_system_model.system_results.get_annuity_of_all_components()

    assert annuities1['C03'] == annuities2['C03'], 'Annuity changed between runs'
    assert Ely_annuity1 == Ely_annuity2, 'Annuity changed between runs'

    print('done')

def run_4_testing(logging_level: LoggingLevels):
    my_system_model = Model_Test_1(database_name='dbi_mat', db_location='local', logging_level=logging_level)
    ## reset Branch and Component ID#s
    # ModelBase.reset_IDs()
    # del my_system_model
    my_system_model = Model_Test_1(database_name='dbi_mat', db_location='local', logging_level=logging_level)

    ''' Electrolyzer should not run when less than minimal power is available'''
    ## set profiles to components
    my_system_model.add_stream_profile_to_port(component_name='RE_Wind',
                                               port_stream_type=StreamEnergy.ELECTRIC,
                                               port_stream_direction=StreamDirection.stream_out_of_component,
                                               profile=np.array([1.0]),
                                               unit=Unit.kW)  # modify the model
    my_system_model.components['RE_Wind'].set_size(size=1)  # kW peak
    my_system_model.components['Ely'].set_size(size=1000)  # kW peak # more power than can be used

    my_system_model.run()
    my_system_model.calculate_costs()
    model_results = my_system_model.create_results()

    ##  here you can find all the relevant profiles and economical results:

    df_basic_econ = model_results.basic_econ_system_settings.to_dataframe()
    df_basic_tech = model_results.basic_technical_settings.to_dataframe()
    df_branch_info = model_results.branch_information.to_dataframe()
    df_tech_results1 = model_results.component_technical_results[0].to_dataframe()
    df_tech_results2 = model_results.port_results[0].to_dataframe()
    df_econ_1 = model_results.component_economic_results[0].to_dataframe()
    df_econ_CAPEX = model_results.component_economic_results[0].to_dataframe_ElementCAPEX()
    df_econ_fixedOPEX = model_results.component_economic_results[0].to_dataframe_ElementfixedOPEX()
    df_econ_variableOPEX = model_results.component_economic_results[0].to_dataframe_ElementvariableOPEX()


    assert df_tech_results2['B00', 'C02', 'P00', 'stream'][0] == -1, 'Grid did not get surplus power'
    assert df_tech_results2['B00', 'C03', 'P00', 'stream'][0] == 0, 'Electrolyzer running below minimal load'

    print('done')

if __name__ == '__main__':
    #run_local(LoggingLevels.CRITICAL)
    run_4_testing(LoggingLevels.WARNING)