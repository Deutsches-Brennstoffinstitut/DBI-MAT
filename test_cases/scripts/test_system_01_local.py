import sys
sys.path.append('..\\..\\')  # back to main folder

from dbimat.source.model_base.ModelBase import *
from dbimat.source.helper.initialize_logger import LoggingLevels

from test_cases.systems.Test_1_Basic_Production_H2 import Model_Test_1

my_system_model = Model_Test_1(database_name='dbi_mat', db_location='local', logging_level=LoggingLevels.CRITICAL)

def test_Ely_load_01():
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
    #my_system_model.calculate_costs()
    model_results = my_system_model.create_results()

    df_tech_results2 = model_results.port_results[0].to_dataframe()

    assert df_tech_results2['B00', 'C02', 'P00', 'stream'][0] == -1, 'Grid did not get surplus power'
    assert df_tech_results2['B00', 'C03', 'P00', 'stream'][0] == 0, 'Electrolyzer running below minimal load'


def test_Ely_load_02():
    ''' Electrolyzer should run at maximal load'''

    my_system_model.add_stream_profile_to_port(component_name='RE_Wind',
                                               port_stream_type=StreamEnergy.ELECTRIC,
                                               port_stream_direction=StreamDirection.stream_out_of_component,
                                               profile=np.array([150.0]),
                                               unit=Unit.kW)  # modify the model
    my_system_model.components['RE_Wind'].set_size(size=150)  # kW peak
    my_system_model.components['Ely'].set_size(size=100)  # kW peak # more power than can be used

    my_system_model.run()
   # my_system_model.calculate_costs()
    model_results = my_system_model.create_results()
    df_tech_results2 = model_results.port_results[0].to_dataframe()

    assert df_tech_results2['B00', 'C02', 'P00', 'stream'][0] == -50, 'Grid did not get the right surplus power'
    assert df_tech_results2['B00', 'C03', 'P00', 'stream'][0] == -100, 'Electrolyzer running at wrong load'


def test_Ely_load_03():
    ''' Electrolyzer should run at minimal load'''
    my_system_model.add_stream_profile_to_port(component_name='RE_Wind',
                                      port_stream_type=StreamEnergy.ELECTRIC,
                                      port_stream_direction=StreamDirection.stream_out_of_component,
                                      profile=np.array([50.0]),
                                      unit=Unit.kW)  # modify the model
    my_system_model.components['RE_Wind'].set_size(size=50)  # kW peak
    my_system_model.components['Ely'].set_size(size=1000)  # kW peak # more power than can be used

    my_system_model.run()
    #my_system_model.calculate_costs()
    model_results = my_system_model.create_results()
    df_tech_results2 = model_results.port_results[0].to_dataframe()

    assert df_tech_results2['B00', 'C02', 'P00', 'stream'][0] == 0, 'Grid did get surplus power'
    assert df_tech_results2['B00', 'C03', 'P00', 'stream'][0] == -50, 'Electrolyzer running at wrong load'


def test_loop_annuity_01():
    '''
    cost calculation results should not change between runs
    '''

    my_system_model.run()
    my_system_model.calculate_costs()
    my_model_results = my_system_model.system_results
    df_econ_main = my_model_results.component_economic_results[0].to_dataframe()
    Ely_annuity1 = df_econ_main['B01', 'C03']['component_Annuity']
    assert Ely_annuity1 != 0, "Annuität NULL"

    my_system_model.run()
    my_system_model.calculate_costs()
    my_model_results = my_system_model.system_results
    df_econ_main = my_model_results.component_economic_results[0].to_dataframe()
    Ely_annuity2 = df_econ_main['B01', 'C03']['component_Annuity']
    assert Ely_annuity1 == Ely_annuity2, 'Annuity changed between runs'
